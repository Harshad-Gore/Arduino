# for our raybyte by eagle and lotus
import serial
from serial.tools import list_ports
import folium
from datetime import datetime
import time
import webbrowser
import os
from math import radians, sin, cos, sqrt, atan2
import csv
from twilio.rest import Client
import threading

HOME_LAT = 18.6748823
HOME_LON = 73.8917839
SAFE_RADIUS = 20.0
MAP_FILE = "arrest_monitor.html"
GPS_HISTORY_SIZE = 5  # gps ch history size, jyada increase nko kru slow houn jail
# tera twilio ka account sign up kiya hai
# email - harshad7237@gmail.com
# pass - JX7GM0TK@**********  tuze pata hai * kya hai okay
TWILIO_ACCOUNT_SID = 'ACe5a6261d91c4dadde60b382346dc9c2d'
TWILIO_AUTH_TOKEN = '5e6ed8e424dc0047007a04811aaf79f4'
TWILIO_PHONE_NUMBER = '+12293634873'
ALERT_RECIPIENTS = ['+917745860406']

# yaha pe person ki details hai kuch galat ho toh edit kar lena
PERSON_DETAILS = {
    "name": "Abhinav Badhe",
    "age": 19,
    "case_number": "HR/2025/7890",
    "offense": "Bail Voilation",
    "allowed_radius": f"{SAFE_RADIUS} meters",
    "tracking_id": "GPS-ALERT-001",
    "officer_in_charge": "Srikant Tiwari",
    "last_seen": "Initializing..."
}

HOME_DETAILS = {
    "address": "Kanda Market, Pravara Water Canal",
    "landmark": "Shelke Eye Hospital",
    "city": "Shrirampur",
    "jurisdiction": "Shrirampur Police"
}

gps_history = []
alert_history = []
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

last_sms_time = 0
sms_lock = threading.Lock()

# yeh function sms bhejta hai jab kuch gadbad hota hai
def send_sms_alert(message):
    global last_sms_time
    with sms_lock:
        now = time.time()
        if now - last_sms_time < 5:
            # time tere hisab se set kar, abhi 5 sec per sms hai
            return
        last_sms_time = now
        for recipient in ALERT_RECIPIENTS:
            try:
                client.messages.create(
                    body=message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=recipient
                )
            except Exception as e:
                print(f"Failed to send SMS alert: {str(e)}")

def haversine(lat1, lon1, lat2, lon2):
    # distance nikalne ka formula hai yeh
    R = 6371000
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# gps ne smooth chalav tyamule average kartoy
def process_gps_data(raw_lat, raw_lng):
    global gps_history
    gps_history.append((raw_lat, raw_lng))
    if len(gps_history) > GPS_HISTORY_SIZE:
        gps_history.pop(0)
    avg_lat = sum(p[0] for p in gps_history) / len(gps_history)
    avg_lng = sum(p[1] for p in gps_history) / len(gps_history)
    return avg_lat, avg_lng

# yaha pe dekh raha hai ki koi tez bhaag raha hai ya boundary cross kiya kya
def check_violation(distance, previous_distance):
    current_speed = abs(distance - previous_distance)
    if current_speed > 10:
        return "RAPID MOVEMENT DETECTED"
    elif distance > SAFE_RADIUS:
        return "BOUNDARY BREACHED"
    return None

# tracking ka data file me likhne ke liye file bana raha hai
def init_log():
    with open('tracking_log.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Distance', 'Status'])

