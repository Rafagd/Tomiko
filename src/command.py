from .database import *


def command(session, author, message):
    tokens    = message.tokens()
    command   = tokens[0].split('@')

    if command[0] == '/slap':
        return slap(session, author, tokens)
    return None


def slap(session, author, tokens):
    if author.user_name != '':
        actor = '@' + author.user_name
    else:
        actor = author.first_name

    try:
        target = tokens[1]
    except:
        target = '#schizo'

    obj = ' '.join(tokens[2:])

    if obj != '':
        new_slap           = Slap()
        new_slap.author_id = author.id
        new_slap.object    = obj
        session.merge(new_slap)

    else:
        obj = Slap.fetch_random(session).object

    message         = Message()
    message.type    = Message.TYPE_TEXT
    message.content = '*{} slaps {} around a bit with {}'.format(actor, target, obj)
    return message


