import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from GroupNotifier import GroupMessageSender
from MessageManager import MessageManager

load_dotenv()
TOKEN = os.getenv('TG_BOT_TOKEN')
WEBHOOK = os.getenv('TG_WEBHOOK')
CHAT_ID = os.getenv('TG_CHAT_ID')
HOST = os.getenv('HOST')
PORT = int(os.environ.get('PORT', 80))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Global MessageManager
message_manager = MessageManager()
# Global dictionary to store user locations
user_locations = {}    
# Create a map to store user IDs who have already pressed the button
users_pressed_button = set()
users_pressed_confirmation_button = set()

@dp.callback_query_handler(lambda query: query.data == 'confirm_yes')
async def handle_confirm_yes(query: types.CallbackQuery) -> None:
    await query.answer()
    user = query.from_user

    # Check if the user has already pressed the button
    if user.id in users_pressed_confirmation_button:
        await query.message.reply(message_manager.get_message('already_pressed_free_button', 'ua'))
        return
    
    users_pressed_confirmation_button.add(user.id)

    # Get the user's location from the global dictionary using user_id as the key
    location = user_locations.get(user.id)

    message_sender = GroupMessageSender(bot)
    await message_sender.send_message_to_group(CHAT_ID, location, user)

@dp.callback_query_handler(lambda query: query.data == 'confirm_no')
async def handle_confirm_no(query: types.CallbackQuery) -> None:
    await query.answer()
    user = query.from_user

    await query.message.reply(message_manager.get_message('confirm_continue_no', 'ua'))
    
    users_pressed_confirmation_button.add(user.id)

@dp.callback_query_handler(lambda query: query.data == 'free')
async def handle_free_button(query: types.CallbackQuery) -> None:
    try:
        await query.answer()
        user = query.from_user
        
        # Check if the user not have @username and haven't received the reminder message yet
        if user.username is None:
            await query.message.reply(message_manager.get_message('username_important', 'ua'))
            return

        # Check if the user has already pressed the button
        if user.id in users_pressed_button:
            await query.message.reply(message_manager.get_message('already_pressed_free_button', 'ua'))
            return
        
        users_pressed_button.add(user.id)
        
         # Create an InlineKeyboardMarkup with "Да" (Yes) and "Нет" (No) buttons
        confirm_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(message_manager.get_message('confirm_yes', 'ua'), callback_data="confirm_yes"),
            InlineKeyboardButton(message_manager.get_message('confirm_no', 'ua'), callback_data="confirm_no")
        )

        await query.message.reply(message_manager.get_message('confirm_continue', 'ua'), reply_markup=confirm_keyboard)
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error handling callback query in handle_free_button: {e}")

@dp.message_handler(content_types=types.ContentTypes.LOCATION)
async def handle_location(message: types.Message) -> None:
    user = message.from_user
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        if user.id in users_pressed_button:
            users_pressed_button.remove(user.id)
        if user.id in users_pressed_confirmation_button:
            users_pressed_confirmation_button.remove(user.id)
            
        # Save the location in the global dictionary using user_id as the key
        user_locations[user.id] = {'latitude': latitude, 'longitude': longitude}
        
        keyboard_free = InlineKeyboardMarkup().add(InlineKeyboardButton(
            message_manager.get_message('free', 'ua', user_mention=f"{user.mention}"),
            callback_data="free")
        )
 
        await message.reply(
            message_manager.get_message('start_working', 'ua', user_mention=f"{user.mention}"),
            reply_markup=keyboard_free
        )
    else:
        await message.reply(message_manager.get_message('no_access_location', 'ua', user_mention=f"{user.mention}"))

# Add handler for the start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    user = message.from_user

    await message.reply(message_manager.get_message('start', 'ua', user_mention=f"{user.mention}"))

async def on_startup(dp):
    # Set up webhook
    await bot.delete_webhook()
    # Replace with your Heroku app URL
    await bot.set_webhook(url=WEBHOOK)

if __name__ == "__main__":
    # For localhost
    # executor.start_polling(dispatcher=dp, skip_updates=True)
    # Start the webhook
    executor.start_webhook(
        dispatcher=dp,
        webhook_path="/",
        on_startup=on_startup,
        skip_updates=True,
        host=HOST,
        port=PORT,
    )
