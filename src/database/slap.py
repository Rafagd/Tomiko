class SlapTable:
    def __init__(self, database):
        self.database = database

    def create(self):
        cursor = self.database.cursor()
        cursor.execute('''
	    CREATE TABLE slaps(
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		author_id INT NOT NULL,
		object TEXT NOT NULL UNIQUE,
		mind TEXT NOT NULL
	    )
        ''')
        cursor.close()

    def insert(self, slap):
        cursor = self.database.cursor()
        cursor.execute('''
            INSERT INTO slaps(
                author_id, object, mind
            ) VALUES (
                ?, ?, ?
            )''',
            [ 
                slap.author_id(),
                slap.object(),
                slap.mind()
            ]
        )
        self.database.commit()
        cursor.close()


class Slap:
    def author_id(self):
        return self._author_id

    def object(self):
        return self._object

    def mind(self):
        return self._mind


class TextSlap(Slap):
    def __init__(self, obj, author_id=0, mind=""):
        self._author_id = author_id
        self._object    = obj
        self._mind      = mind
