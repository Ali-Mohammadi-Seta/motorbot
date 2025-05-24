# bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import urllib.parse

ORS_API_KEY = "5b3ce3597851110001cf624817be512ab5bf4e009dbe0b1c0ba578d8"
BOT_TOKEN = "7669334877:AAE8itnRAdSlltCpmoYebpcfJEvU0aC8TGY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! مبدا و مقصد رو به شکل «میدان آزادی به تجریش» بنویس.")

async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "به" not in text:
        await update.message.reply_text("فرمت اشتباهه. لطفاً مثل «انقلاب به ونک» بنویس.")
        return

    origin, destination = [x.strip() for x in text.split("به")]

    def get_coords(place):
        url = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&text={urllib.parse.quote(place)}, تهران"
        res = requests.get(url).json()
        coords = res["features"][0]["geometry"]["coordinates"]
        return coords

    try:
        coords_from = get_coords(origin)
        coords_to = get_coords(destination)

        url = "https://api.openrouteservice.org/v2/directions/cycling-regular"
        body = {
            "coordinates": [coords_from, coords_to],
            "instructions": False,
            "options": {"avoid_features": ["highways"]},
        }
        headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
        res = requests.post(url, json=body, headers=headers).json()

        if "features" in res:
            coords = res["features"][0]["geometry"]["coordinates"]
            maps_url = f"https://www.openstreetmap.org/directions?engine=graphhopper_bicycle&route={coords_from[1]},{coords_from[0]};{coords_to[1]},{coords_to[0]}"
            await update.message.reply_text(f"✅ مسیر پیشنهادی:\n{maps_url}")
        else:
            await update.message.reply_text("❌ نتونستم مسیر پیدا کنم.")

    except Exception as e:
        await update.message.reply_text("خطا در پردازش مسیر. لطفاً دوباره امتحان کن.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_handler))
app.run_polling()
