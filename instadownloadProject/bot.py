from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import instaloader
import re
import requests
from io import BytesIO

# Инициализация Instaloader
loader = instaloader.Instaloader()

# Функция извлечения shortcode из ссылки
def extract_shortcode(url: str) -> str:
    match = re.search(r"(p|reel|tv)/([A-Za-z0-9_-]+)", url)
    if match:
        return match.group(2)
    else:
        return url.rstrip("/").split("/")[-1]

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Отправь мне ссылку на видео из Instagram, и я помогу тебе его скачать."
    )

# Обработчик текстовых сообщений
def download_video(update: Update, context: CallbackContext):
    url = update.message.text.strip()

    if "instagram.com" not in url:
        update.message.reply_text("Пожалуйста, отправь корректную ссылку на Instagram-видео.")
        return

    try:
        # Извлечение shortcode
        shortcode = extract_shortcode(url)
        if not shortcode:
            update.message.reply_text("Не удалось извлечь код из ссылки. Проверьте формат ссылки.")
            return

        # Получение поста Instagram
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Получение прямой ссылки на видео
        video_url = post.video_url
        if not video_url:
            update.message.reply_text("Не удалось найти видео в этом посте. Проверьте ссылку.")
            return

        # Скачивание видео в память
        response = requests.get(video_url)
        if response.status_code != 200:
            update.message.reply_text("Ошибка при скачивании видео.")
            return

        video_data = BytesIO(response.content)

        # Отправка видео в Telegram
        update.message.reply_video(video=video_data, caption="Вот ваше видео!")

    except instaloader.exceptions.InstaloaderException as e:
        update.message.reply_text(f"Ошибка при скачивании: {str(e)}")
    except Exception as e:
        update.message.reply_text(f"Произошла ошибка: {str(e)}")

# Обработчик ошибок
def error(update: Update, context: CallbackContext):
    print(f"Ошибка {context.error}")

def main():
    TOKEN = '6421291124:AAGANEJYvOBpJeXH8dSxiNhDOApKHU7mIVg'

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
