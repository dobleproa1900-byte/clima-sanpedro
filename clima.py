import os
import requests
from datetime import datetime

LAT = -33.68
LON = -59.66
TIMEZONE = "America/Argentina/Buenos_Aires"

# Obtenemos las credenciales desde variables de entorno (GitHub Actions)
# o puedes poner los valores por defecto entre comillas si ejecutas localmente.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8600687554:AAGz_GBgiJx-M1UhN7gMYvfCnPfVCcYwXK8")

DESTINATARIOS = [
    {"nombre": "Gerardo", "chat_id": os.getenv("CHAT_ID_1", "8640771491")},
    {"nombre": "Valeria", "chat_id": os.getenv("CHAT_ID_2", "TU_CHAT_ID_2")},
]

# 1. Obtener datos meteorológicos de Open-Meteo
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

# 2. Evaluar condiciones y alertas
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

alerta_helada = f"\n⚠️ *ALERTA HELADA* — Temperatura mínima: {temp_min}°C" if temp_min <= 2 else ""
alerta_lluvia = f"\n🌧️ *ALERTA LLUVIA* — Probabilidad: {prob_lluvia}%" if prob_lluvia >= 70 else ""

dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
hoy = datetime.now()
fecha_hoy = f"{dias[hoy.weekday()]} {hoy.day} de {meses[hoy.month-1]} de {hoy.year}"

# 3. Enviar a Telegram
url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

for dest in DESTINATARIOS:
    if not dest["chat_id"]:
        continue

    mensaje = f"""🌤️ *Reporte del clima — San Pedro*
📅 {fecha_hoy} — ¡Buenos días {dest['nombre']}!

🌡️ *Ahora:* {temp}°C
📈 *Máxima:* {temp_max}°C | 📉 *Mínima:* {temp_min}°C
☁️ *Condición:* {condicion}
💨 *Viento:* {viento} km/h
🌧️ *Lluvia:* {prob_lluvia}% | {lluvia_mm}mm
🌞 *UV:* {uv}
🌅 *Sale:* {sunrise} | *Se oculta:* {sunset}{alerta_helada}{alerta_lluvia}

¡Buen día! 💪"""

    payload = {
        "chat_id": dest["chat_id"],
        "text": mensaje,
        "parse_mode": "Markdown"
    }

    try:
        resp = requests.post(url_telegram, data=payload, timeout=10)
        if resp.status_code == 200:
            print(f"✅ Enviado a {dest['nombre']} ({dest['chat_id']}): OK")
        else:
            print(f"❌ Error al enviar a {dest['nombre']}: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"⚠️ Error de conexión con {dest['nombre']}: {e}")

print("Completado:", datetime.now().strftime("%Y-%m-%d %H:%M"))