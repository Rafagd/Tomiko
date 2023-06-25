import os
import signal

from telegram       import Update
from telegram.error import NetworkError
from telegram.ext   import Handler

from .database import Message, Author



class UpdateHandler(Handler):
    def __init__(self, metadata, callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        
        super(UpdateHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data
        )

        self.metadata = metadata


    def check_update(self, update):
        # I'm not dealing with edited messages. Just ignore all.
        return update.edited_message == None


    def error_handler(self, api, update, error):
        optional_args = { 'error': error }
        return self.callback(dispatcher.bot, update, **optional_args)


    def handle_update(self, update, dispatcher):
        optional_args = {}
        return self.callback(dispatcher.bot, update, **optional_args)



def read_author(update, session):
    if not isinstance(update, Update):
        raise TypeError('Argument must be instance of telegram.Update')

    try:
        return Author.fetch(session, update.message.from_user.id)

    except:
        pass

    try:
        author = Author(
            id         = update.message.from_user.id,
            first_name = update.message.from_user.first_name,
            last_name  = update.message.from_user.last_name,
            user_name  = update.message.from_user.username,
        )

        session.add(author)
        return author

    except:
        print(update)
        raise


def read_message(update, error = None):
    if not isinstance(update, Update):
        raise TypeError('Argument must be instance of telegram.Update')

    message           = Message()
    message.author_id = update.message.from_user.id

    if error != None:
        message.type    = Message.TYPE_ERROR
        message.content = str(error)
        return message

    try:
        message.content = update.message.document.file_id
        message.type    = Message.TYPE_DOCUMENT
        return message
    except:
        pass

    try:
        message.content = update.message.sticker.file_id
        message.type    = Message.TYPE_STICKER
        return message
    except:
        pass

    if len(update.message.text) > 0 and update.message.text[0] == '/':
        message.type = Message.TYPE_COMMAND
    else:
        message.type = Message.TYPE_TEXT

    message.content = update.message.text
    return message



def send(update, response, with_quote=False):
    if response.type == Message.TYPE_TEXT:
        update.message.reply_text(response.content, quote=with_quote)

    elif response.type == Message.TYPE_DOCUMENT:
        update.message.reply_document(response.content, quote=with_quote)

    elif response.type == Message.TYPE_STICKER:
        update.message.reply_sticker(response.content, quote=with_quote)

    else:
        update.message.reply_text('Tipo desconhecido: {}'.format(response))



