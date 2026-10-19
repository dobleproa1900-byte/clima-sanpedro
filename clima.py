import os
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

# --- CONFIGURACIÓN DE APIS Y TELEGRAM ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LATITUD = -33.6791
LONGITUD = -59.6582

# 1. OBTENER DATOS DEL CLIMA (Open-Meteo)
url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUD}&longitude={LONGITUD}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,uv_index&hourly=temperature_2m,precipitation_probability&timezone=America%2FArgentina%2FBuenos_Aires"

try:
    res = requests.get(url_clima, timeout=15)
    res.raise_for_status()
    res_clima = res.json()

    if "current" not in res_clima:
        raise ValueError(f"Respuesta inesperada de la API: {res_clima}")

    current = res_clima["current"]
    hourly = res_clima["hourly"]

    temp_actual = current["temperature_2m"]
    humedad = current["relative_humidity_2m"]
    viento = current["wind_speed_10m"]
    uv_index = current["uv_index"]
    weather_code = current["weather_code"]
except Exception as e:
    print(f"Error al obtener datos del clima: {e}")
    exit(1)

# 2. DEFINIR BANNER Y TEMÁTICA SEGÚN EL CLIMA
def obtener_tematica(code):
    if code in [0, 1]:
        return "Dia Despejado / Soleado", "#FF8C00", "#FFF8DC"
    elif code in [2, 3]:
        return "Parcialmente Nublado", "#4682B4", "#F0F8FF"
    elif code in [51, 61, 80, 95]:
        return "Alerta de Lluvia / Tormenta", "#2F4F4F", "#E6F2FF"
    else:
        return "Tiempo Variable", "#5F9EA0", "#F5F5F5"

titulo_clima, color_primario, color_fondo = obtener_tematica(weather_code)

# 3. GENERAR DASHBOARD INFOGRÁFICO UNIFICADO (Matplotlib)
fig, (ax_info, ax_graph) = plt.subplots(2, 1, figsize=(8, 10), gridspec_kw={'height_ratios': [1, 1]})
fig.patch.set_facecolor(color_fondo)

# Panel Superior: Infografía
ax_info.set_facecolor(color_fondo)
ax_info.axis("off")

texto_card = (
    f"SAN PEDRO - REPORTE DIARIO\n"
    f"Estado: {titulo_clima}\n\n"
    f"• Temp. Actual: {temp_actual}°C\n"
    f"• Humedad: {humedad}%\n"
    f"• Viento: {viento} km/h\n"
    f"• Indice UV: {uv_index} ({'Extremo' if uv_index > 8 else 'Moderado/Bajo'})"
)
ax_info.text(0.05, 0.5, texto_card, fontsize=14, fontweight='bold', va='center', color="#1A1A1A")

# Panel Inferior: Gráfico 24h
horas = [datetime.fromisoformat(t).strftime("%H:00") for t in hourly["time"][:24]]
temps = hourly["temperature_2m"][:24]
lluvia = hourly["precipitation_probability"][:24]

ax_graph.set_facecolor("#FFFFFF")
ax_graph.plot(horas[::3], temps[::3], color=color_primario, marker='o', linewidth=2.5, label="Temp (°C)")
ax_graph.set_ylabel("Temperatura (°C)", color=color_primario, fontweight='bold')

ax_lluvia = ax_graph.twinx()
ax_lluvia.bar(horas[::3], lluvia[::3], alpha=0.3, color="#1E90FF", width=0.4, label="Lluvia (%)")
ax_lluvia.set_ylabel("Prob. Lluvia (%)", color="#1E90FF", fontweight='bold')

plt.title("Proyeccion para las proximas 24 horas", fontsize=12, fontweight='bold')
plt.tight_layout()

buffer_dashboard = BytesIO()
plt.savefig(buffer_dashboard, format='png', dpi=150)
buffer_dashboard.seek(0)
plt.close()

# 4. OBTENER MAPA DE RADAR (RainViewer)
def obtener_radar():
    try:
        res_radar = requests.get("https://api.rainviewer.com/public/weather-maps.json", timeout=10).json()
        host = res_radar["host"]
        path_radar = res_radar["radar"]["past"][-1]["path"]
        url_tile = f"{host}{path_radar}/512/3/3/3/1/0_0.png"
        img_res = requests.get(url_tile, timeout=10)
        if img_res.status_code == 200:
            return BytesIO(img_res.content)
    except Exception as e:
        print(f"Aviso: Radar no disponible ({e})")
    return None

buffer_radar = obtener_radar()

# 5. ENVIAR A TELEGRAM
def enviar_imagen_telegram(buffer_img, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    files = {"photo": ("imagen.png", buffer_img, "image/png")}
    data = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=data, files=files, timeout=20)
        print(f"Respuesta de Telegram (Status {res.status_code}): {res.text}")
        res.raise_for_status()
    except Exception as e:
        print(f"Error al enviar foto a Telegram: {e}")

# Envíos
enviar_imagen_telegram(buffer_dashboard, caption="☀️ <b>Reporte del Clima - San Pedro</b>")

if buffer_radar:
    enviar_imagen_telegram(buffer_radar, caption="🛰️ <b>Cobertura de Radar / Satélite en vivo</b>")