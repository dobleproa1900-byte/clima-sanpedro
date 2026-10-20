import os
from datetime import datetime
import requests

# Cargar variables de entorno desde GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 1. Obtener datos de Open-Meteo
url = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=-33.6791&longitude=-59.6644"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m,uv_index"
    "&hourly=temperature_2m,precipitation_probability"
    "&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset"
    "&timezone=America%2FArgentina%2FBuenos_Aires"
)

response = requests.get(url)
data = response.json()

current = data["current"]
daily = data["daily"]
hourly = data["hourly"]


# 2. Funciones auxiliares para nombres y formatos
def obtener_fecha_espanol():
    dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]
    meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    ahora = datetime.now()
    return f"{dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]} de {ahora.year}"


def direccion_viento(grados):
    direcciones = [
        "Norte",
        "Noreste",
        "Este",
        "Sudeste",
        "Sur",
        "Sudoeste",
        "Oeste",
        "Noroeste",
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


# 3. Formatear datos
fecha = obtener_fecha_espanol()
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

# Pronóstico por tramos (tomando horas clave: 09:00, 15:00 y 21:00)
t_manana = hourly["temperature_2m"][9]
t_tarde = hourly["temperature_2m"][15]
t_noche = hourly["temperature_2m"][21]

# Salida y Puesta del Sol
amanecer = datetime.fromisoformat(daily["sunrise"][0]).strftime("%H:%M")
atardecer = datetime.fromisoformat(daily["sunset"][0]).strftime("%H:%M")

# 4. Construir el mensaje de texto
mensaje = f"""📍 *San Pedro, Buenos Aires*
📅 {fecha}
Parcialmente nublado ⛅

🌡️ Temperatura: {temp}°C (Sensación: {sensacion}°C)
⬆️ Máx: {max_t}°C | ⬇️ Mín: {min_t}°C
🌧️ Precipitaciones: {precip_prob}% ({precip_mm}mm)
💨 Viento: {viento_vel} km/h ({viento_dir}) | Ráfagas: {rafagas} km/h
💧 Humedad: {humedad}%
☀️ Índice UV: {uv} ({uv_text})
📉 Presión: {presion} hPa

🕒 *Pronóstico por tramos:*
- Mañana: ⛅ {t_manana}°C
- Tarde: ☀️ {t_tarde}°C
- Noche: 🌙 {t_noche}°C

🌅 Amanecer: {amanecer} hs | 🌇 Atardecer: {atardecer} hs

_Fuente: Open-Meteo_"""

# 5. Enviar mensaje a Telegram
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}

res = requests.post(telegram_url, data=payload)

if res.status_code == 200:
    print("Reporte enviado con éxito.")
else:
    print(f"Error al enviar reporte: {res.status_code} - {res.text}")