from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import time, threading
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

# Raspberry Pi Sensor Imports
import RPi.GPIO as GPIO
import Adafruit_DHT
import smbus
import atexit

# ---------- Flask & Database Setup ----------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IOT.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- Sensor Configuration ----------
GPIO.setmode(GPIO.BCM)
IR_PIN = 17
GPIO.setup(IR_PIN, GPIO.IN)

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

bus = smbus.SMBus(1)
MPU6050_ADDR = 0x68
bus.write_byte_data(MPU6050_ADDR, 0x6B, 0)  # Wake up MPU6050

# ---------- GPIO Cleanup on Exit ----------
@atexit.register
def cleanup():
    GPIO.cleanup()

# ---------- Database Model ----------
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    infrared = db.Column(db.Integer, nullable=False)
    accel = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ---------- Sensor Reading Functions ----------
def read_accel():
    raw = bus.read_word_data(MPU6050_ADDR, 0x3B)
    val = raw if raw < 32768 else raw - 65536
    return round(val / 16384.0, 2)

# ---------- Background Sensor Insertion ----------
def auto_insert_sensor_data():
    while True:
        humidity, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        ir = GPIO.input(IR_PIN)
        accel = read_accel()
        now_utc = datetime.now(timezone.utc)

        if humidity is not None and temp is not None:
            with app.app_context():
                data = SensorData(
                    temperature=round(temp, 2),
                    infrared=ir,
                    accel=accel,
                    timestamp=now_utc
                )
                db.session.add(data)
                db.session.commit()
        time.sleep(10)

threading.Thread(target=auto_insert_sensor_data, daemon=True).start()

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    india = pytz_timezone('Asia/Kolkata')
    rows = SensorData.query.order_by(SensorData.timestamp.desc()).limit(50).all()

    for row in rows:
        if row.timestamp.tzinfo is None:
            row.timestamp = row.timestamp.replace(tzinfo=timezone.utc)
        row.timestamp = row.timestamp.astimezone(india)

    return render_template('dashboard.html', rows=rows)

# ---------- Run ----------
if __name__ == '__main__':
    app.run()