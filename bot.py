import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "ВАШ_ТОКЕН_БОТА")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "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")
GROQ_URL       = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL     = "llama-3.3-70b-versatile"
# =================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

user_histories = {}

def ask_groq(messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

@dp.message(Command("start"))
async def start(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer("Привет! Я AI-бот. Напиши мне что-нибудь!")

@dp.message(Command("clear"))
async def clear(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer("История очищена!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({
        "role": "user",
        "content": message.text
    })

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        messages = [
            {"role": "system", "content": "Ты полезный AI-ассистент. Отвечай на русском языке, если тебя спрашивают на русском."},
            *user_histories[user_id]
        ]

        reply = ask_groq(messages)

        user_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })

        if len(user_histories[user_id]) > 20:
            user_histories[user_id] = user_histories[user_id][-20:]

        await message.answer(reply)

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
