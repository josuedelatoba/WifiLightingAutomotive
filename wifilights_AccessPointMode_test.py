import network
import socket
import time
from machine import Pin

AP_SSID = 'ESP32_CARRO'
AP_PASSWORD = '12345678'

ap = network.WLAN(network.AP_IF)
ap.active(False)
time.sleep(1)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD)
time.sleep(2)

ip = ap.ifconfig()[0]
print('Red WiFi creada:', AP_SSID)
print('Password:', AP_PASSWORD)
print('IP:', ip)

PIN_DRL = 19
PIN_LOW = 18
PIN_HIGH = 5
PIN_TL = 17
PIN_TR = 16

PIN_TAIL = 22
PIN_BRAKE = 23
PIN_REVERSE = 27

PIN_CABIN = 4
PIN_TRUNK_LIGHT = 21

PIN_DOOR_L = 32
PIN_DOOR_R = 33
PIN_TRUNK_SW = 25

drl = Pin(PIN_DRL, Pin.OUT, value=0)
low = Pin(PIN_LOW, Pin.OUT, value=0)
high = Pin(PIN_HIGH, Pin.OUT, value=0)
tl = Pin(PIN_TL, Pin.OUT, value=0)
tr = Pin(PIN_TR, Pin.OUT, value=0)

tail = Pin(PIN_TAIL, Pin.OUT, value=0)
brake = Pin(PIN_BRAKE, Pin.OUT, value=0)
reverse = Pin(PIN_REVERSE, Pin.OUT, value=0)

cabin_light = Pin(PIN_CABIN, Pin.OUT, value=0)
trunk_light = Pin(PIN_TRUNK_LIGHT, Pin.OUT, value=0)

door_left = Pin(PIN_DOOR_L, Pin.IN, Pin.PULL_UP)
door_right = Pin(PIN_DOOR_R, Pin.IN, Pin.PULL_UP)
trunk_switch = Pin(PIN_TRUNK_SW, Pin.IN, Pin.PULL_UP)

state = {
    "drl": 0,
    "low": 0,
    "high": 0,
    "left": 0,
    "right": 0,
    "hazard": 0,
    "brake": 0,
    "reverse": 0,
    "cabin_mode": 0
}

blink_on = False
last_blink_ms = time.ticks_ms()
BLINK_PERIOD_MS = 500

def doors_open():
    return (door_left.value() == 0) or (door_right.value() == 0)

def trunk_open():
    return trunk_switch.value() == 0

def apply_headlights_logic():
    drl_out = state["drl"]
    low_out = state["low"]
    high_out = state["high"]

    if high_out == 1:
        low_out = 1

    if low_out == 1 or high_out == 1:
        drl_out = 0

    tail_out = 1 if (low_out == 1 or high_out == 1) else 0

    drl.value(drl_out)
    low.value(low_out)
    high.value(high_out)
    tail.value(tail_out)

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

def update_aux_lights():
    brake.value(state["brake"])
    reverse.value(state["reverse"])

def update_courtesy_lights():
    if state["cabin_mode"] == 0:
        cabin_light.value(0)
    elif state["cabin_mode"] == 1:
        cabin_light.value(1)
    elif state["cabin_mode"] == 2:
        cabin_light.value(1 if doors_open() else 0)

    trunk_light.value(1 if trunk_open() else 0)

def set_mode(mode, val):
    if mode in ("drl", "low", "high", "brake", "reverse"):
        state[mode] = val
        apply_headlights_logic()
        update_aux_lights()
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

    if mode == "cabin_mode":
        state["cabin_mode"] = val
        return

def status_badge(on):
    return "<span style='padding:3px 8px;border-radius:10px;background:{};color:white;font-size:12px'>{}</span>".format(
        "#2ecc71" if on else "#e74c3c",
        "ON" if on else "OFF"
    )

def sensor_badge(opened):
    return "<span style='padding:3px 8px;border-radius:10px;background:{};color:white;font-size:12px'>{}</span>".format(
        "#f39c12" if opened else "#555",
        "ABIERTA" if opened else "CERRADA"
    )

def mode_badge(mode):
    if mode == 0:
        txt = "OFF"
        color = "#e74c3c"
    elif mode == 1:
        txt = "ON"
        color = "#2ecc71"
    else:
        txt = "AUTO"
        color = "#3498db"

    return "<span style='padding:3px 8px;border-radius:10px;background:{};color:white;font-size:12px'>{}</span>".format(color, txt)

def web_page():
    low_out = state["low"]
    high_out = state["high"]
    drl_out = state["drl"]

    if high_out == 1:
        low_out = 1
    if low_out == 1 or high_out == 1:
        drl_out = 0

    tail_out = 1 if (low_out == 1 or high_out == 1) else 0

    door_l_open = (door_left.value() == 0)
    door_r_open = (door_right.value() == 0)
    trunk_is_open = (trunk_switch.value() == 0)

    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="1">
<title>Control Automotriz</title>
</head>
<body style="font-family:Arial;background:#0b1220;color:#fff;margin:0;padding:16px">
<h2 style="margin:0 0 10px 0">Control de Luces Automotrices</h2>
<p style="margin:0 0 18px 0;color:#b8c1d1">ESP32 IP: {ip}</p>

