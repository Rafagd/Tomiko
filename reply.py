from log import Message

class NoReply:
    def __init__(self):
        pass

    def set_target(self, target):
        pass

    def send(self, api, chat):
        pass


class MessageReply:
    def __init__(self, message):
        self.message = isinstance(message, Message) and message
        self.target  = ""

    def set_target(self, target):
        self.target = target

    def send(self, api, chat):
        api.send_message(
            chat_id = chat,
            text    = self.message.text.format(nome=self.target)
        )


class GifReply:
    def __init__(self, message):
        message = isinstance(message, Message) and message
        parts   = message.text.split("\t")
        try:
            self.file_id = parts[0]
        except:
            self.file_id = ""
        try:
            self.message = Message("\t".join(part[1:]), message.offset)
        except:
            self.message = Message("", message.offset)

    def set_target(self, target):
        pass

    def send(self, api, chat):
        api.send_document(chat_id=chat, document=self.file_id)

