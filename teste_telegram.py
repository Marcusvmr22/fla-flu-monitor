import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

resposta = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "🧪 TESTE DO MONITOR FLAMENGO x FLUMINENSE\n\nSe você recebeu esta mensagem, o Telegram está funcionando corretamente."
    },
    timeout=20
)

print("Status:", resposta.status_code)
print("Resposta:", resposta.text)

if resposta.ok:
    print("📲 Telegram funcionando!")
else:
    print("❌ Falha no Telegram.")
