import json

class MessageManager:
    def __init__(self, file_path='assets/user_notification_messages.json'):
        self.file_path = file_path
        self.messages = self.load_messages()

    def load_messages(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_message(self, key, lang, **kwargs):
        message_text = self.messages.get(key, {}).get(lang, "Message not found for the given language")
        return message_text.format(**kwargs)