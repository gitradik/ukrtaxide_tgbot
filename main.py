import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
TOKEN = os.getenv('TG_BOT_TOKEN')
WEBHOOK = os.getenv('TG_WEBHOOK')
CHAT_ID = os.getenv('TG_CHAT_ID')
HOST = os.getenv('HOST')
PORT = int(os.environ.get('PORT', 80))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Global dictionary to store user locations
user_locations = {}

async def start(message: types.Message) -> None:
    user = message.from_user
    await message.reply(fr"Привет, {user.mention}! Если вы планируете предоставлять услуги такси, пожалуйста, отправьте нам свою Геолокацию из меню 📎.")
# Create a set to store user IDs who have already pressed the button
users_pressed_button = {}

async def handle_location(message: types.Message) -> None:
    user = message.from_user
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        users_pressed_button[user.id] = 0
            
        # Save the location in the global dictionary using user_id as the key
        user_locations[user.id] = {'latitude': latitude, 'longitude': longitude}
        
        keyboard_free = InlineKeyboardMarkup().add(InlineKeyboardButton("Свободен", callback_data="free"))


        await message.reply(
            f"Привет, {user.mention}! Если у вас есть возможность начать работать, пожалуйста, нажмите на кнопку [Свободен] ниже, чтобы поделиться своей Геолокацией. \n\n Так мы сможем отправить вашу геометку📍 в нужную группу, чтобы люди могли воспользоваться вашим такси-сервисом. \n Спасибо за вашу готовность помочь! 🚕🌟",
            reply_markup=keyboard_free,
        )
    else:
        await message.reply(f"Простите, {user.mention}, но мы не можем получить доступ к вашему местоположению.\n\n Пожалуйста, свяжитесь с администратором чата @ramal_softdev для помощи. Будем ждать вашего обращения и надеемся, что сможем предоставить вам нашу услугу такси в ближайшее время. \n Спасибо за понимание! 🚕🌟😊")

async def free_btn(query: types.CallbackQuery) -> None:
    await query.answer()
    user = query.from_user

    users_pressed_button[user.id] += 1

    # Check if the user has already pressed the button
    if users_pressed_button[user.id] > 1:
        await query.message.reply("Вы уже нажали кнопку [Свободен]. Если хотите обновить геометку📍, просто отправьте свою Геолокацию ещё раз.")
        return

    # Get the user's location from the global dictionary using user_id as the key
    location = user_locations.get(user.id)

    if location:
        latitude = location['latitude']
        longitude = location['longitude']

        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"Привет👋! Я ваш таксист {user.mention}, готов помочь вам с комфортной поездкой 🚕🌟.\n\nПожалуйста, отправьте мне свою Геолокацию из меню 📎, и я приеду к вам! С нетерпением жду возможности вам помочь с перемещением по городу.\nСпасибо за выбор нашего такси-сервиса, и до скорой встречи!😊",
        )

        # Send the location map to the group
        await bot.send_location(chat_id=CHAT_ID, latitude=latitude, longitude=longitude)

        await query.message.reply(f"Благодарим вас за предоставленное местоположение.\n\nМы успешно отправили его в группу {CHAT_ID}. Если вы захотите обновить свою геометку📍 в этой группе, просто повторно отправьте свою Геолокацию.")
    else:
        await query.message.reply(f"Простите, {user.mention}, но мы не получили вашего местоположения.\n\nПожалуйста, попробуйте отправить его ещё раз. Если у вас возникнут какие-либо проблемы, вы также можете написать администратору чата @ramal_softdev для помощи.\nМы с нетерпением ждем вашего запроса и готовы предоставить вам отличный сервис! 🚕🌟😊")

async def on_startup(dp):
    # Set up webhook
    await bot.delete_webhook()
    await bot.set_webhook(url=WEBHOOK)  # Replace with your Heroku app URL


def main():
    # Add handler for the start command
    dp.register_message_handler(start, commands=["start"])

    # Add handler for the location message
    dp.register_message_handler(handle_location, content_types=types.ContentTypes.LOCATION)

    # Add handler for the "Свободен" button
    dp.register_callback_query_handler(free_btn, text="free")

    # Start the webhook
    executor.start_webhook(
        dispatcher=dp,
        webhook_path="/",
        on_startup=on_startup,
        skip_updates=True,
        host=HOST,
        port=PORT,
    )

if __name__ == "__main__":
    main()