<div style="background:#111a2e;border-radius:12px;padding:14px;margin-bottom:12px">
  <h3 style="margin:0 0 10px 0;font-size:16px">Luces delanteras</h3>

  <div style="margin:10px 0">
    <b>DRL</b> {drl_s}<br>
    <a href="/?drl=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?drl=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Bajas</b> {low_s}<br>
    <a href="/?low=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?low=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Altas</b> {high_s}<br>
    <a href="/?high=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?high=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>
</div>

<div style="background:#111a2e;border-radius:12px;padding:14px;margin-bottom:12px">
  <h3 style="margin:0 0 10px 0;font-size:16px">Direccionales</h3>

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
    <b>Hazard</b> {haz_s}<br>
    <a href="/?hazard=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?hazard=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>
</div>

<div style="background:#111a2e;border-radius:12px;padding:14px;margin-bottom:12px">
  <h3 style="margin:0 0 10px 0;font-size:16px">Luces traseras</h3>

  <div style="margin:10px 0">
    <b>Traseras nocturnas</b> {tail_s}
  </div>

  <div style="margin:10px 0">
    <b>Freno</b> {brake_s}<br>
    <a href="/?brake=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?brake=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Reversa</b> {reverse_s}<br>
    <a href="/?reverse=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?reverse=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
  </div>
</div>

<div style="background:#111a2e;border-radius:12px;padding:14px;margin-bottom:12px">
  <h3 style="margin:0 0 10px 0;font-size:16px">Cortesía</h3>

  <div style="margin:10px 0">
    <b>Cabina</b> {cabin_mode_s}<br>
    <a href="/?cabin_mode=off"><button style="width:110px;height:34px;margin-top:6px">OFF</button></a>
    <a href="/?cabin_mode=on"><button style="width:110px;height:34px;margin-top:6px">ON</button></a>
    <a href="/?cabin_mode=auto"><button style="width:110px;height:34px;margin-top:6px">AUTO</button></a>
  </div>

  <div style="margin:10px 0">
    <b>Puerta izquierda</b> {door_l_s}
  </div>

  <div style="margin:10px 0">
    <b>Puerta derecha</b> {door_r_s}
  </div>

  <div style="margin:10px 0">
    <b>Cajuela</b> {trunk_s}
  </div>

  <div style="margin:10px 0">
    <b>Luz cabina</b> {cabin_light_s}
  </div>

  <div style="margin:10px 0">
    <b>Luz cajuela</b> {trunk_light_s}
  </div>
</div>

<p style="color:#b8c1d1;font-size:12px">
Nota: Altas enciende también Bajas. Bajas o Altas apagan DRL y encienden las traseras nocturnas. La luz de cajuela siempre depende de su switch.
</p>

</body>
</html>
""".format(
        ip=ip,
        drl_s=status_badge(drl_out),
        low_s=status_badge(low_out),
        high_s=status_badge(high_out),
        left_s=status_badge(state["left"]),
        right_s=status_badge(state["right"]),
        haz_s=status_badge(state["hazard"]),
        tail_s=status_badge(tail_out),
        brake_s=status_badge(state["brake"]),
        reverse_s=status_badge(state["reverse"]),
        cabin_mode_s=mode_badge(state["cabin_mode"]),
        door_l_s=sensor_badge(door_l_open),
        door_r_s=sensor_badge(door_r_open),
        trunk_s=sensor_badge(trunk_is_open),
        cabin_light_s=status_badge(cabin_light.value()),
        trunk_light_s=status_badge(trunk_light.value())
    )
    return html

def parse_request(req):
    try:
        r = req.decode()
    except:
        return None, None

    keys = ["drl", "low", "high", "left", "right", "hazard", "brake", "reverse"]
    for k in keys:
        if ("/?{}=on".format(k)) in r:
            return k, 1
        if ("/?{}=off".format(k)) in r:
            return k, 0

    if "/?cabin_mode=off" in r:
        return "cabin_mode", 0
    if "/?cabin_mode=on" in r:
        return "cabin_mode", 1
    if "/?cabin_mode=auto" in r:
        return "cabin_mode", 2

    return None, None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(3)
s.settimeout(0.2)

print("Servidor listo")
print("Conectate a:", AP_SSID)
print("Abre en tu navegador: http://192.168.4.1")

apply_headlights_logic()
update_aux_lights()
update_courtesy_lights()

while True:
    update_blinking()
    update_courtesy_lights()

    try:
        conn, addr = s.accept()
    except OSError:
        continue

    try:
        req = conn.recv(1024)
        mode, val = parse_request(req)
        if mode is not None:
            set_mode(mode, val)

        apply_headlights_logic()
        update_aux_lights()
        update_courtesy_lights()

        resp = web_page()
        conn.send('HTTP/1.1 200 OK\r\n')
        conn.send('Content-Type: text/html; charset=utf-8\r\n')
        conn.send('Connection: close\r\n\r\n')
        conn.sendall(resp)
    except:
        pass
    finally:
        conn.close()