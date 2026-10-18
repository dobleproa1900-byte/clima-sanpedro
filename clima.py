import requests
from datetime import datetime

TOKEN = "8938156715:AAGl4Bzqv4g8FFpYi_Dl_kBK2hmk9J7J04A"
DESTINATARIOS = ["8640771491", "8872397261"]

LAT = -33.68
LON = -59.66
TIMEZONE = "America/Argentina/Buenos_Aires"

url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    f"&current_weather=true"
    f"&hourly=temperature_2m,apparent_temperature,relativehumidity_2m,precipitation_probability,windspeed_10m,winddirection_10m,surface_pressure,uv_index"
    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
    f"precipitation_sum,sunrise,sunset,uv_index_max,windspeed_10m_max,windgusts_10m_max"
    f"&wind_speed_unit=kmh"
    f"&timezone={TIMEZONE}"
    f"&forecast_days=1"
)

response = requests.get(url)
data = response.json()
w = data["current_weather"]
daily = data["daily"]
hourly = data["hourly"]

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
viento_max = daily["windspeed_10m_max"][0]
rafaga = daily["windgusts_10m_max"][0]

# Sensación térmica y humedad de la hora actual
hora_actual = datetime.now().hour
temp_aparente = hourly["apparent_temperature"][hora_actual]
humedad = hourly["relativehumidity_2m"][hora_actual]
presion = hourly["surface_pressure"][hora_actual]

# Dirección del viento
dir_viento = w.get("winddirection", 0)
dirs = ["Norte","Noreste","Este","Sureste","Sur","Suroeste","Oeste","Noroeste"]
dir_nombre = dirs[round(dir_viento / 45) % 8]

# Pronóstico por tramos
temp_manana = hourly["temperature_2m"][8]
temp_tarde = hourly["temperature_2m"][14]
temp_noche = hourly["temperature_2m"][20]

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

if uv <= 2:
    uv_desc = "Bajo"
elif uv <= 5:
    uv_desc = "Moderado"
elif uv <= 7:
    uv_desc = "Alto - usar protector"
elif uv <= 10:
    uv_desc = "Muy alto"
else:
    uv_desc = "Extremo"

alerta_helada = f"\n⚠️ ALERTA HELADA — Mínima: {temp_min}°C" if temp_min <= 2 else ""
alerta_lluvia = f"\n🌧️ ALERTA LLUVIA — Probabilidad: {prob_lluvia}%" if prob_lluvia >= 70 else ""

dias = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
hoy = datetime.now()
fecha_hoy = f"{dias[hoy.weekday()]} {hoy.day} de {meses[hoy.month-1]} de {hoy.year}"

mensaje = f"""📍 *San Pedro, Buenos Aires*
📅 {fecha_hoy}
{condicion}

🌡️ Temperatura: {temp}°C (Sensación: {temp_aparente}°C)
⬆️ Máx: {temp_max}°C | ⬇️ Mín: {temp_min}°C
🌧️ Precipitaciones: {prob_lluvia}% ({lluvia_mm}mm)
💨 Viento: {viento} km/h ({dir_nombre}) | Ráfagas: {rafaga} km/h
💧 Humedad: {humedad}%
☀️ Índice UV: {uv} ({uv_desc})
📉 Presión: {presion:.0f} hPa

🕒 *Pronóstico por tramos:*
- Mañana: 🌤️ {temp_manana}°C
- Tarde: ☀️ {temp_tarde}°C
- Noche: 🌙 {temp_noche}°C

🌅 Amanecer: {sunrise} hs | 🌇 Atardecer: {sunset} hs{alerta_helada}{alerta_lluvia}

_Fuente: Open-Meteo_"""

url_telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
for chat_id in DESTINATARIOS:
    resp = requests.post(url_telegram, json={
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    })
    print(f"Enviado a {chat_id}: {resp.status_code}")

print("Completado:", datetime.now().strftime("%Y-%m-%d %H:%M"))
