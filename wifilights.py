import network
import socket
import time
import gc
from machine import Pin

AP_SSID = 'ESP32_CARRO'
AP_PASSWORD = '12345678'

network.WLAN(network.STA_IF).active(False)

ap = network.WLAN(network.AP_IF)
ap.active(False)
time.sleep(1)
ap.active(True)
time.sleep(1)

try:
    ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=3)
except:
    ap.config(essid=AP_SSID)

time.sleep(2)

ip = ap.ifconfig()[0]
print("WiFi:", AP_SSID)
print("IP:", ip)

PIN_DRL = 19
PIN_LOW = 18
PIN_HIGH = 26
PIN_TL = 17
PIN_TR = 16

PIN_TAIL = 13     #
PIN_BRAKE = 14    #
PIN_REVERSE = 27  # movido para no chocar


drl = Pin(PIN_DRL, Pin.OUT, value=0)
low = Pin(PIN_LOW, Pin.OUT, value=0)
high = Pin(PIN_HIGH, Pin.OUT, value=0)

left_signal = Pin(PIN_TL, Pin.OUT, value=0)
right_signal = Pin(PIN_TR, Pin.OUT, value=0)

tail = Pin(PIN_TAIL, Pin.OUT, value=0)
brake = Pin(PIN_BRAKE, Pin.OUT, value=0)
reverse = Pin(PIN_REVERSE, Pin.OUT, value=0)

state = {
    "drl": 0,
    "low": 0,
    "high": 0,
    "left": 0,
    "right": 0,
    "hazard": 0,
    "brake": 0,
    "reverse": 0
}

blink_on = False
last_blink = time.ticks_ms()

def apply_headlights_logic():
    drl_out = state["drl"]
    low_out = state["low"]
    high_out = state["high"]

    if high_out:
        low_out = 1

    if low_out or high_out:
        drl_out = 0

    state["low"] = low_out
    state["drl"] = drl_out

    tail_out = 1 if (low_out or high_out) else 0

    drl.value(drl_out)
    low.value(low_out)
    high.value(high_out)
    tail.value(tail_out)

def update_aux():
    brake.value(state["brake"])
    reverse.value(state["reverse"])

def update_blinking():
    global blink_on, last_blink

    active_left = state["left"]
    active_right = state["right"]
    active_hazard = state["hazard"]

    if not (active_left or active_right or active_hazard):
        left_signal.value(0)
        right_signal.value(0)
        return

    now = time.ticks_ms()

    if time.ticks_diff(now, last_blink) >= 500:
        last_blink = now
        blink_on = not blink_on

        if active_hazard:
            left_signal.value(blink_on)
            right_signal.value(blink_on)
        else:
            left_signal.value(blink_on if active_left else 0)
            right_signal.value(blink_on if active_right else 0)

def set_mode(mode, val):
    if mode in ("drl", "low", "high", "brake", "reverse"):
        state[mode] = val
        apply_headlights_logic()
        update_aux()
        return

    if mode == "left":
        state["left"] = val
        if val:
            state["right"] = 0
            state["hazard"] = 0
        return

    if mode == "right":
        state["right"] = val
        if val:
            state["left"] = 0
            state["hazard"] = 0
        return

    if mode == "hazard":
        state["hazard"] = val
        if val:
            state["left"] = 0
            state["right"] = 0
        return

def status_badge(on):
    color = "#27ae60" if on else "#c0392b"
    text = "ON" if on else "OFF"
    return "<span style='background:{};padding:4px 10px;border-radius:12px;font-size:12px'>{}</span>".format(color, text)

def button(label, url, color):
    return "<a href='{}'><button style='width:105px;height:36px;margin:4px;border:0;border-radius:10px;background:{};color:white;font-weight:bold'>{}</button></a>".format(url, color, label)

