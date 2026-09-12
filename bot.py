import asyncio
import json
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeChat,
)


# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = "8772793059:AAEPQqgOCQiggh0FKnJreW6atVJv28rD2o4"

ADMIN_USERNAME = "skylinix"

DATA_FILE = "data.json"


# =========================
# ЗАГРУЗКА ДАННЫХ
# =========================

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
else:
    data = {}

data.setdefault("movies", [])
data.setdefault("support", [])
data.setdefault("admin_message_map", {})


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_admin(message: Message) -> bool:
    username = message.from_user.username

    if not username:
        return False

    return username.lower() == ADMIN_USERNAME.lower()


# =========================
# КОМАНДЫ
# =========================

USER_COMMANDS = [
    BotCommand(
        command="start",
        description="Запустить бота",
    ),
    BotCommand(
        command="suggmovie",
        description="Предложить фильм или сериал",
    ),
    BotCommand(
        command="supporthub",
        description="Написать в поддержку",
    ),
]

ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(
        command="suggsmovieslist",
        description="Список предложенных фильмов",
    ),
    BotCommand(
        command="supporthubmenu",
        description="Открыть обращения",
    ),
]


# =========================
# БОТ
# =========================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start_command(message: Message):
    text = (
        "👋 <b>Привет, киноман!</b>\n\n"
        "🎬 Это официальный бот <b>KINO HUB</b>.\n\n"
        "Здесь ты можешь:\n"
        "🎥 Предложить фильм или сериал\n"
        "🆘 Написать в поддержку\n"
        "💡 Сообщить о проблеме или предложить идею\n\n"
        "Используй команды из меню бота."
    )

    await message.answer(text, parse_mode="HTML")

    if is_admin(message):
        await bot.set_my_commands(
            ADMIN_COMMANDS,
            scope=BotCommandScopeChat(
                chat_id=message.from_user.id
            ),
        )


# =========================
# ПРЕДЛОЖЕНИЕ ФИЛЬМА
# =========================

@dp.message(Command("suggmovie"))
async def suggest_movie(message: Message):
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "🎬 <b>Введите название фильма!</b>\n\n"
            "Например:\n"
            "<code>/suggmovie Интерстеллар</code>",
            parse_mode="HTML",
        )
        return

    movie_name = parts[1].strip()

    if len(movie_name) < 3:
        await message.answer(
            "❌ Название должно содержать минимум "
            "<b>3 символа</b>.",
            parse_mode="HTML",
        )
        return

    data["movies"].append(
        {
            "title": movie_name,
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        }
    )

    save_data()

    await message.answer(
        f"✅ <b>Фильм предложен!</b>\n\n"
        f"🎬 {movie_name}\n\n"
        "Спасибо за предложение ❤️",
        parse_mode="HTML",
    )


# =========================
# ПОДДЕРЖКА
# =========================

@dp.message(Command("supporthub"))
async def support_hub(message: Message):
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "🆘 <b>Введите текст обращения!</b>\n\n"
            "Например:\n"
            "<code>/supporthub У меня не открывается фильм</code>",
            parse_mode="HTML",
        )
        return

    support_text = parts[1].strip()

    if len(support_text) < 10:
        await message.answer(
            "❌ Обращение должно содержать минимум "
            "<b>10 символов</b>.",
            parse_mode="HTML",
        )
        return

    data["support"].append(
        {
            "user_id": message.from_user.id,
            "text": support_text,
        }
    )

    save_data()

    await message.answer(
        "✅ <b>Ваше обращение отправлено в поддержку!</b>\n\n"
        "Ожидайте ответа администрации.",
        parse_mode="HTML",
    )


# =========================
# СПИСОК ФИЛЬМОВ
# =========================

@dp.message(Command("suggsmovieslist"))
async def movies_list(message: Message):
    if not is_admin(message):
        return

    movies = data["movies"]

    if not movies:
        await message.answer(
            "📭 Пока никто не предложил фильмов."
        )
        return

    text = "🎬 <b>Предложенные фильмы и сериалы:</b>\n\n"

    for i, movie in enumerate(movies, 1):
        text += f"{i}. {movie['title']}\n"

    await message.answer(
        text,
        parse_mode="HTML",
    )


# =========================
# МЕНЮ ПОДДЕРЖКИ
# =========================

@dp.message(Command("supporthubmenu"))
async def support_menu(message: Message):
    if not is_admin(message):
        return

    support = data["support"]

    if not support:
        await message.answer(
            "📭 Новых обращений нет."
        )
        return

    await message.answer(
        f"🆘 <b>Новых обращений: {len(support)}</b>\n\n"
        "Ответь на сообщение пользователя, чтобы отправить ему ответ.",
        parse_mode="HTML",
    )

    for item in support:
        try:
            sent_message = await bot.send_message(
                chat_id=message.from_user.id,
                text=(
                    "🆘 <b>Обращение пользователя:</b>\n\n"
                    f"{item['text']}"
                ),
                parse_mode="HTML",
            )

            data["admin_message_map"][
                str(sent_message.message_id)
            ] = {
                "user_id": item["user_id"],
                "support_text": item["text"],
            }

        except Exception as e:
            print(f"Ошибка отправки обращения: {e}")

    save_data()


# =========================
# ОТВЕТ АДМИНА
# =========================

@dp.message(F.reply_to_message)
async def admin_reply(message: Message):
    if not is_admin(message):
        return

    replied_message_id = message.reply_to_message.message_id
    key = str(replied_message_id)

    if key not in data["admin_message_map"]:
        return

    support_item = data["admin_message_map"][key]
    user_id = support_item["user_id"]

    answer_text = message.text

    if not answer_text:
        await message.answer(
            "❌ Ответ должен быть текстовым сообщением."
        )
        return

    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "🆘 <b>Ответ поддержки KINO HUB:</b>\n\n"
                f"{answer_text}"
            ),
            parse_mode="HTML",
        )

        data["support"] = [
            item
            for item in data["support"]
            if not (
                item["user_id"] == user_id
                and item["text"] == support_item["support_text"]
            )
        ]

        del data["admin_message_map"][key]

        save_data()

        await message.answer(
            "✅ Ответ отправлен пользователю анонимно."
        )

    except Exception as e:
        print(f"Ошибка ответа: {e}")

        await message.answer(
            "❌ Не удалось отправить ответ пользователю."
        )


# =========================
# ЗАПУСК
# =========================

async def main():
    await bot.set_my_commands(
        USER_COMMANDS,
        scope=BotCommandScopeDefault(),
    )

    print("KINO HUB Bot запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())