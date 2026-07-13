from flask import Flask, render_template, request, redirect, session
import random
import string
import webbrowser
import threading
import os

try:
    import qrcode
except:
    qrcode = None

app = Flask(__name__)
app.secret_key = "EV_FINAL_KEY"

bookings = []

stations_data = {
    "Nagpur": [
        {"name": "IT Park EV Hub", "distance": "2 km", "crowd": "High"},
        {"name": "Bardi Charging Station", "distance": "4 km", "crowd": "Medium"},
        {"name": "Civil Lines EV Point", "distance": "5 km", "crowd": "Low"}
    ],
    "Mumbai": [
        {"name": "Bandra EV Hub", "distance": "3 km", "crowd": "High"},
        {"name": "Andheri Station", "distance": "5 km", "crowd": "Medium"}
    ],
    "Delhi": [
        {"name": "Connaught Place", "distance": "2 km", "crowd": "High"},
        {"name": "Noida Sector 18", "distance": "6 km", "crowd": "Medium"}
    ]
}

def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_qr(data, filename):
    if not os.path.exists("static"):
        os.makedirs("static")

    path = os.path.join("static", filename)

    if qrcode:
        img = qrcode.make(data)
        img.save(path)
    else:
        print("QR library missing")

    return filename


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['vehicle'] = request.form['vehicle']
        session['city'] = request.form['city']
        session['location'] = request.form['location']
        return redirect('/stations')

    return render_template("register.html")


@app.route('/stations')
def stations():
    city = session.get('city')
    data = stations_data.get(city, [])
    return render_template("stations.html", stations=data, city=city)


@app.route('/book/<station>')
def book(station):
    session['station'] = station
    return render_template("booking.html", station=station)


@app.route('/payment', methods=['POST'])
def payment():
    session['slot'] = request.form['slot']

    bookings.append({
        "name": session.get('name'),
        "vehicle": session.get('vehicle'),
        "city": session.get('city'),
        "station": session.get('station'),
        "slot": session.get('slot')
    })

    return redirect('/success')


@app.route('/success')
def success():
    token = generate_token()

    qr_data = f"""
Name: {session.get('name')}
Vehicle: {session.get('vehicle')}
City: {session.get('city')}
Station: {session.get('station')}
Slot: {session.get('slot')}
Token: {token}
"""

    qr_file = f"{token}.png"
    generate_qr(qr_data, qr_file)

    return render_template(
        "success.html",
        name=session.get('name'),
        vehicle=session.get('vehicle'),
        city=session.get('city'),
        station=session.get('station'),
        token=token,
        qr_image=qr_file
    )


@app.route('/admin')
def admin():
    return render_template("admin.html", bookings=bookings)


def open_browser():
    webbrowser.open("http://127.0.0.1:5000/")


if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, use_reloader=False)