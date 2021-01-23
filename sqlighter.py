import sqlite3


class SQLighter:

    def __init__(self, tgbot_db):
        self.connection = sqlite3.connect(tgbot_db, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def add_subscriber(self, user_id, date_from, date_to, status=True):
        with self.connection:
            return self.cursor.execute(
                'INSERT INTO `subscriptions` (`user_id`, `status`, `date_from`, `date_to`) VALUES(?,?,?,?)',
                (user_id, status, date_from, date_to,))

    def date_chek(self, user_id):
        with self.connection:
            tables = self.cursor.execute("SELECT * FROM subscriptions WHERE `user_id` = ?", (user_id,)).fetchall()
            for date_to in tables:
                return date_to[4]

    def get_subscriptions(self, status=True):
        with self.connection:
            return self.cursor.execute('SELECT * FROM `subscriptions` WHERE `status` = ?', (status,)).fetchall()

    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute('UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?', (status, user_id))

    def subscriber_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()
            return bool(len(result))

    def update_date(self, date_to, user_id):
        with self.connection:
            return self.cursor.execute('UPDATE `subscriptions` SET `date_to` = ? WHERE `user_id` = ?',
                                       (date_to, user_id,))

    def add_email(self, email, user_id):
        with self.connection:
            return self.cursor.execute('UPDATE `subscriptions` SET `email` = ? WHERE `user_id` = ?', (email, user_id,))

    def close(self):
        self.connection.close()
