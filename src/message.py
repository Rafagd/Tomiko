class Message:
    def identify(metadata, update):
        if hasattr(update, 'document'):
            return DocumentMsg(metadata, update)
        return TextMsg(metadata, update)

    def __init__(self, metadata, update):
        raise NotImplementedError()

    def reply(self):
        raise NotImplementedError()

    def send(self):
        raise NotImplementedError()


class DocumentMsg(Message):
    def __init__(self, metadata, update):
        self.message = update.message


class TextMsg(Message):
    def __init__(self, metadata, update):
        self.message = update.message
