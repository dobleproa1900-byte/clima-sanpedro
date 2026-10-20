import os
from datetime import datetime, timedelta
import requests

# Cargar variables de entorno desde GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 1. Obtener datos de Open-Meteo (se agrega precipitation_probability_max en daily)
url = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=-33.6791&longitude=-59.6644"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m,uv_index"
    "&hourly=temperature_2m,precipitation_probability"
    "&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max"
    "&timezone=America%2FArgentina%2FBuenos_Aires"
)

response = requests.get(url)
data = response.json()

current = data["current"]
daily = data["daily"]
hourly = data["hourly"]

# 2. Manejo de días y fechas en español
dias_semana = [
    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
]
meses = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

ahora = datetime.now()
fecha_hoy = f"{dias_semana[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]} de {ahora.year}"

# Días para el pronóstico extendido
dia_1_nombre = dias_semana[(ahora + timedelta(days=1)).weekday()]
dia_2_nombre = dias_semana[(ahora + timedelta(days=2)).weekday()]


def direccion_viento(grados):
    direcciones = [
        "Norte", "Noreste", "Este", "Sudeste",
        "Sur", "Sudoeste", "Oeste", "Noroeste"
    ]
    idx = int((grados + 22.5) / 45) % 8
    return direcciones[idx]


def descripcion_uv(uv):
    if uv < 3:
        return "Bajo"
    if uv < 6:
        return "Moderado"
    if uv < 8:
        return "Alto"
    if uv < 11:
        return "Muy alto"
    return "Extremo"


# 3. Formatear datos de hoy
temp = current["temperature_2m"]
sensacion = current["apparent_temperature"]
max_t = daily["temperature_2m_max"][0]
min_t = daily["temperature_2m_min"][0]
precip_prob = hourly["precipitation_probability"][0]
precip_mm = current["precipitation"]
viento_vel = current["wind_speed_10m"]
viento_dir = direccion_viento(current["wind_direction_10m"])
rafagas = current["wind_gusts_10m"]
humedad = current["relative_humidity_2m"]
uv = current["uv_index"]
uv_text = descripcion_uv(uv)
presion = int(current["surface_pressure"])

# Pronóstico por tramos (hoy)
t_manana = hourly["temperature_2m"][9]
t_tarde = hourly["temperature_2m"][15]
t_noche = hourly["temperature_2m"][21]

# Salida y Puesta del Sol
amanecer = datetime.fromisoformat(daily["sunrise"][0]).strftime("%H:%M")
atardecer = datetime.fromisoformat(daily["sunset"][0]).strftime("%H:%M")

# 4. Datos del Pronóstico Extendido (Día 1 y Día 2)
max_t1 = daily["temperature_2m_max"][1]
min_t1 = daily["temperature_2m_min"][1]
prob_p1 = daily["precipitation_probability_max"][1]

max_t2 = daily["temperature_2m_max"][2]
min_t2 = daily["temperature_2m_min"][2]
prob_p2 = daily["precipitation_probability_max"][2]

# 5. Construir el mensaje
mensaje = f"""📍 *San Pedro, Buenos Aires*
📅 {fecha_hoy}
Parcialmente nublado ⛅

🌡️ Temperatura: {temp}°C (Sensación: {sensacion}°C)
⬆️ Máx: {max_t}°C | ⬇️ Mín: {min_t}°C
🌧️ Precipitaciones: {precip_prob}% ({precip_mm}mm)
💨 Viento: {viento_vel} km/h ({viento_dir}) | Ráfagas: {rafagas} km/h
💧 Humedad: {humedad}%
☀️ Índice UV: {uv} ({uv_text})
📉 Presión: {presion} hPa

🕒 *Pronóstico por tramos (Hoy):*
- Mañana: ⛅ {t_manana}°C
- Tarde: ☀️ {t_tarde}°C
- Noche: 🌙 {t_noche}°C

📅 *Pronóstico Extendido:*
- *{dia_1_nombre} (Mañana):* ⬆️ {max_t1}°C | ⬇️ {min_t1}°C (🌧️ {prob_p1}%)
- *{dia_2_nombre} (Pasado):* ⬆️ {max_t2}°C | ⬇️ {min_t2}°C (🌧️ {prob_p2}%)

🌅 Amanecer: {amanecer} hs | 🌇 Atardecer: {atardecer} hs

_Fuente: Open-Meteo_"""

# 6. Enviar a Telegram
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}

res = requests.post(telegram_url, data=payload)

if res.status_code == 200:
    print("Reporte enviado con éxito.")
else:
    print(f"Error al enviar reporte: {res.status_code} - {res.text}")