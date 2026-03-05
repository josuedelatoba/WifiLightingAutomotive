import network
import socket
import time
from machine import Pin

SSID = 'TU_SSID'
PASSWORD = 'TU_PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    pass

ip = wlan.ifconfig()[0]
print('Conexion WiFi establecida:', SSID)
print('IP:', ip)

PIN_DRL   = 19
PIN_LOW   = 18
PIN_HIGH  = 5
PIN_TL    = 17
PIN_TR    = 16

drl   = Pin(PIN_DRL,  Pin.OUT, value=0)
low   = Pin(PIN_LOW,  Pin.OUT, value=0)
high  = Pin(PIN_HIGH, Pin.OUT, value=0)
tl    = Pin(PIN_TL,   Pin.OUT, value=0)
tr    = Pin(PIN_TR,   Pin.OUT, value=0)

state = {
    "drl": 0,
    "low": 0,
    "high": 0,
    "left": 0,
    "right": 0,
    "hazard": 0
}

blink_on = False
last_blink_ms = time.ticks_ms()
BLINK_PERIOD_MS = 500

def apply_headlights_logic():
    # Lógica automotriz:
    # - Si LOW o HIGH están ON -> DRL OFF
    # - Si HIGH ON -> LOW ON también
    if state["high"] == 1:
        state["low"] = 1
    if state["low"] == 1 or state["high"] == 1:
        state["drl"] = 0

    drl.value(state["drl"])
    low.value(state["low"])
    high.value(state["high"])

def update_blinking():
    global blink_on, last_blink_ms

    active_left = state["left"] == 1
    active_right = state["right"] == 1
    active_hazard = state["hazard"] == 1

    if not (active_left or active_right or active_hazard):
        tl.value(0)
        tr.value(0)
        blink_on = False
        return

    now = time.ticks_ms()
    if time.ticks_diff(now, last_blink_ms) >= BLINK_PERIOD_MS:
        last_blink_ms = now
        blink_on = not blink_on

        if active_hazard:
            tl.value(1 if blink_on else 0)
            tr.value(1 if blink_on else 0)
        else:
            tl.value(1 if (active_left and blink_on) else 0)
            tr.value(1 if (active_right and blink_on) else 0)

def set_mode(mode, val):
    if mode in ("drl", "low", "high"):
        state[mode] = val
        apply_headlights_logic()
        return

    if mode == "left":
        state["left"] = val
        if val == 1:
            state["right"] = 0
            state["hazard"] = 0
        return

    if mode == "right":
        state["right"] = val
        if val == 1:
            state["left"] = 0
            state["hazard"] = 0
        return

    if mode == "hazard":
        state["hazard"] = val
        if val == 1:
            state["left"] = 0
            state["right"] = 0
        return

def status_badge(on):
    return "<span style='padding:3px 8px;border-radius:10px;background:{};color:white;font-size:12px'> {}</span>".format(
        "#2ecc71" if on else "#e74c3c",
        "ON" if on else "OFF"
    )

def web_page():
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Luces Automotrices</title>
</head>
<body style="font-family:Arial;background:#0b1220;color:#fff;margin:0;padding:16px">
<h2 style="margin:0 0 10px 0">Control de Luces Automotrices</h2>
<p style="margin:0 0 18px 0;color:#b8c1d1">ESP32 IP: {ip}</p>

<div style="background:#111a2e;border-radius:12px;padding:14px;margin-bottom:12px">
  <h3 style="margin:0 0 10px 0;font-size:16px">Luces</h3>

  <div style="margin:10px 0">
    <b>Diurnas (DRL)</b> {drl_s}<br>
    <a href="/?drl=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?drl=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Normales (Bajas)</b> {low_s}<br>
    <a href="/?low=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?low=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Altas</b> {high_s}<br>
    <a href="/?high=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?high=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <p style="margin-top:12px;color:#b8c1d1;font-size:12px">
    Nota: Si enciendes Bajas o Altas, DRL se apaga. Si enciendes Altas, Bajas se enciende también.
  </p>
</div>

<div style="background:#111a2e;border-radius:12px;padding:14px;margin-bottom:12px">
  <h3 style="margin:0 0 10px 0;font-size:16px">Intermitentes</h3>

  <div style="margin:10px 0">
    <b>Izquierda</b> {left_s}<br>
    <a href="/?left=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?left=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Derecha</b> {right_s}<br>
    <a href="/?right=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?right=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Warnings</b> {haz_s}<br>
    <a href="/?hazard=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?hazard=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>
</div>

</body>
</html>
""".format(
        ip=ip,
        drl_s=status_badge(state["drl"]),
        low_s=status_badge(state["low"]),
        high_s=status_badge(state["high"]),
        left_s=status_badge(state["left"]),
        right_s=status_badge(state["right"]),
        haz_s=status_badge(state["hazard"])
    )
    return html

def parse_request(req):
    try:
        r = req.decode()
    except:
        return None, None

    keys = ["drl", "low", "high", "left", "right", "hazard"]
    for k in keys:
        if ("/?{}=on".format(k)) in r:
            return k, 1
        if ("/?{}=off".format(k)) in r:
            return k, 0
    return None, None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(3)
s.settimeout(0.2)

print("Servidor listo! Abre: http://{}".format(ip))

apply_headlights_logic()

while True:
    update_blinking()

    try:
        conn, addr = s.accept()
    except OSError:
        continue

    try:
        req = conn.recv(1024)
        mode, val = parse_request(req)
        if mode is not None:
            set_mode(mode, val)

        resp = web_page()
        conn.send('HTTP/1.1 200 OK\r\n')
        conn.send('Content-Type: text/html; charset=utf-8\r\n')
        conn.send('Connection: close\r\n\r\n')
        conn.sendall(resp)
    except:
        pass
    finally:
        conn.close()