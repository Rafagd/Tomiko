from .database import *


def command(bot, session, author, message):
    tokens  = message.tokens()
    command = tokens[0].split('@')

    try:
        if command[1] != bot.metadata.username:
            return None
    except:
        pass

    if command[0] == '/slap':
        return slap(session, author, tokens)

    elif command[0] == '/mind':
        return mind(bot)

    elif command[0] == '/explain':
        return explain(bot)

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


def mind(bot):
    mind = []
    for word, ttl in bot.mind.data.items():
        mind.append((ttl, word))
    mind.sort(key=lambda item: item[0], reverse=True)

    if len(mind) == 0:
        content = 'Calma aí, acabei de acordar!'

    else:
        content = 'TTL\tWORD\n'
        for (ttl, word) in mind:
            content += '{:02d}\t{}\n'.format(ttl, word)

    message         = Message()
    message.type    = Message.TYPE_TEXT
    message.content = content
    return message


explain_kw = {
    'mentions_me':   lambda stack: 'Me chamaram',
    'random_answer': lambda stack: 'Tava lendo o chat',

    'from_mind':     lambda stack: 'estava pensando em "{}"'.format(stack.pop()),
    'from_text':     lambda stack: 'falaram isso: "{}"'.format(stack.pop()),

    'response_mind':     lambda stack: 'respondi o que estava pensando "{}"'.format(explain_kw[stack.pop()]),
    'response_random':   lambda stack: 'respondi qualquer coisa',
    'response_document': lambda stack: 'quis enviar uma imagem',
    'response_sticker':  lambda stack: 'achei que um sticker ia ser engraçado',
    'response_text':     lambda stack: 'mandei um texto',

    'fetch_document': lambda stack: 'procurei por algo com "{}"'.format(stack.pop()),
    'fetch_sticker':  lambda stack: 'tentei achar um relacionado com "{}"'.format(stack.pop()),
    'fetch_word':     lambda stack: 'usei a palavra "{}"'.format(stack.pop()),

    'random_document': lambda stack: 'não achei. Aí enviei qualquer coisa',
    'random_sticker':  lambda stack: 'não tinha. Mandei o primeiro que eu vi',
    'random_word':     lambda stack: 'não sabia nada sobre isso. Acabei falando qualquer merda aí',

    'period':      lambda stack: 'tranquilamente',
    'exclamation': lambda stack: 'excitada',
    'question':    lambda stack: 'intrigada',

    'nothing': lambda stack: 'Nem falei nada.',
    'error':   lambda stack: 'TELEGRAM ERROR: {}'.format(stack.pop),
}

def explain(bot):
    try:
        stack = bot.last_response.why
    except:
        stack = [ 'nothing' ]
    segments = []

    try:
        while True:
            index = stack.pop()

            try:
                func = explain_kw[index]
            except:
                # Keyword not found, just dump the stack as text.
                segments.append('EXPLAIN STACK ERROR: ' + index)
                while True:
                    segments.append(stack.pop())
            
            segments.append(func(stack))
    except:
        pass
    
    last = segments.pop()
    rest = ', '.join(segments)

    if rest == '':
        response = last + '.'
    else:
        response = rest + ' e ' + last + '.'

    message         = Message()
    message.type    = Message.TYPE_TEXT
    message.content = response
    return message


