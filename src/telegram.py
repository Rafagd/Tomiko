import os
import signal

from telegram.error import NetworkError
from telegram.ext   import Handler

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
        print(update)
        optional_args = {}
        return self.callback(dispatcher.bot, update, **optional_args)

