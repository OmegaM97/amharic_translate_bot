# bot.py
from fastapi import FastAPI, Request
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize FastAPI
app = FastAPI()

# Initialize Groq client
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

def translate_to_amharic(text: str) -> str:
    """
    Translate input text to Amharic using Groq OpenAI client
    """
    prompt = f"Translate the following text to Amharic:\n\n{text}"
    
    response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt,
    )
    
    return response.output_text

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
            translated = translate_to_amharic(text)
            send_telegram_message(chat_id, translated)
    
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)