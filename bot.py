from fastapi import FastAPI, Request
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

def translate_to_amharic(text: str) -> str:
    """
    Translate input text to Amharic using Groq OpenAI client.
    Strictly translation only, no explanations, no extra text.
    """
    prompt = f"""
You are a strict translator. ONLY translate the input text to Amharic.
Do NOT add explanations, summaries, or anything else.
Input text: {text}
"""
    response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt,
    )
    return response.output_text.strip()

def send_telegram_message(chat_id: int, text: str):
    """
    Send message to Telegram chat
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.post(f"/webhook/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    """
    Telegram webhook to receive messages
    """
    data = await request.json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text:
            if text.startswith("/"):
                if text.strip().lower() == "/start":
                    welcome_message = (
                        "👋 Welcome to the Amharic Translator Bot!\n\n"
                        "I can translate any text you send into Amharic. "
                        "Just type your message in any language, and I will give you a clean translation in Amharic.\n\n"
                        "Currently, only text translation is supported."
                    )
                    send_telegram_message(chat_id, welcome_message)
                else:
                    send_telegram_message(chat_id, "⚠️ We are not handling that command yet. Feature coming soon.")
            else:
                translated = translate_to_amharic(text)
                send_telegram_message(chat_id, translated)
    
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)