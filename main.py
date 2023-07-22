import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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


def main():
    # Add handler for the start command
    dp.register_message_handler(start, commands=["start"])

    # Add handler for the location message
    dp.register_message_handler(handle_location, content_types=types.ContentTypes.LOCATION)

    # Add handler for the "Свободен" button
    dp.register_callback_query_handler(free_btn, text="free")

    # Start the bot
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()



# async def start(message: types.Message) -> None:
#     user = message.from_user
#     keyboard_location_access = InlineKeyboardMarkup().add(InlineKeyboardButton("Дать доступ к моему местоположению", callback_data="location_access"))
#     await message.reply(
#         fr"Привет, {user.mention}!",
#         reply_markup=keyboard_location_access,
#     )


# async def location_permission_callback(query: types.CallbackQuery) -> None:
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     keyboard.add(types.KeyboardButton("Дать доступ", request_location=True))
#     await query.message.reply(
#         "Пожалуйста, нажмите \"Дать доступ\" и разрешите доступ к вашему местоположению.",
#         reply_markup=keyboard,
#     )


# async def location_access_btn(query: types.CallbackQuery) -> None:
#     await location_permission_callback(query)
#     return await bot.send_message(
#         chat_id=query.message.chat.id,
#         text="Пожалуйста, нажмите \"Свободен\" если вы свободны.",
#         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Свободен", callback_data="free")),
#     )


# async def free_btn(query: types.CallbackQuery) -> None:
#     try:
#         await query.answer()
#         user = query.from_user
#         await bot.send_message(
#             chat_id="@UKRTaxiBremenGroup",  # Replace with the name or ID of your group
#             text=f"{user.mention} свободен(а)!",
#         )

#         # Check if the location exists before sending it to the group
#         if query.message.location:
#             await bot.send_location(
#                 chat_id="@UKRTaxiBremenGroup",  # Replace with the name or ID of your group
#                 latitude=query.message.location.latitude,
#                 longitude=query.message.location.longitude,
#             )
#         else:
#             # Handle the case when the location is not available
#             await bot.send_message(
#                 chat_id="@UKRTaxiBremenGroup",  # Replace with the name or ID of your group
#                 text="Извините, местоположение не доступно.",
#             )
#     except Exception as e:
#         # Handle the exception (e.g., log the error, notify the admin, etc.)
#         print(f"An error occurred while handling free_btn: {e}")


# def main():
#     # Add handlers for commands and actions
#     dp.register_message_handler(start, commands=["start"])
#     dp.register_callback_query_handler(location_access_btn, text="location_access")
#     dp.register_callback_query_handler(free_btn, text="free")

#     # Start the bot
#     executor.start_polling(dp, skip_updates=True)


# if __name__ == "__main__":
#     main()

