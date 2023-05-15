import sqlite3

def fetch_data_from_database():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()

    c.execute('SELECT * FROM form_data')

    rows = c.fetchall()

    conn.close()
    return rows

if __name__ == '__main__':
    data = fetch_data_from_database()
    print('Data in the database:')
    print('ID | Src IP | Dst IP | Dst Port | Acc Auth')
    print('-------------------------------------------')
    for row in data:
        print('{} | {} | {} | {} | {}'.format(row[0], row[1], row[2], row[3], row[4]))