import json

class LangEnum:
    EN = 'en'
    RU = 'ru'
    UA = 'ua'

class MessageManager:
    def __init__(self, file_path='assets/user_notification_messages.json'):
        self.file_path = file_path
        self.messages = self.load_messages()
        self.lang = LangEnum.UA

    def change_lang(self, lang):
        if lang in [LangEnum.EN, LangEnum.RU, LangEnum.UA]:
            self.lang = lang
        else:
            raise ValueError("Invalid language. Supported languages are 'en', 'ru', and 'ua'.")

    def load_messages(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_message(self, key, **kwargs):
        message_text = self.messages.get(key, {}).get(self.lang, "Message not found for the given language")
        return message_text.format(**kwargs)