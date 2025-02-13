from machine import Pin, SoftI2C, Timer
import time
import network
import urequests
import tm1637
from ds1307 import DS1307
import ubinascii

TOGGL_API_KEY = ""
TOGGL_WORKSPACE_ID = ""
WORK_DURATION = 25 * 60 - 3
BREAK_DURATION = 5 * 60

display = tm1637.TM1637(clk=Pin(2), dio=Pin(3))
display.show("IDLE")
print("Display initialized")

button = Pin(15, Pin.IN, Pin.PULL_UP)

i2c0 = SoftI2C(scl=Pin(1), sda=Pin(0), freq=100000)
rtc = DS1307(0x68, i2c0)

TOGGL_API_KEY = TOGGL_API_KEY + ":api_token"
TOGGL_API_KEY = TOGGL_API_KEY.encode("utf-8")
TOGGL_API_KEY = ubinascii.b2a_base64(TOGGL_API_KEY).decode("utf-8").strip()

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("", "")
while not wifi.isconnected():
    time.sleep(1)
print("Connected to Wi-Fi")

def get_iso_timestamp():
    datetime_tuple = rtc.datetime
    iso_timestamp = f"{datetime_tuple[0]}-{datetime_tuple[1]:02d}-{datetime_tuple[2]:02d}T{datetime_tuple[3]:02d}:{datetime_tuple[4]:02d}:{datetime_tuple[5]:02d}Z"
    return iso_timestamp

def start_toggl_session():
    print("RTC Time:", rtc.datetime)
    url = f"https://api.track.toggl.com/api/v9/workspaces/{TOGGL_WORKSPACE_ID}/time_entries"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {TOGGL_API_KEY}"
    }
    data = {
        "created_with": "Pomodoro Timer",
        "description": "",
        "tags": [],
        "billable": False,
        "workspace_id": int(TOGGL_WORKSPACE_ID),
        "duration": -1,
        "start": get_iso_timestamp(),
        "stop": None
    }
    print("Starting Toggl session:", data)
    response = urequests.post(url, json=data, headers=headers)
    return response.json().get('id', None)

def stop_toggl_session(entry_id):
    if not entry_id:
        return
    url = f"https://api.track.toggl.com/api/v9/workspaces/{TOGGL_WORKSPACE_ID}/time_entries/{entry_id}/stop"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {TOGGL_API_KEY}"
    }
    response = urequests.patch(url, headers=headers)
    print("Stopping Toggl session:", response.json())
    return response.json()

current_state = "IDLE"
entry_id = None
timer = Timer()
remaining_time = 0

def update_display(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    display.numbers(minutes, secs)

def countdown_callback(t):
    global remaining_time, current_state
    if remaining_time <= 0:
        timer.deinit()
        if current_state == "WORK":
            print("Work session ended, starting break")
            start_break()
        else:
            print("Break session ended, starting work")
            start_work()
        return

    update_display(remaining_time)
    remaining_time -= 1

def start_countdown(duration):
    global remaining_time
    remaining_time = duration
    timer.init(period=1000, mode=Timer.PERIODIC, callback=countdown_callback)

def start_work():
    global current_state, entry_id
    current_state = "WORK"
    entry_id = start_toggl_session()
    print("Starting work session")
    start_countdown(WORK_DURATION)

def start_break():
    global current_state, entry_id
    current_state = "BREAK"
    stop_toggl_session(entry_id)
    display.show("REST")
    print("Starting break session")
    start_countdown(BREAK_DURATION)

def stop_session():
    global current_state, entry_id
    timer.deinit()
    stop_toggl_session(entry_id)
    current_state = "IDLE"
    display.show("IDLE")
    print("Session stopped")

while True:
    if button.value() == 0:
        if current_state == "IDLE":
            print("Button pressed: Starting work session")
            start_work()
        elif current_state in ["WORK", "BREAK"]:
            print("Button pressed: Stopping session")
            stop_session()
    time.sleep(0.1)
