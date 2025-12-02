from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import time
import threading
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone  # For IST conversion

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IOT.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- Database Model ----------
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    infrared = db.Column(db.Integer, nullable=False)
    accel = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ---------- Random Sensor Data Insertion ----------
def auto_insert_sensor_data():
    while True:
        temp = round(random.uniform(20.0, 40.0), 2)
        ir = random.randint(0, 1)
        accel = round(random.uniform(-2.0, 2.0), 2)

        # Insert with UTC-aware timestamp
        now_utc = datetime.now(timezone.utc)
        data = SensorData(temperature=temp, infrared=ir, accel=accel, timestamp=now_utc)
        with app.app_context():
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

    # Convert each timestamp to IST and format for display
    for row in rows:
        if row.timestamp.tzinfo is None:
            row.timestamp = row.timestamp.replace(tzinfo=timezone.utc)
        row.timestamp = row.timestamp.astimezone(india)

    return render_template('dashboard.html', rows=rows)

if __name__ == '__main__':
=======
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import time
import threading
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone  # For IST conversion

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IOT.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- Database Model ----------
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    infrared = db.Column(db.Integer, nullable=False)
    accel = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ---------- Random Sensor Data Insertion ----------
def auto_insert_sensor_data():
    while True:
        temp = round(random.uniform(20.0, 40.0), 2)
        ir = random.randint(0, 1)
        accel = round(random.uniform(-2.0, 2.0), 2)

        # Insert with UTC-aware timestamp
        now_utc = datetime.now(timezone.utc)
        data = SensorData(temperature=temp, infrared=ir, accel=accel, timestamp=now_utc)
        with app.app_context():
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

    # Convert each timestamp to IST and format for display
    for row in rows:
        if row.timestamp.tzinfo is None:
            row.timestamp = row.timestamp.replace(tzinfo=timezone.utc)
        row.timestamp = row.timestamp.astimezone(india)

    return render_template('dashboard.html', rows=rows)

if __name__ == '__main__':
    app.run()