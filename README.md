# Home Arrest GPS Tracking System

## Overview
This project is a simple home arrest GPS tracking and geofencing system. It uses an Arduino with a GPS module to track a person's location, sends alerts if they leave a defined area, and visualizes live tracking data on a web map. It also logs data to Firebase and sends SMS alerts using Twilio.

---

## Features
- **Live GPS Tracking:** See the person's current location on a map in real time.
- **Geofencing:** Set a safe area (radius) around a home. Get alerts if the person leaves this area.
- **SMS Alerts:** Sends SMS to police/guardian if the person leaves the safe area or moves rapidly.
- **Data Logging:** Saves all location updates and alerts to a CSV file and Firebase.
- **Web Visualization:** View live location and recent logs in your browser.
- **Easy Setup:** Simple Python and HTML files, easy to run and modify.
- **Modern UI:** Clean, responsive, and easy-to-read web pages for monitoring.

---

## How to Run (Step by Step)

### 1. Hardware Setup
#### a. Components Needed
- Arduino Uno (or compatible)
- GPS Module (e.g., NEO-6M)
- Buzzer
- Jumper wires
- USB cable for Arduino

#### b. Arduino to GPS Module Connections
| GPS Module Pin | Arduino Pin |
|:--------------:|:----------:|
| VCC            | 3.3V or 5V |
| GND            | GND        |
| TX             | D3         |
| RX             | D4         |

#### c. Buzzer Connection
| Buzzer Pin | Arduino Pin |
|:----------:|:-----------:|
| + (long)   | D5          |
| - (short)  | GND         |

#### d. Upload Arduino Code
- Open `sketch.txt` in the Arduino IDE.
- Select the correct board and port from the Tools menu.
- Click the Upload button.
- **Important:** Close the Arduino IDE after uploading, so Python can use the serial port.

---

### 2. Software Setup
#### a. Install Python (if not already installed)
- Download and install Python 3.x from [python.org](https://www.python.org/downloads/).
- During installation, check "Add Python to PATH".

#### b. Install Required Python Packages
Open a terminal (Command Prompt or PowerShell) and run:
```
pip install pyserial folium twilio firebase-admin
```

#### c. Set Up Firebase
- Go to [firebase.google.com](https://firebase.google.com/) and create a new project.
- In the project settings, go to Service Accounts and generate a new private key.
- Download the JSON file and place it in your project folder as `firebase_service_account.json`.
- In the Firebase Realtime Database, create a new database and set the rules to allow read/write for testing.
- Copy your database URL and update it in `track.py` (look for `FIREBASE_DB_URL`).

#### d. Set Up Twilio (for SMS alerts)
- Sign up at [twilio.com](https://www.twilio.com/).
- Verify your phone number.
- Get your Account SID, Auth Token, and Twilio phone number from the Twilio Console.
- Put these in `track.py` (use placeholders for public sharing).

#### e. Connect Arduino
- Plug in your Arduino with the GPS module and buzzer attached.
- Make sure no other program (like Arduino IDE) is using the same COM port.

---

### 3. Run the Python Tracking Script
- Open a terminal in the project folder.
- Run:
```
python Geofencing/track.py
```
- The script will:
  - Read GPS data from Arduino
  - Log data to CSV and Firebase
  - Send SMS alerts if needed
  - Update the map HTML file
  - Open the map in your browser

---

### 4. View the Map and Logs
- Open `arrest_monitor.html` in your browser to see the live map and subject details.
- Open `Geofencing/live_tracking.html` in your browser to see live tracking and recent logs (requires Firebase setup).
- Both pages are styled for clarity and mobile-friendly viewing.

---

### 5. CSV Logs
- All location updates are saved in `tracking_log.csv` for your records.
- You can open this file in Excel or any spreadsheet app.

---

## Notes
- Use placeholder credentials for public code sharing.
- Do not share your real Twilio or Firebase keys.
- The system is for educational/demo purposes. For real use, add security and privacy features.
- If you change the COM port or wiring, update the code accordingly.

---

## Troubleshooting
- **Serial port error:**
  - Check that the Arduino is connected and no other program is using the port.
  - Use Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac) to find the correct port.
- **Map does not update:**
  - Check your Python script output for errors.
  - Make sure the browser is opening the correct HTML file.
- **Firebase or Twilio errors:**
  - Double-check your credentials and internet connection.
  - Make sure your Firebase rules allow writing.
- **No GPS data:**
  - Make sure the GPS module has a clear view of the sky.
  - Wait a few minutes for the first GPS fix.

---

## Credits
- Made for learning and demo purposes.
- Uses open source libraries: Folium, Leaflet, Firebase, Twilio, PySerial.
- UI inspired by modern dashboard designs for clarity and ease of use.

## Contributors
- https://github.com/nambhadane  
- https://github.com/krishnarane2005  
- https://github.com/Rohan264v
- https://github.com/Vanshika6605
