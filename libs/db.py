from datetime import datetime
import sqlite3

from libs.const import LOCAL_TZ

class DataBase:
    def __init__(self) -> None:
        try:
            self.conn = sqlite3.connect('postDB.db')
            print("База данных создана и успешно подключена к SQLite")
        except sqlite3.Error as error: print("[Ошибка SQLITE] ", error); exit(1)
        self._create_Table()
    
    def _create_Table(self) -> None:
        cur = self.conn.cursor()
        try:
            table_channels = '''CREATE TABLE channels (
                                        id INTEGER PRIMARY KEY,
                                        channels_id INTEGER,
                                        kolvo_post INTEGER DEFAULT 0);'''
            cur.execute(table_channels)
            print("Таблица CHANNELS создана")
        except: pass
        try:
            '''CREATE TABLE users (
                id INTEGER PRIMARY KEY, [0]
                chat_id INTEGER, [1]
                id_last_message INTEGER, [2]
                id_other_messages TEXT, [3]
                admin BOOLEAN [4]
            );'''
            table_users = '''CREATE TABLE users (
                                        id INTEGER PRIMARY KEY,
                                        chat_id INTEGER,
                                        id_last_message INTEGER,
                                        id_other_messages TEXT,
                                        admin BOOLEAN DEFAULT 0);'''
            cur.execute(table_users)
            print("Таблица USERS создана")
        except: pass
        try:
            '''
                STATUS:
                    0 - ОПУБЛИКОВАН
                    1 - УДАЛЕН
            '''
            '''CREATE TABLE posts (
                id INTEGER PRIMARY KEY, [0]
                channel_id INTEGER, [1]
                chat_id INTEGER, [2]
                message_id INTEGER, [3]
                name TEXT, [4]
                type TEXT, [5]
                status INT, [6]
                datetime TEXT [7]
            );'''
            table_posts = '''CREATE TABLE posts (
                                        id INTEGER PRIMARY KEY,
                                        channel_id INTEGER,
                                        chat_id INTEGER,
                                        message_id INTEGER,
                                        name TEXT,
                                        type TEXT,
                                        status TEXT,
                                        datetime TEXT
                                        );'''
            cur.execute(table_posts)
            print("Таблица POSTS создана")
        except: pass
        try:
            '''CREATE TABLE plan_posts (
                id INTEGER PRIMARY KEY, [0]
                name TEXT, [1]
                chat_id INTEGER, [2]
                channel_id INTEGER, [3]
                media_urls TEXT, [4]
                text TEXT, [5]
                inline_buttons TEXT, [6]
                type TEXT, [7]
                pin BOOLEAN, [8]
                day INTEGER, [9]
                month INTEGER, [10]
                year INTEGER, [11]
                hour INTEGER, [12]
                minute INTEGER [13]
            )'''
            table_plan_post = '''CREATE TABLE plan_posts (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT,
                                        chat_id INTEGER,
                                        channel_id INTEGER,
                                        media_urls TEXT,
                                        text TEXT,
                                        inline_buttons TEXT,
                                        type TEXT,
                                        pin BOOLEAN,
                                        day INTEGER,
                                        month INTEGER,
                                        year INTEGER,
                                        hour INTEGER,
                                        minute INTEGER
                                        )'''
            cur.execute(table_plan_post)
            print("Таблица PLAN_POSTS создана")
        except: pass
        try:
            '''CREATE TABLE create_post (
                id INTEGER PRIMARY KEY, [0]
                chat_id INTEGER, [1]
                channel_id, INTEGER, [2]
                type TEXT, [3]
                shag TEXT, [4]
                edit BOOLEAN DEFAULT 1, [5]
                name TEXT, [6]
                text TEXT, [7]
                media_urls TEXT, [8]
                inline_buttons TEXT, [9]
                datetime TEXT, [10]
                pin BOOLEAN DEFAULT 0, [11]
                result BOOLEAN DEFAULT 0 [12]
            )'''
            table_create_post = '''CREATE TABLE create_post (
                                        id INTEGER PRIMARY KEY,
                                        chat_id INTEGER,
                                        channel_id INTEGER,
                                        type TEXT,
                                        shag TEXT,
                                        edit BOOLEAN DEFAULT 1,
                                        name TEXT,
                                        text TEXT,
                                        media_urls TEXT,
                                        inline_buttons TEXT,
                                        datetime TEXT,
                                        pin BOOLEAN DEFAULT 0,
                                        result BOOLEAN DEFAULT 0
                                        )'''
            cur.execute(table_create_post)
            print("Таблица CREATE_POST создана")
        except: pass
        self.conn.commit()
    
    def _insert_Table(self, table_name: str, data: dict):
        tables = [i for i in data.keys()]
        tabl = ','.join(tables)
        vopr = ','.join(['?' for i in range(len(tables))])
        comm = f'INSERT INTO {table_name} ({tabl}) VALUES({vopr})'
        cur = self.conn.cursor()
        cur.execute(comm, [i for i in data.values()])
        self.conn.commit()
    
    def _select_More_Table(self, table_name: str, where: str = None) -> list:
        comm = f'SELECT * FROM {table_name}{" WHERE "+where if where != None else ""}'
        cur = self.conn.cursor()
        cur.execute(comm)
        data = cur.fetchall()
        return data

    def _select_One_Table(self, table_name: str, where: str = None) -> tuple:
        comm = f'SELECT * FROM {table_name}{" WHERE "+where if where != None else ""}'
        cur = self.conn.cursor()
        cur.execute(comm)
        data = cur.fetchone()
        return data
    
    def _exist_Table(self, table_name: str, where: str) -> bool:
        comm = f'SELECT * FROM {table_name} WHERE {where}'
        cur = self.conn.cursor()
        cur.execute(comm)
        data = cur.fetchall()
        return True if len(data) > 0 else False
    
    def _delete_Table(self, table_name: str, where: str) -> bool:
        comm = f'DELETE FROM {table_name} WHERE {where}'
        cur = self.conn.cursor()
        cur.execute(comm)
        self.conn.commit()

    def _update_Table(self, table_name: str, seta: dict, where: str):
        list_sets = [str(i)+" = ?" for i,j in seta.items()]
        sets = ','.join(list_sets)
        comm = f'UPDATE {table_name} SET {sets} WHERE {where}'
        cur = self.conn.cursor()
        cur.execute(comm, [i for i in seta.values()])
        self.conn.commit()
    
    def _count_Table(self, table_name: str, where: str = None) -> int:
        comm = f'SELECT COUNT(*) FROM {table_name}{" WHERE "+where if where != None else ""}'
        cur = self.conn.cursor()
        cur.execute(comm)
        data = cur.fetchone()
        return data[0]
    
    def _check_edit_post(self, people_id: int) -> bool:
        if self._exist_Table('create_post', f'chat_id={people_id} AND edit={True}'): return True
        return False

    def _check_admin(self, people_id: int) -> bool:
        if self._exist_Table('users', f'chat_id={people_id}'):
            request = self._select_One_Table('users', f'chat_id={people_id}')
            return False if request[3] == 0 else True
        return False
    
    def _get_first_post(self, channel_id: int, timeDate: datetime, typePost: str) -> str:
        request = self._select_One_Table('plan_posts', f'type="{typePost}" AND ( Day >= {timeDate.day} AND Month={timeDate.month} AND Year={timeDate.year} AND Hour>={timeDate.hour} AND Minute>={timeDate.minute} ) OR ( (Day > {timeDate.day} OR Day < {timeDate.day}) AND Month > {timeDate.month} ) OR Year > {timeDate.year} ORDER BY Day ASC, Month ASC, Year ASC, hour ASC, minute ASC;')
        if request == None: return 'Не найдено'
        else: 
            timePost = datetime(request[11], request[10], request[9], request[12], request[13], 0)
            c = timePost-timeDate
            if c.total_seconds() > 86400: return ''
            seconds = c.total_seconds()
            hours = seconds//3600
            minutes = 0
            while seconds > 60: 
                minutes = 1 if minutes == 60 else minutes+1
                seconds -= 60
            m = ''
            h = ''
            s = ''
            if hours != 0:
                if hours%10 == 1: h = str(hours) + ' час'
                elif hours%10 > 4 or hours%10 == 0: h = str(hours) + ' часов'
                elif hours%10 > 1: h = str(hours) + ' часа'
            if minutes != 0:
                if minutes%10 == 1: m = str(minutes) + ' минуту'
                elif minutes%10 > 4 or minutes%10 == 0: m = str(minutes) + ' минут'
                elif minutes%10 > 1: m = str(minutes) + ' минуты'
            if minutes == 0 and hours == 0:
                if seconds%10 == 1 and seconds != 11: s = str(seconds) + ' секунду'
                elif (seconds%10 > 1 and seconds%10 < 5 ) and ( seconds < 5 or seconds > 21 ): s = str(seconds) + ' секунды'
                else: s = str(seconds) + ' секунд'

            if h != '' and m != '': h += ' и'

            return f"через {h+' ' if h != '' else h}{m}{s}"
    
    def _plusMinus_post_channel(self, channel_id: int, znat: int = 1):
        request = self._select_One_Table('channels', f'channels_id={channel_id}')
        if request != None: self._update_Table('channels', {'kolvo_post': request[2]+znat}, f'channels_id={channel_id}')
    
    def _get_numPost_channel(self, channel_id: int) -> int:
        request = self._select_One_Table('channels', f'channels_id={channel_id}')
        return request[2] if request != None else 0
    
    def get_admins(self) -> list:
        request = db._select_More_Table('users', 'admin=1')
        return [i[1] for i in request]
            
'''CREATE TABLE plan_posts (
                id INTEGER PRIMARY KEY, [0]
                name TEXT, [1]
                chat_id INTEGER, [2]
                channel_id INTEGER, [3]
                media_urls TEXT, [4]
                text TEXT, [5]
                inline_buttons TEXT, [6]
                type TEXT, [7]
                pin BOOLEAN, [8]
                day INTEGER, [9]
                month INTEGER, [10]
                year INTEGER, [11]
                hour INTEGER, [12]
                minute INTEGER [13]
            )'''
db = DataBase()