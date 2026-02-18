import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import Groq

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "ВАШ_ТОКЕН_БОТА"  # Вставь токен от @BotFather
GROQ_API_KEY = "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"
MODEL = "llama-3.3-70b-versatile"  # Можно изменить модель
# =================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY)

# История сообщений для каждого пользователя
user_histories = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer(
        "Привет! Я AI-бот на базе Groq. Напиши мне что-нибудь!"
    )

@dp.message(Command("clear"))
async def clear(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer("История очищена!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    # Инициализируем историю если её нет
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    # Добавляем сообщение пользователя в историю
    user_histories[user_id].append({
        "role": "user",
        "content": message.text
    })
    
    # Показываем что бот печатает
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Запрос к Groq
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Ты полезный AI-ассистент. Отвечай на русском языке, если тебя спрашивают на русском."},
                *user_histories[user_id]
            ],
            max_tokens=1024,
        )
        
        reply = response.choices[0].message.content
        
        # Добавляем ответ в историю
        user_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })
        
        # Ограничиваем историю (последние 20 сообщений)
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
