import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.webhook import get_new_configured_app

load_dotenv()
TOKEN = os.getenv('TG_BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Global dictionary to store user locations
user_locations = {}


async def start(message: types.Message) -> None:
    user = message.from_user
    await message.reply(fr"Привет, {user.mention}! Пожалуйста, отправьте своё местоположение.")


async def handle_location(message: types.Message) -> None:
    user = message.from_user
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        # Save the location in the global dictionary using user_id as the key
        user_locations[user.id] = {'latitude': latitude, 'longitude': longitude}
        
        keyboard_free = InlineKeyboardMarkup().add(InlineKeyboardButton("Свободен", callback_data="free"))
        await message.reply(
            f"{user.mention}, eсли вы свободны, нажмите кнопку [Свободен].",
            reply_markup=keyboard_free,
        )
    else:
        await message.reply(f"Извините, {user.mention}, но местоположение не доступно.")


async def free_btn(query: types.CallbackQuery) -> None:
    await query.answer()
    user = query.from_user

    # Get the user's location from the global dictionary using user_id as the key
    location = user_locations.get(user.id)

    if location:
        latitude = location['latitude']
        longitude = location['longitude']

        await bot.send_message(
            chat_id="@UKRTaxiBremenGroup",  # Replace with the name or ID of your group
            text=f"{user.mention} свободен(а)!",
        )

        # Send the location map to the group
        await bot.send_location(chat_id="@UKRTaxiBremenGroup", latitude=latitude, longitude=longitude)
        await query.message.reply(f"{user.mention}, спасибо за предоставленное местоположение. Мы отправили его в группу @UKRTaxiBremenGroup.")
        aa = await bot.send_message(
            chat_id=query.message.chat.id,
            text=f"Пожалуйста, отправьте своё местоположение, если вы считаете, что оно значительно поменялось."
        )
        print(aa)
    else:
        await bot.send_message(
            chat_id=query.message.chat.id,
            text=f"Извините, {user.mention}, но ваше местоположение не было предоставлено.",
        )

async def on_startup(dp):
    # Set up webhook
    await bot.delete_webhook()
    await bot.set_webhook(url="https://ukrtaxidetgbot-ac1c3a901204.herokuapp.com/")  # Replace with your Heroku app URL


def main():
    # Add handler for the start command
    dp.register_message_handler(start, commands=["start"])

    # Add handler for the location message
    dp.register_message_handler(handle_location, content_types=types.ContentTypes.LOCATION)

    # Add handler for the "Свободен" button
    dp.register_callback_query_handler(free_btn, text="free")

    # Get the app with configured webhook
    app = get_new_configured_app(dp)

    # Start the webhook
    executor.start_webhook(
        dispatcher=dp,
        webhook_path="/",
        on_startup=on_startup,
        skip_updates=True
    )

if __name__ == "__main__":
    main()
