from aiogram import Bot, types
from abc import ABC, abstractmethod

from MessageManager import MessageManager

class GroupNotifier(ABC):

    @abstractmethod
    async def send_message_to_group(self, chat_id: int, location: dict, user: types.User) -> None:
        pass


class GroupMessageSender(GroupNotifier):
    message_manager = MessageManager()

    def __init__(self, bot: Bot, users_group: dict):
        self.bot = bot
        self.users_group = users_group  # Store users_group as an instance variable

    async def send_message_to_group(self, location: dict, user: types.User) -> None:
        try:
            latitude = location['latitude']
            longitude = location['longitude']
            
            # Get the chat_id for the user from the users_group dictionary
            chat_id = self.users_group.get(user.id)

            if chat_id:
                # Send the message to the group
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=self.message_manager.get_message('driver_in_group', 'ua', username=user.username)
                )
                # Send the location map to the group
                await self.bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)

                # Send the message to chat bot
                await self.bot.send_message(
                    chat_id=user.id,
                    text=self.message_manager.get_message('thanks_for_location', 'ua', chat_id=chat_id)
                )
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error sending message to group: {e}")
