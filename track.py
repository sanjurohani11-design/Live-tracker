from flask import Flask, request, render_template_string
import requests
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Live Tracker</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
body{font-family:Arial;background:#0f172a;color:white;margin:0}
.container{width:90%%;margin:auto;padding:10px}
.card{background:#1e293b;padding:15px;border-radius:10px;margin-top:10px}
input,button{width:100%%;padding:10px;margin-top:10px;border-radius:8px;border:none}
button{background:#3b82f6;color:white}
#map{height:320px;border-radius:10px;margin-top:10px}
</style>
</head>
<body>

<div class="container">

<div class="card">
<form method="POST">
<input type="text" name="number" placeholder="Enter Number" required>
<button>Search</button>
</form>
</div>

{% if data %}
<div class="card">
<b>Name:</b> {{data.name}}<br>
<b>Mobile:</b> {{data.mobile}}<br>
<b>Address:</b> <span id="addr">{{data.address}}</span>
</div>

<div class="card">
<div id="map"></div>
<div id="distance"></div>
</div>
{% endif %}

</div>

<script>
let map = L.map('map').setView([20.59,78.96],5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

let address = document.getElementById("addr")?.innerText;

if(address){

navigator.geolocation.getCurrentPosition(function(pos){

let userLat = pos.coords.latitude;
let userLng = pos.coords.longitude;

L.marker([userLat,userLng]).addTo(map).bindPopup("You");

fetch("https://nominatim.openstreetmap.org/search?format=json&q="+encodeURIComponent(address))
.then(res=>res.json())
.then(d=>{

if(d.length>0){

let lat = d[0].lat;
let lon = d[0].lon;

L.marker([lat,lon]).addTo(map).bindPopup("Target");

L.polyline([[userLat,userLng],[lat,lon]],{color:"blue"}).addTo(map);

map.fitBounds([[userLat,userLng],[lat,lon]]);

// distance
function dist(a,b,c,d){
let R=6371;
let dLat=(c-a)*Math.PI/180;
let dLon=(d-b)*Math.PI/180;
let x=Math.sin(dLat/2)**2+
Math.cos(a*Math.PI/180)*Math.cos(c*Math.PI/180)*
Math.sin(dLon/2)**2;
return R*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x));
}

let km = dist(userLat,userLng,lat,lon);

document.getElementById("distance").innerHTML="📏 Distance: "+km.toFixed(2)+" KM";

}

});

});

}
</script>

</body>
</html>
"""

# ===== ONLY NEW API =====
def fetch_data(number):
    try:
        url = f"https://exploitsindia.site/track/live.php?term={number}"
        res = requests.get(url, timeout=10).text

        def get(pattern):
            m = re.search(pattern, res)
            return m.group(1).strip() if m else "N/A"

        return {
            "name": get(r"Name[:\-]?\s*(.*)"),
            "mobile": number,
            "address": get(r"Address[:\-]?\s*(.*)")
        }

    except:
        return None

@app.route("/", methods=["GET","POST"])
def home():
    data = None

    if request.method == "POST":
        number = request.form.get("number")
        data = fetch_data(number)

    return render_template_string(HTML, data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)