def log_data(timestamp, lat, lng, distance, status):
    # har update ka record rakh raha hai file me
    with open('tracking_log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, lat, lng, distance, status])

# map bana raha hai jaha pe home ka marker aur info box dikh raha hai
def create_map():
    m = folium.Map(location=[HOME_LAT, HOME_LON], zoom_start=18)
    home_tooltip = f"""<b>{HOME_DETAILS['address']}</b><br>
    {HOME_DETAILS['landmark']}<br>
    {HOME_DETAILS['city']}<br>
    Jurisdiction: {HOME_DETAILS['jurisdiction']}"""
    folium.Marker(
        [HOME_LAT, HOME_LON],
        tooltip=home_tooltip,
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)
    info_html = f"""
    <div style="position:fixed;top:50px;left:50px;width:350px;background:white;padding:15px;z-index:9999;border:3px solid #cc0000;border-radius:10px;">
        <h3 style="color:#cc0000;margin-top:0;">Home Arrest Monitor</h3>
        <div style="background:#ffe6e6;padding:10px;border-radius:5px;">
            <h4 style="margin:0 0 10px 0;">Subject Details:</h4>
            <p style="margin:5px 0;"><b>Name:</b> {PERSON_DETAILS['name']}<br><b>Case No:</b> {PERSON_DETAILS['case_number']}<br><b>Tracking ID:</b> {PERSON_DETAILS['tracking_id']}</p>
        </div>
        <div style="margin-top:15px;background:#f0f0f0;padding:10px;border-radius:5px;">
            <p style="margin:5px 0;"><b>Last Update:</b> <span id="updateTime">-</span></p>
        </div>
    </div>
    <script>setTimeout(function(){{window.location.reload(1);}},3000);</script>
    """
    m.get_root().html.add_child(folium.Element(info_html))
    return m

# yeh function har update pe map ko refresh karta hai aur banda ka marker dalta hai
def update_map(m, lat, lng, distance):
    for _ in range(3):
        try:
            m = create_map()
            person_tooltip = f"""<b>{PERSON_DETAILS['name']}</b><br>
            Age: {PERSON_DETAILS['age']}<br>
            Case: {PERSON_DETAILS['case_number']}<br>
            Offense: {PERSON_DETAILS['offense']}<br>
            Last Seen: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Distance: {distance:.1f}m"""
            folium.Marker(
                [lat, lng],
                tooltip=person_tooltip,
                icon=folium.Icon(color='blue' if distance <= SAFE_RADIUS else 'red', icon='user')
            ).add_to(m)
            folium.Circle(
                location=[HOME_LAT, HOME_LON],
                radius=SAFE_RADIUS,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.2
            ).add_to(m)
            folium.PolyLine(
                locations=[[HOME_LAT, HOME_LON], [lat, lng]],
                color='blue',
                weight=2,
                dash_array='5'
            ).add_to(m)
            m.get_root().html.add_child(folium.Element(f"""
            <script>
            document.getElementById('updateTime').innerHTML = '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}';
            </script>
            """))
            m.save(MAP_FILE)
            break
        except:
            time.sleep(1)

def get_arduino_port():
    # yeh function arduino ka port dhundta hai system me
    ports = list_ports.comports()
    for p in ports:
        if 'Arduino' in p.description or 'CH340' in p.description:
            return p.device
    return None

def main():
    # sab kuch yaha se start hota hai
    arduino_port = get_arduino_port()
    if not arduino_port:
        return
    try:
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        print(f"Connected to {arduino_port}")
        m = create_map()
        m.save(MAP_FILE)
        webbrowser.open(f"file://{os.path.abspath(MAP_FILE)}")
        init_log()
        previous_distance = 0
        while True:
            line = ser.readline().decode().strip()
            if line.startswith("TRACK:"):
                # yaha pe gps ka data mil raha hai arduino se
                data = line.split(":")[1].split(",")
                raw_lat = float(data[0])
                raw_lng = float(data[1])
                lat, lng = process_gps_data(raw_lat, raw_lng)
                distance = haversine(lat, lng, HOME_LAT, HOME_LON)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                violation = check_violation(distance, previous_distance)
                status = "NORMAL"
                if violation:
                    # agar boundry breach hua toh alert bhej raha hai
                    alert_msg = f"{timestamp} - {violation} at {distance:.1f}m from residence"
                    print(alert_msg)
                    alert_history.append(alert_msg)
                    send_sms_alert(
                        f"\n{PERSON_DETAILS['name']} - {violation}\n"
                        f"Coordinates: {lat:.6f}, {lng:.6f}\n"
                        f"Distance: {distance:.1f}m\n"
                    )
                    status = violation
                log_data(timestamp, lat, lng, distance, status)
                update_map(m, lat, lng, distance)
                previous_distance = distance
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()


# remote desktop access code - QM1NP5
# acc sid - ACe5a6261d91c4dadde60b382346dc9c2d
# auth token - 5e6ed8e424dc0047007a04811aaf79f4
# twilio number - +12293634873


# GPS Module -> Arduino
# VCC       -> 3.3V
# GND       -> GND
# TX        -> D3
# RX        -> D4

# Buzzer -> Arduino
# (+)     -> D5
# (-)     -> GND

# 2 software ek time pe same usb port nhi use kr sakte, toh serial monitor mat kholna
# aur ardiuno me sketch upload karne se pehle ye program band karna, nahi toh upload nahi hoga


# csv file me arrested person ka live data store hoga like uska location info, voilation type, aur bc jo bhi ho
# all the best pillu 😆
