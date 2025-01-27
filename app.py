from flask import Flask, request, jsonify, render_template
from twilio.rest import Client
import math

app = Flask(__name__)



account_sid = 'AC82e085907070bcb30f6e495b664f2af5'
auth_token = '5d30a987575a9cccecd6e41c71e59fac'
client = Client(account_sid, auth_token)

def send_message(message):
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=message,
        to='whatsapp:+919627463880'
)


# Geofence center and radius
geofence_lat, geofence_lng = 29.867541708963497, 77.86683592449667
radius = 50  # Radius in meters

# Variable to track the last geofence status
last_in_range_status = None

# Shared variable to store the latest coordinates
latest_coordinates = {"latitude": 0, "longitude": 0}


# Haversine formula for distance calculation
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# Endpoint to receive location and check geofence
@app.route("/webhook", methods=["POST"])
def webhook():
    global last_in_range_status, latest_coordinates

    try:
        # Parse the incoming JSON data
        data = request.json
        if not data or "latitude" not in data or "longitude" not in data:
            return jsonify({"error": "Invalid data"}), 400

        user_lat = data["latitude"]
        user_lon = data["longitude"]

        # Update the latest coordinates
        latest_coordinates = {"latitude": user_lat, "longitude": user_lon}

        # Calculate distance and check if in range
        distance = haversine(user_lat, user_lon, geofence_lat, geofence_lng)
        in_range = distance <= radius

        # Check if the geofence status has changed
        if in_range != last_in_range_status:
            # Print new geofence status
            if in_range:
                send_message("User is in range")
            else:
                send_message("User is out of range")

            # Update the last status to the current status
            last_in_range_status = in_range

        # No response back to the Android app, just return empty
        return '', 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Map route to render map and send the coordinates to template
@app.route("/", methods=["GET"])
def map():
    # Pass initial data to the map template
    return render_template(
        "map.html",
        geofence_lat=geofence_lat,
        geofence_lng=geofence_lng,
        device_lat=latest_coordinates["latitude"],
        device_lng=latest_coordinates["longitude"],
        radius=radius,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
