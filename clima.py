import requests
import urllib.parse
import locale
from datetime import datetime

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass

LAT = -33.68
LON = -59.66
TIMEZONE = "America/Argentina/Buenos_Aires"
DESTINATARIOS = [
    {"phone": "5493329599250", "apikey": "4769644", "nombre": "Gerardo"},
    {"phone": "5493329668717", "apikey": "8522696", "nombre": "Valeria"},
]

url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    f"&current_weather=true"
    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
    f"precipitation_sum,sunrise,sunset,uv_index_max"
    f"&wind_speed_unit=kmh"
    f"&timezone={TIMEZONE}"
    f"&forecast_days=1"
)

response = requests.get(url)
data = response.json()
w = data["current_weather"]
daily = data["daily"]

temp = w["temperature"]
viento = w["windspeed"]
codigo = w["weathercode"]
temp_max = daily["temperature_2m_max"][0]
temp_min = daily["temperature_2m_min"][0]
prob_lluvia = daily["precipitation_probability_max"][0]
lluvia_mm = daily["precipitation_sum"][0]
uv = daily["uv_index_max"][0]
sunrise = daily["sunrise"][0].split("T")[1]
sunset = daily["sunset"][0].split("T")[1]

if codigo >= 61:
    condicion = "Lluvia 🌧️"
elif codigo >= 51:
    condicion = "Llovizna 🌦️"
elif codigo >= 45:
    condicion = "Niebla 🌫️"
elif codigo >= 3:
    condicion = "Nublado ☁️"
elif codigo >= 1:
    condicion = "Parcialmente nublado ⛅"
else:
    condicion = "Despejado ☀️"

alerta_helada = f"\n⚠️ ALERTA HELADA — Temperatura mínima: {temp_min}°C" if temp_min <= 2 else ""
alerta_lluvia = f"\n🌧️ ALERTA LLUVIA — Probabilidad: {prob_lluvia}%" if prob_lluvia >= 70 else ""

fecha_hoy = datetime.now().strftime("%A %d de %B de %Y").capitalize()

for dest in DESTINATARIOS:
    mensaje = f"""🌤️ Reporte del clima — San Pedro
📅 {fecha_hoy} — Buenos días {dest['nombre']}!
🌡️ Ahora: {temp}°C
📈 Máxima: {temp_max}°C | 📉 Mínima: {temp_min}°C
☁️ Condición: {condicion}
💨 Viento: {viento} km/h
🌧️ Lluvia: {prob_lluvia}% | {lluvia_mm}mm
🌞 UV: {uv}
🌅 Sale: {sunrise} | Se oculta: {sunset}{alerta_helada}{alerta_lluvia}
¡Buen día! 💪"""
    texto_encoded = urllib.parse.quote(mensaje)
    url_callmebot = f"https://api.callmebot.com/whatsapp.php?phone={dest['phone']}&text={texto_encoded}&apikey={dest['apikey']}"
    resp = requests.get(url_callmebot)
    print(f"Enviado a {dest['nombre']}: {resp.status_code}")

print("Completado:", datetime.now().strftime("%Y-%m-%d %H:%M"))
