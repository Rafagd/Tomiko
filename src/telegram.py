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
        return True


    def error_handler(self, api, update, error):
        try:
            raise error
        except NetworkError as e:
            if '(409)' in e.message:
                os.kill(os.getpid(), signal.SIGINT)
                return
        # Printing unknown errors.
        print("ERROR:", api, update, error)


    def handle_update(self, update, dispatcher):
        optional_args = {}
        return self.callback(dispatcher.bot, update, **optional_args)


def read_author(update):
    if not isinstance(update, Update):
        raise TypeError('Argument must be instance of telegram.Update')

    return Author(
        id         = update.message.from_user.id,
        first_name = update.message.from_user.first_name,
        last_name  = update.message.from_user.last_name,
        user_name  = update.message.from_user.username,
    )


def read_message(update):
    if not isinstance(update, Update):
        raise TypeError('Argument must be instance of telegram.Update')

    message = Message()

    try:
        message.type    = Message.TYPE_DOCUMENT
        message.content = update.message.document.file_id

    except:
        message.content = update.message.text

        if message.content[0] == '/':
            message.type = Message.TYPE_COMMAND
        else:
            message.type = Message.TYPE_TEXT

    return message


def send(update, response, with_quote=False):
    if response.type == Message.TYPE_TEXT:
        update.message.reply_text(response.content, quote=with_quote)

    elif response.type == Message.TYPE_DOCUMENT:
        update.message.reply_document(response.content, quote=with_quote)

    else:
        update.message.reply_text('Tipo desconhecido: {}'.format(response))
    
