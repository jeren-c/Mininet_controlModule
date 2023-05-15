import sqlite3

DATABASE_FILE = 'form_data.db'

class Database:
    def create_database(self):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS form_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        src_ip TEXT,
                        dst_ip TEXT,
                        dst_port INTEGER,
                        acc_auth TEXT)''')

        conn.commit()
        conn.close()

    def insert_data(self, form_data):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()

        c.execute('''INSERT INTO form_data (src_ip, dst_ip, dst_port, acc_auth) 
                     VALUES (?, ?, ?, ?)''', (form_data['src_ip'], form_data['dst_ip'], form_data['dst_port'], form_data['acc_auth']))

        conn.commit()
        conn.close()