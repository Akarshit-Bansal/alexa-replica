import json
import os
import sqlite3

class Storage:
    def __init__(self, use_sqlite=False):
        self.use_sqlite = use_sqlite
        if use_sqlite:
            self.conn = sqlite3.connect('assistant.db')
            self.create_tables()
        else:
            self.data_file = 'assistant_data.json'

    def create_tables(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY, task TEXT, time TEXT)''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS alarms (id INTEGER PRIMARY KEY, time TEXT)''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS shopping_list (id INTEGER PRIMARY KEY, item TEXT)''')
        self.conn.commit()

    def load_data(self):
        if self.use_sqlite:
            reminders = [row for row in self.conn.execute('SELECT task, time FROM reminders')]
            alarms = [row[0] for row in self.conn.execute('SELECT time FROM alarms')]
            shopping_list = [row[0] for row in self.conn.execute('SELECT item FROM shopping_list')]
            return {'reminders': reminders, 'alarms': alarms, 'shopping_list': shopping_list}
        else:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {'reminders': [], 'alarms': [], 'shopping_list': []}

    def save_data(self, data):
        if self.use_sqlite:
            self.conn.execute('DELETE FROM reminders')
            self.conn.execute('DELETE FROM alarms')
            self.conn.execute('DELETE FROM shopping_list')
            for task, time in data['reminders']:
                self.conn.execute('INSERT INTO reminders (task, time) VALUES (?, ?)', (task, time))
            for time in data['alarms']:
                self.conn.execute('INSERT INTO alarms (time) VALUES (?)', (time,))
            for item in data['shopping_list']:
                self.conn.execute('INSERT INTO shopping_list (item) VALUES (?)', (item,))
            self.conn.commit()
        else:
            with open(self.data_file, 'w') as f:
                json.dump(data, f)

    def close(self):
        if self.use_sqlite:
            self.conn.close()
