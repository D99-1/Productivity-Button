import urequests
import machine
import time
import ubinascii
import network

# Configuration
API_URL = "https://api.track.toggl.com/api/v9" 
API_Token = ""
WORKSPACE_ID = 0000  # Replace with Workspace ID as INT
Wifi_SSID = ""
Wifi_Password = ""


# GPIO Config
BUTTON_PIN = 2
LED_PIN = 11
POLL_INTERVAL = 10 
DEBOUNCE_DELAY = 15000 


button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin(LED_PIN, machine.Pin.OUT)

API_Token = API_Token + ":api_token"
API_Token = API_Token.encode("utf-8")
API_Token = ubinascii.b2a_base64(API_Token)
API_Token = API_Token.decode("utf-8")
API_Token = API_Token.replace("\n", "")

header = {"Authorization": f"Basic {API_Token.strip()}"}

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Wi-Fi connected:", wlan.ifconfig())

connect_wifi(Wifi_SSID, Wifi_Password)

def check_session():
    try:
        response = urequests.get(API_URL + "/me/time_entries/current", headers=header)
        if response:
            session_status = response.json()
            if session_status is None:
                print("Session is not running")
                return [False, None, None]
            else:
                print("Session is running")
                return [True, session_status['id'], session_status['workspace_id']]
        else:
            print("Failed to get session status")
            return [False, None, None]
    except Exception as e:
        print("Error checking session:", e)
        return [False, None, None]
    finally:
        if "response" in locals():
            response.close()

def stop_session(wid,sid):
    try:
        response = urequests.patch(API_URL + f"/workspaces/{wid}/time_entries/{sid}/stop", headers=header)
        if response:
            led.off()
            print("Session stopped successfully")
        else:
            print("Failed to stop session")
    except Exception as e:
        print("Error stopping session:", e)
    finally:
        if "response" in locals():
            response.close()

def start_session():
    try:
        timeRespose = urequests.get("https://timeapi.io/api/time/current/zone?timeZone=UTC")
        if timeRespose.status_code == 200:
            timeData = timeRespose.json()['dateTime'] + "Z"
            timeRespose.close()

            data = {
                "created_with": "",
                "description": "",
                "tags": [],
                "billable": False,
                "workspace_id": WORKSPACE_ID,
                "duration": -1,
                "start": timeData,
                "stop": None
            }

            url = API_URL + f"/workspaces/{WORKSPACE_ID}/time_entries"
            
            response = urequests.post(url, headers=header, json=data)
            
            if response.status_code == 200:
                session_data = response.json()
                response.close()
                led.on()
                print("Session started successfully")
                print("Session ID:", session_data.get('id'))
            else:
                print("Failed to start session. Status code:", response.status_code)
                print("Response content:", response.text) 
                response.close() 
        else:
            print("Failed to get time. Status code:", timeRespose.status_code)
            timeRespose.close()
    except Exception as e:
        print("Error starting session:", e)
    finally:
        if "timeRespose" in locals():
            timeRespose.close()
        if "response" in locals():
            response.close()



last_button_press_time = 0


def button_callback(pin):
    global last_button_press_time
    current_time = time.ticks_ms()

    if time.ticks_diff(current_time, last_button_press_time) > DEBOUNCE_DELAY:
        led.value(not led.value())
        time.sleep(0.1)
        led.value(not led.value())
        time.sleep(0.1)
        led.value(not led.value())
        time.sleep(0.1)
        led.value(not led.value())
        print("Button pressed!")
        session_running = check_session()
        if session_running[0]:
            stop_session(session_running[2],session_running[1])
        elif not session_running[0]:
            start_session()
        last_button_press_time = current_time 


button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_callback)


def main():
    while True:
        session_running = check_session()
        led.value(session_running[0])
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
