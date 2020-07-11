import sqlite3


class DataBase:
    def __init__(self, dbpath="data.db"):
        self.tables = self.get_tables()
        self.start_users_table()

    def get_tables(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name;"""
        )
        tables = cursor.fetchall()
        conn.close()
        return tables

    def start_users_table(self):
        if ("users",) not in self.tables:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cmd = """
            CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR,
                    telegram_id VARCHAR NOT NULL,
                    notification INT NOT NULL
            );
            """
            cursor.execute(cmd)
            conn.commit()
            self.tables = self.get_tables()
            conn.close()

    def insert_user(self, name=None, telegram_id=None, notification=1):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cmd = f"""INSERT INTO users (name, telegram_id, notification)
        VALUES ('{name}', '{telegram_id}', {notification})"""
        cursor.execute(cmd)
        conn.commit()
        conn.close()

    def update_user(self, user_id, param_dict):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cmd = f"""UPDATE users SET"""
        for i, col in enumerate(param_dict.keys()):
            cmd += f""" {col} = '{param_dict[col]}'"""
            if i > 0:
                cmd += ","
        cmd += f" WHERE id = {user_id}"
        cursor.execute(cmd)
        conn.commit()
        conn.close()

    def check_telegram_user(self, telegram_id):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cmd = f"""SELECT * FROM users WHERE telegram_id = '{telegram_id}'"""
        cursor.execute(cmd)
        results = cursor.fetchall()
        conn.close()
        if len(results) > 0:
            return results[0]
        else:
            return None

    def get_telegram_user(self, telegram_id):
        user = self.check_telegram_user(telegram_id)
        if not user:
            self.insert_user(telegram_id=telegram_id)
            user = self.check_telegram_user(telegram_id)
        return user

    def get_users(self, param_dict=None):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cmd = f"""SELECT * FROM users"""
        if param_dict:
            cmd += " WHERE"
            for i, col in enumerate(param_dict.keys()):
                cmd += f""" {col} = '{param_dict[col]}'"""
                if i > 0:
                    cmd += ","
        cursor.execute(cmd)
        r = cursor.fetchall()
        conn.close()
        return r
