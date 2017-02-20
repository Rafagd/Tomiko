from log import Message

class NoReply:
    def __init__(self):
        self.message   = ""
        self.quote_msg = False
        pass

    def send(self, update):
        pass


class MessageReply:
    def __init__(self, message):
        self.message   = message
        self.quote_msg = False

    def send(self, update):
        target  = update.message.from_user.first_name
        message = self.message.text.format(nome=target)
        update.message.reply_text(message, quote=self.quote_msg)


class GifReply:
    def __init__(self, message):
        parts          = message.text.split("\t")
        self.file_id   = parts[0] if len(parts) > 0 else ""
        self.message   = Message("\t".join(parts[1:]) if len(parts) > 1 else "", message.offset)
        self.quote_msg = False

    def send(self, update):
        update.message.reply_document(self.file_id, quote=self.quote_msg)

