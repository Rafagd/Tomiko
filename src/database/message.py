import telegram

class MessageTable:
    def __init__(self, database):
        self.database = database

    def create(self):
        cursor = self.database.cursor()
        cursor.execute('''
            CREATE TABLE messages(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                author_id INT NOT NULL,
                type INT NOT NULL,
                content TEXT NOT NULL,
                mind TEXT NOT NULL
            )
        ''')
        cursor.close()

    def insert(self, message):
        cursor = self.database.cursor()
        cursor.execute('''
            INSERT INTO messages(
                author_id, type, content, mind
            ) VALUES (
                ?, ?, ?, ?
            )''',
            [
                message.author_id(),
                message.type(),
                message.content(),
                message.mind()
            ]
        )
        self.database.commit()
        cursor.close()

    def search(self, word=None):
        cursor = self.database.cursor()
        if word != None:
            cursor.execute('''
                SELECT *
                FROM messages
                ORDER BY RANDOM()
                LIMIT 1
            ''')
        else:
            cursor.execute('''
                SELECT *
                FROM messages
                WHERE (content LIKE ?) OR (mind LIKE ?)
                ORDER BY RANDOM()
                LIMIT 1''',
                [ word, word ]
            )
        data = cursor.fetchone()
        cursor.close()
        return Message.factory(data)


class Message:
    def factory(data, mind=''):
        if isinstance(data, telegram.update.Update):
            try:
                return DocumentMessage(data.message.document.id,
                    author_id=data.message.from_user.id,
                    mind=mind
                )
            except:
                return TextMessage(data.message.text,
                    author_id=data.message.from_user.id,
                    mind=mind
                )
        else:
            author_id = int(data[1])
            msg_type  = int(data[2])
            content   = data[3]
            mind      = data[4]

            if msg_type == 0:
                return TextMessage(content, author_id=authod_id, mind=mind)
            elif msg_type == 1:
                return DocumentMessage(content, author_id=author_id, mind=mind)

        return NoMessage()

    def author_id(self):
        return self._author_id

    def type(self):
        return self._type

    def content(self):
        return self._content

    def mind(self):
        return self._mind

    def __repr__(self):
        return '{{ author_id: "{}", type: "{}", content: "{}", mind: "{}" }}'.format(
            self.author_id(),
            self.type(),
            self.content(),
            self.mind()
        )


class NoMessage(Message):
    def __init__(self):
        self._author_id = 0
        self._type      = 0
        self._content   = ''
        self._mind      = ''


class TextMessage(Message):
    def __init__(self, text, author_id=0, mind=""):
        self._author_id = author_id
        self._type      = 0
        self._content   = text
        self._mind      = mind
        

class DocumentMessage(Message):
    def __init__(self, document, author_id=0, mind=""):
        self._author_id = author_id
        self._type      = 1
        self._content   = document
        self._mind      = mind
        
