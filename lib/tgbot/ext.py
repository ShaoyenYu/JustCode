import logging
from typing import Optional, Union

from telegram import MessageEntity, Update
from telegram.ext import filters, UpdateFilter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class ValidUserFilter(UpdateFilter):
    def __init__(self, valid_users):
        self.valid_users = set(valid_users)

    def filter(self, update: Update) -> Optional[Union[bool, filters.DataDict]]:
        print("=" * 64)
        print(update.message.chat_id, update.message.from_user.id, update.message.from_user.name)
        print(update.message.text)
        print("=" * 64)
        return update.message.from_user.id in self.valid_users


class TextBuilder:
    def __init__(self, left_align=10):
        self.text = ""
        self.entities = []
        self.left_align = left_align

    def _handle_entity(self, **kwargs):
        self.entities.append(
            MessageEntity(**{
                k: v for k in ("type", "url", "language", "offset", "length") if (v := kwargs.get(k)) is not None
            })
        )

    def add(self, text, type_=None, url=None, language=None, newline=True):
        if newline:
            text += "\n"
        self.text += text

        offset = len(self.text) - len(text)

        self._handle_entity(type=type_, url=url, language=language, offset=offset, length=len(text))
