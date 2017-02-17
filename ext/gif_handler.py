from telegram.ext import Handler
from telegram     import Update
from telegram.ext import Handler

class GifHandler(Handler):
    def __init__(self, command, callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(GifHandler, self).__init__(callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)


    def check_update(self, update):
        res = False
        if isinstance(update, Update):
            try:
                mime_type = update.message.document.mime_type
            except:
                mime_type = ""

            if mime_type == "video/mp4":
                res = update
        return res


    def handle_update(self, update, dispatcher):
        optional_args = {}
        return self.callback(dispatcher.bot, update, **optional_args)
