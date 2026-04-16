import asyncio
import logging
import sys
from config import BOT_TOKEN as TOKEN

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch
from aiogram.client.session.aiohttp import AiohttpSession

import Spotify_API


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

session = AiohttpSession(proxy='http://proxy.server:3128')

dp = Dispatcher()


@dp.message(CommandStart())
async def start_bot(message: Message) -> None:
    await message.answer(f"👋 Привет, {html.bold(message.from_user.full_name)}! 👋\n"
                         "👀 Я могу искать и скачивать музыку и видео 📩\n"
                         "🎞️ YouTube или Spotify 🎶\n"
                         "🎞️ Кидай название или тему того, что хочешь посмотреть или послушать!🎶\n"
                         "📺 Если видео с Youtube, то перед названием пиши 'yt'! 📺\n"
                         "📻 Если музыка со Spotify, то перед названием пиши 'sf' 📻")


@dp.message(lambda message: message.text.startswith("yt"))
async def handle_youtube_search(message: Message):
    search_query = message.text[len("yt "):]
    try:
        search_list = VideosSearch(search_query, limit=6).result()['result']
        keyboard = [[InlineKeyboardButton(text=element['title'], callback_data=element['link'])] for element in search_list]
        choose_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer("👀 Вот предложенные вам видео:\n", reply_markup=choose_markup)
    except Exception as e:
        await message.answer(f"Произошла ошибка при поиске видео: {e}")
        logging.error(f"Ошибка при поиске на YouTube: {e}")


@dp.callback_query()
async def callback_handler(query: CallbackQuery):
    download_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📥 Скачать видео можно тут 📥", url='https://ru.savefrom.net/')]])
    await query.message.answer(
        f"📺 Приятного просмотра:\n {query.data}\n"
        "Если хотите скачать видео, это можете сделать на этом сайте:",
        reply_markup=download_markup
    )
    await query.answer()


@dp.message(lambda message: message.text.startswith("sf"))
async def music_from_spotify(message: Message):
    query = message.text[len("sf "):]
    try:
        logging.info(f"Запрос к Spotify > {query}")
        tracks = Spotify_API.search_tracks(query)

        if tracks:
            response = "🎵 Найденные треки:\n\n"
            keyboard = []

            for track in tracks:
                track_name = track['name']
                artists = ', '.join([artist['name'] for artist in track['artists']])
                download_url = track['external_urls']['spotify']
                response += f"{html.bold(track_name)} by {html.italic(artists)}\n"

                keyboard.append([InlineKeyboardButton(text=f"Скачать {track_name}", url=download_url)])

            choose_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            await message.answer(response, reply_markup=choose_markup)
        else:
            await message.answer("Треки не найдены.")

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        logging.error(f"Ошибка Spotify API: {e}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
#    bot = Bot(token=TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
