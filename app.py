from flask import Flask
from api.telegram import telegram_bp

app = Flask(__name__)
app.register_blueprint(telegram_bp)

@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return "OK", 200

# Necesario para Vercel
handler = app
