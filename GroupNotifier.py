from aiogram import Bot, types
from abc import ABC, abstractmethod

class GroupNotifier(ABC):

    @abstractmethod
    async def send_message_to_group(self, chat_id: int, location: dict, user: types.User) -> None:
        pass


class GroupMessageSender(GroupNotifier):

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message_to_group(self, chat_id: int, location: dict, user: types.User) -> None:
        try:
            latitude = location['latitude']
            longitude = location['longitude']

            await self.bot.send_message(
                chat_id=chat_id,
                text=f"Привет👋! Я ваш таксист @{user.username}, готов помочь вам с комфортной поездкой 🚕🌟.\n\nПожалуйста, отправьте мне свою Геолокацию из меню 📎, и я приеду к вам! С нетерпением жду возможности вам помочь с перемещением по городу.\nСпасибо за выбор нашего такси-сервиса, и до скорой встречи!😊",
            )

            # Send the location map to the group
            await self.bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)

            await self.bot.send_message(
                chat_id=user.id,
                text=f"Благодарим вас за предоставленное местоположение.\n\nМы успешно отправили его в группу {chat_id}. Если вы захотите обновить свою 📍геометку в этой группе, просто повторно отправьте свою Геолокацию."
            )
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error sending message to group: {e}")
