import asyncio
from services import check_message_for_spam

async def main():
    # Набор тестовых сообщений (нормальные и типичный спам)
    test_messages = [
        "Есть работа на лето , , График свободный .Платим 16 800 в день. ЛС https://t.me/Filtr_colin",
        "Привет, нужна помощь, оптишите в лс, заплачу 20 тысяч, -https://t.me/m/RZTEPYInYWE6",
        "Приветствую! Подойдёт ли вам продвижение в Telegram и MAX для вашего бренда, чтобы увеличить охваты?https://dinokays.fun/0dc26670bff1c4b7fa3d4ac774c550b5",
        "Всем привет, крутой контент",
    ]

    print("Запуск тестирования...\n")
    
    for i, text in enumerate(test_messages, 1):
        print(f"[{i}] Проверка текста: {text}")
        
        # Вызываем нашу функцию
        result = await check_message_for_spam(text)
        is_spam = result.get("is_spam")
        
        # Красивый вывод результата
        status = "🔴 СПАМ" if is_spam else "🟢 НОРМАЛЬНО"
        print(f"Вердикт: {status}\n")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())