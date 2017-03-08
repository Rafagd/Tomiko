class AuthorTable:
    def __init__(self, database):
        self.database = database

    def create(self):
        cursor = self.database.cursor()
        cursor.execute('''
	    CREATE TABLE authors(
		id INTEGER NOT NULL PRIMARY KEY,
		first_name TEXT NOT NULL,
		last_name TEXT NOT NULL,
		user_name TEXT NOT NULL,
                gender INT NOT NULL
	    )
        ''')
        cursor.close()

    def insert(author):
        cursor = self.database.cursor()
        cursor.execute('''INSERT INTO author VALUES(?, ?, ?, ?)''',
            author.id(),
            author.first_name(),
            author.last_name(),
            author.user_name(),
            author.gender()
        )
        self.database.commit()
        cursor.close()


class Author:
    def __init__(_id=0, first_name='', last_name='', user_name='', gender=''):
        self.id         = _id
        self.first_name = first_name
        self.last_name  = last_name
        self.user_name  = user_name
        self.gender     = gender

    def id(self):
        return self.id

    def first_name(self):
        return self.first_name

    def last_name(self):
        return self.last_name

    def user_name(self):
        return self.user_name

    def gender(self):
        return self.gender