def web_page():
    gc.collect()

    low_out = state["low"]
    high_out = state["high"]
    drl_out = state["drl"]

    if high_out:
        low_out = 1

    if low_out or high_out:
        drl_out = 0

    tail_out = 1 if (low_out or high_out) else 0

    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="1">
<title>ESP32 Car Control</title>
</head>

<body style="font-family:Arial;background:#080f1f;color:white;margin:0;padding:16px">

<h2 style="text-align:center;margin-bottom:4px">ESP32 Car Control</h2>
<p style="text-align:center;color:#9aa4b2;margin-top:0">IP: """ + ip + """</p>

<div style="background:#111a2e;border-radius:16px;padding:14px;margin-bottom:14px">
<h3>Luces delanteras</h3>

<p><b>DRL</b> """ + status_badge(drl_out) + """</p>
""" + button("ON", "/?drl=on", "#27ae60") + button("OFF", "/?drl=off", "#c0392b") + """

<p><b>Bajas</b> """ + status_badge(low_out) + """</p>
""" + button("ON", "/?low=on", "#27ae60") + button("OFF", "/?low=off", "#c0392b") + """

<p><b>Altas</b> """ + status_badge(high_out) + """</p>
""" + button("ON", "/?high=on", "#27ae60") + button("OFF", "/?high=off", "#c0392b") + """
</div>

<div style="background:#111a2e;border-radius:16px;padding:14px;margin-bottom:14px">
<h3>Direccionales</h3>

<p><b>Izquierda</b> """ + status_badge(state["left"]) + """</p>
""" + button("ON", "/?left=on", "#f39c12") + button("OFF", "/?left=off", "#c0392b") + """

<p><b>Derecha</b> """ + status_badge(state["right"]) + """</p>
""" + button("ON", "/?right=on", "#f39c12") + button("OFF", "/?right=off", "#c0392b") + """

<p><b>Hazard</b> """ + status_badge(state["hazard"]) + """</p>
""" + button("ON", "/?hazard=on", "#f39c12") + button("OFF", "/?hazard=off", "#c0392b") + """
</div>

<div style="background:#111a2e;border-radius:16px;padding:14px;margin-bottom:14px">
<h3>Luces traseras</h3>

<p><b>Traseras nocturnas</b> """ + status_badge(tail_out) + """</p>

<p><b>Freno</b> """ + status_badge(state["brake"]) + """</p>
""" + button("ON", "/?brake=on", "#e74c3c") + button("OFF", "/?brake=off", "#c0392b") + """

<p><b>Reversa</b> """ + status_badge(state["reverse"]) + """</p>
""" + button("ON", "/?reverse=on", "#3498db") + button("OFF", "/?reverse=off", "#c0392b") + """
</div>

<p style="font-size:12px;color:#9aa4b2;text-align:center">
Altas activan bajas. Bajas/altas apagan DRL y encienden traseras.
</p>

</body>
</html>"""

    return html

def parse(req):
    try:
        r = req.decode()
    except:
        return None, None

    keys = ["drl", "low", "high", "left", "right", "hazard", "brake", "reverse"]

    for k in keys:
        if "/?{}=on".format(k) in r:
            return k, 1

        if "/?{}=off".format(k) in r:
            return k, 0

    return None, None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(3)
s.settimeout(0.2)

print("Servidor listo")
print("Conectate a:", AP_SSID)
print("Abre: http://192.168.4.1")

apply_headlights_logic()
update_aux()

while True:
    update_blinking()

    try:
        conn, addr = s.accept()
    except OSError:
        gc.collect()
        continue

    try:
        req = conn.recv(1024)

        mode, val = parse(req)

        if mode is not None:
            set_mode(mode, val)

        apply_headlights_logic()
        update_aux()

        response = web_page()

        conn.send("HTTP/1.1 200 OK\r\n")
        conn.send("Content-Type: text/html; charset=utf-8\r\n")
        conn.send("Connection: close\r\n\r\n")
        conn.sendall(response)

        gc.collect()

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()
        gc.collect()