import asyncio
from transformers import pipeline

# Загружаем модель один раз при старте бота (может занять время при первом запуске)
# Если есть видеокарта NVIDIA, добавь параметр device=0 в pipeline
classifier = pipeline("text-classification", model="corall88/russian_spam_detector")

def _predict(text: str) -> bool:
    """Синхронная функция для работы нейросети"""
    # Обрезаем текст, так как у моделей BERT обычно лимит 512 токенов
    result = classifier(text[:1500])
    label = result[0]['label'].lower()
    
    # В зависимости от автора модели, класс спама может называться по-разному.
    # Чаще всего это 'spam', 'label_1' или '1'. 
    return "spam" in label or "label_1" in label or label == "1"

async def check_message_for_spam(text: str) -> dict:
    """Асинхронная обертка, которую ждет наш бот"""
    try:
        # Запускаем тяжелую ML-задачу в отдельном потоке, чтобы не блочить бота
        is_spam = await asyncio.to_thread(_predict, text)
        return {"is_spam": is_spam}
    except Exception as e:
        print(f"Ошибка модели: {e}")
        # При ошибке пропускаем сообщение
        return {"is_spam": False}