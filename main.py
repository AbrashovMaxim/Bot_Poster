from aiogram import Bot, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from datetime import datetime
import pytz
import asyncio
import os

from libs.db import db
from libs.const import TOKEN, LOCAL_TZ, NUM_SMILES

select_ch = {}
change_pos = {}

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def run_check():
    while True:
        tim = datetime.now(pytz.timezone(LOCAL_TZ))
        a = db._select_More_Table('plan_posts', f'day={tim.day} AND month={tim.month} AND year={tim.year} AND hour={tim.hour} AND minute={tim.minute}')
        print(f'day={tim.day} AND month={tim.month} AND year={tim.year} AND hour={tim.hour} AND minute={tim.minute}')
        if len(a) > 0:
            for i in a:
                time = tim.strftime("%d.%m.%Y - %H:%M")
                await post_Post(i[2], i[3], i[1], i[7], i[5], i[4], i[6], time, i[8])
                db._delete_Table('plan_posts', f'id={i[0]}')
        else: await asyncio.sleep(30)

async def show_Menu(chat_id: int, number: int = None, comment: str = None) -> None:
    if number != None: select_ch[chat_id] = [number, datetime.now(pytz.timezone(LOCAL_TZ))]
    else: 
        if chat_id in select_ch: select_ch[chat_id] = [select_ch[chat_id][0], datetime.now(pytz.timezone(LOCAL_TZ))]; number = select_ch[chat_id][0]
        else: await start_Message(chat_id); return

    cht = await bot.get_chat(number)

    ib = InlineKeyboardMarkup()
    ib.add(InlineKeyboardButton("💫 Обновить 💫", callback_data="start_restartMenu"))
    ib.add(InlineKeyboardButton("📝 Выложить пост 📄", callback_data="post_post.new_post"))
    ib.add(InlineKeyboardButton("📝 Выложить пост рекламы 📣", callback_data="post_post.new_ads"))
    if db._exist_Table('create_post', f'type="POST" AND chat_id={chat_id} AND channel_id={select_ch[chat_id][0]}'): ib.add(InlineKeyboardButton("✏️ Редактировать пост 📄", callback_data="post_post.edit_post"))
    if db._exist_Table('create_post', f'type="ADS" AND chat_id={chat_id} AND channel_id={select_ch[chat_id][0]}'): ib.add(InlineKeyboardButton("✏️ Редактировать пост рекламы 📣", callback_data="post_post.edit_ads"))
    ib.add(InlineKeyboardButton("📑 Список постов 📄", callback_data="list_post"))
    ib.add(InlineKeyboardButton("📑 Список постов рекламы 📣", callback_data="list_ads"))
    ib.add(InlineKeyboardButton("🚪 Назад 🏃", callback_data="back_start"))
    get_c = await cht.get_members_count()
    get_cp = db._count_Table('posts', f'type="POST" AND channel_id={select_ch[chat_id][0]}')
    get_ca = db._count_Table('posts', f'type="ADS" AND channel_id={select_ch[chat_id][0]}')
    comment = comment+"\n\n" if comment != None else ''
    timeDate = datetime.now(pytz.timezone(LOCAL_TZ))
    timeDate = timeDate.replace(tzinfo=None)
    text = f"{comment}🔱 <b>Меню канала</b> 🔱\n<a href='https://t.me/{cht.username}'>{cht.title}</a>\n\n👨‍👩‍👧‍👦 Количество подписчиков: <b>{get_c}</b> 👨‍👩‍👧‍👦\n📃 Количество выложенных постов: <b>{get_cp}</b> 📃\n📢 Количество выложенной рекламы: <b>{get_ca}</b> 📢\n\n🕒 Ближайший запланированный пост: <b>{db._get_first_post(select_ch[chat_id][0], timeDate, 'POST')}</b> 📃\n🕓 Ближайший запланированный пост рекламы: <b>{db._get_first_post(select_ch[chat_id][0], timeDate, 'ADS')}</b> 📢\n\n❗️ <b><u>Незабывай, бот находится в разработке</u></b> ❗️"
    mess = await bot.send_message(chat_id, text, reply_markup=ib, parse_mode=ParseMode.HTML)
    await update_Message(chat_id, mess.message_id)

async def post_Post(chat_id: int, id_channel: int, name: str, typee: str, msg: str, urls: str, inline_buttons: str, dateTime: str = None, pin: bool = None) -> types.Message:
    post_ib = None
    post_media = None
    post_mess_media = None
    
    if urls != None:
        media_len = 0
        post_media = types.MediaGroup()
        temp_files = urls.split(' ')

        for i,j in enumerate(temp_files):
            if j.split('.')[-1] == 'jpg': 
                type_media = 'IMG'
                post_media.attach_photo(types.InputFile(j), msg if i == 0 and inline_buttons == None else None)
            else: 
                post_media.attach_video(types.InputFile(j), msg if i == 0 and inline_buttons == None else None)
                type_media = 'VIDEO'
            media_len += 1
    
    if inline_buttons != None:
        post_ib = InlineKeyboardMarkup()
        inline_buttons = inline_buttons.splitlines()
        for i in inline_buttons:
            a = i.split('-|-')
            a[0] = a[0].strip()
            a[1] = a[1].strip()
            post_ib.add(InlineKeyboardButton(a[0], url=a[1]))

    mess_id = ''

    if inline_buttons != None:
        if post_media != None:
            if media_len > 1: post_mess_media = await bot.send_media_group(id_channel, media=post_media)
            else: 
                if type_media == 'IMG': post_mess_media = await bot.send_photo(id_channel, photo=types.InputFile(urls))
                else: post_mess_media = await bot.send_video(id_channel, video=types.InputFile(urls))
        post_mess = await bot.send_message(id_channel, text=msg, reply_markup=post_ib, parse_mode=ParseMode.HTML)
    else:
        if post_media != None:
            if media_len > 1: post_mess = await bot.send_media_group(id_channel, media=post_media)
            else: 
                if type_media == 'IMG': post_mess = await bot.send_photo(id_channel, photo=types.InputFile(urls))
                else: post_mess = await bot.send_video(id_channel, video=types.InputFile(urls))
        else: post_mess = await bot.send_message(id_channel, text=msg, reply_markup=post_ib, parse_mode=ParseMode.HTML)

    if pin != None:
        if post_mess_media != None:
            if type(post_mess_media) == list:
                temp = [i for i in post_mess_media]
                temp.append(post_mess)
                mess_id = ' '.join([i.message_id for i in temp])
            else: mess_id = ' '.join([i.message_id for i in [post_mess, post_mess_media]])
        else:
            if type(post_mess) == list: mess_id = ' '.join([i.message_id for i in post_mess])
            else: mess_id = str(post_mess.message_id)
            
        db._insert_Table('posts', {'channel_id': id_channel, 'chat_id': chat_id, 'message_id': mess_id, 'name': name, 'type': typee, 'status': 0, 'datetime': dateTime})

        db._plusMinus_post_channel(id_channel)
        temp_files = urls.split(' ')
        for i in temp_files: 
            if os.path.isfile(i): os.remove(i)

    if post_mess_media != None:
        if type(post_mess_media) == list:
            post_mess_media.append(post_mess)
            return post_mess_media
        else:
            return [post_mess, post_mess_media]

    return post_mess

async def check_select(id_chat: int) -> bool:
    if id_chat in select_ch:
        a = datetime.now(pytz.timezone(LOCAL_TZ)) - select_ch[id_chat][1]
        if a.days >=1: return False
    else: return False
    return True

async def start_Message(chat_id: int) -> None:
    if chat_id in select_ch: del select_ch[chat_id]
    if chat_id in change_pos: del change_pos[chat_id]
    a = await bot.get_chat(chat_id)
    count_channels = db._count_Table('channels')
    ib = InlineKeyboardMarkup()
    msg = f"Приветствую, <b><i>{a['first_name']}</i></b>! 🤗\nЯ <b><i>Бот</i></b>, который поможет тебе постить посты в каналы от <b><i>PLUS inc</i></b>! 🫡\n\n{'<b>Выбери канал:</b>' if count_channels > 0 else '<b>Каналов нет!</b>'}"
    if count_channels == 0: ib.add(InlineKeyboardButton(InlineKeyboardButton('💫 Обновить 💫', callback_data="start_restart")))
    else:
        for i in db._select_More_Table('channels'):
            g_c = await bot.get_chat(i[1])
            ib.add(InlineKeyboardButton(g_c.title, callback_data="start_"+str(i[1])))

    mess = await bot.send_message(chat_id, text=msg, reply_markup=ib, parse_mode=ParseMode.HTML)
    await update_Message(chat_id, mess.message_id)

async def del_Message(chat_id: int) -> bool:
    try:
        request = db._select_One_Table('users', f'chat_id={chat_id}')
        if request[2] != None: 
            try: await bot.delete_message(chat_id, request[2])
            except: pass
        if request[3] != None:
            for i in request[3].split(' '): 
                try: await bot.delete_message(chat_id, int(i))
                except: pass
    except: pass

async def update_Message(chat_id: int, id_mess: int = None, two_id_mess: str = None) -> None:
    await del_Message(chat_id)
    db._update_Table('users', {'id_last_message': id_mess, 'id_other_messages': two_id_mess}, f'chat_id={chat_id}')

async def loading_Message(chat_id: int) -> None:
    message = await bot.send_message(chat_id, '♻️ Загрузка... ♻️')
    await update_Message(chat_id, message.message_id)


# @dp.channel_post_handler()
# async def echo_post_send(message: types.Message): await message.delete()

@dp.message_handler(content_types=types.ContentType.TEXT)
async def echo_send(message: types.Message):
    chat_id = message['from']['id']
    if db._check_admin(chat_id):
        if message.text == '/start': # Это старт общения с ботом | This is the start of communication with the bot
            await start_Message(chat_id)
        else:
            if db._check_edit_post(chat_id):
                check = await check_select(chat_id)
                if check:
                    temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                    if temp[4] == '1': 
                        db._update_Table('create_post', {'name': message.text}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                        await new_edit_post(chat_id, '1')
                    elif temp[4] == '2': 
                        if message.text == '': await new_edit_post(chat_id, '2', '❗️ Содержание поста не должно быть - <u><b>пустое</b></u> ❗️')
                        else: 
                            db._update_Table('create_post', {'text': message.html_text}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                            await new_edit_post(chat_id, '2')
                    elif temp[4] == '4':
                        try:
                            a = message.text.splitlines()
                            res = []
                            for i in a:
                                b = i.split('-|-')
                                if len(b) != 2:
                                    await new_edit_post(chat_id, '4', f'❗️ Неправильно введены кнопки ❗️\n<code>{message.text}</code>')
                                    await message.delete()
                                    return
                                b[0] = b[0].strip()
                                b[1] = b[1].strip()
                                res.append(b[0] + ' - ' + b[1])
                            res = '\n'.join(res)
                            db._update_Table('create_post', {'inline_buttons': res}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                            await new_edit_post(chat_id, '4')
                        except: await new_edit_post(chat_id, '4', f'❗️ Неправильно введены кнопки ❗️\n<code>{message.text}</code>'); await message.delete(); return
                    elif temp[4] == '5':
                        # 01.01.2004 - 18:32
                        try:
                            if message.text.lower() != 'сейчас':
                                a = message.text.splitlines()[0].split('-')
                                a[0] = a[0].strip()
                                a[1] = a[1].strip()
                                if len(a[0].split('.')) != 3 or len(a[1].split(':')) != 2:
                                    print(a[0], a[1])
                                    await new_edit_post(chat_id, '5', f'❗️ Неправильно введена дата ❗️\n<code>{message.text}</code>')
                                    await message.delete()
                                    return
                            elif  message.text.lower() == 'сейчас': pass
                            else: await new_edit_post(chat_id, '5', f'❗️ Некоректно введена дата ❗️\n<code>{message.text}</code>'); await message.delete(); return

                            db._update_Table('create_post', {'datetime': message.text}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                            await new_edit_post(chat_id, '5')
                        except Exception as e: print(e); await new_edit_post(chat_id, '5', f'❗️ Ошибка в дате ❗️\n<code>{message.text}</code>'); await message.delete(); return
                    await message.delete();
                    return

                else:
                    db._update_Table('create_post', {'edit': False}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
            await start_Message(chat_id)

    else: 
        if not db._exist_Table('users', f'chat_id={chat_id}'): db._insert_Table('users', {'chat_id': chat_id})

    await message.delete()

@dp.message_handler(content_types=types.ContentType.ANY)
async def echo_send_video(message: types.Message):
    await message.delete()
    chat_id = message['from']['id']
    await del_Message(chat_id)
    if db._check_admin(chat_id):
        if db._check_edit_post(chat_id):
            a = 'return'
            if message.content_type == 'video': a = save_file_message(chat_id, 'VIDEO')
            elif message.content_type == 'photo' or message.content_type == 'sticker': a = save_file_message(chat_id, 'IMG')

            if a == 'False': await new_edit_post(chat_id, '3', '❗️ Нельзя добавить в пост больше <u><b>10 медиафайлов</b></u> ❗️'); return
            elif a == 'return': 
                temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                await new_edit_post(chat_id, temp[4]);
                return
            else:
                if message.content_type == 'video': await message.video.download(a)
                elif message.content_type == 'photo': await message.photo[-1].download(a)
                elif message.content_type == 'sticker': await message.sticker.download(a)

            await new_edit_post(chat_id, '3')
        else: await start_Message(chat_id)
    

def save_file_message(chat_id: int, typee: str) -> bool:
    temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
    if temp[4] == '3':
        a = []
        if temp[8] != None:
            if len(temp[8]) > 0:
                a = temp[8].split(' ')
                if len(a) == 10: return 'False'
        tim = datetime.now(pytz.timezone(LOCAL_TZ))
        file = f'{"photos" if typee == "IMG" else "videos"}/{tim.year}/{tim.month}/{tim.day}/{chat_id}/{"photo" if typee == "IMG" else "video"}_{tim.hour}_{tim.minute}_{tim.second}_{tim.microsecond}.{"jpg" if typee == "IMG" else "mp4"}'
        a.append(file)
        b = ' '.join(a)
        db._update_Table('create_post', {'media_urls': b}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
        return file
    return 'return'

@dp.my_chat_member_handler()
async def join_and_leave_bot_on_channel(message: types.Message) -> None:
    a = message.new_chat_member.status
    if a == "left" or a == "kicked":
        if db._exist_Table('channels', f'channels_id={message.chat.id}'): 
            db._delete_Table('channels', f'channels_id={message.chat.id}')
            await message_admin(f'❗️ Бот удален из канала ❗️\n{message.chat.title}')
    else:
        if db._check_admin(message['from']['id']):
            if not db._exist_Table('channels', f'channels_id={message.chat.id}'): 
                db._insert_Table('channels', {'channels_id': message.chat.id})
                await message_admin(f'❗️ Бот добавлен в канала ❗️\n{message.chat.title}')
            return
        await message.chat.leave()

@dp.callback_query_handler(Text(startswith="start_"))
async def process_callback_start(callback: types.CallbackQuery):
    chat_id = callback['from']['id']
    if not db._check_admin(chat_id): return
    code = callback.data.split('_')[1]

    if code == 'restart': await start_Message(chat_id); return
    if code == 'restartMenu': await show_Menu(chat_id); return

    if not await check_select(chat_id):
        await show_Menu(chat_id, int(code))
        
    else: await start_Message(chat_id)

@dp.callback_query_handler(Text(startswith="back_"))
async def process_callback_back(callback: types.CallbackQuery):
    code = callback.data.split('_')[1]
    if code == 'start': await start_Message(callback['from']['id'])
    if code == 'post': await show_Menu(callback['from']['id'], comment='✅ <b>Пост сохранен!</b> ✅')

@dp.callback_query_handler(Text(startswith="delete_"))
async def process_callback_back(callback: types.CallbackQuery):
    code = callback.data.split('_')[1].split('.')
    chat_id = callback['from']['id']
    if code[0] == 'post':
        try:
            num = int(code[1])
            a = {}
            if num == 1: a = {'name': None}
            elif num == 2: a = {'text': None}
            elif num == 3: 
                temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                a = {'media_urls': None}
                if temp[8] != None:
                    temp_files = temp[8].split(' ')
                    for i in temp_files:
                        if os.path.isfile(i): os.remove(i)
            elif num == 4: a = {'inline_buttons': None}
            elif num == 5: a = {'datetime': None}
            db._update_Table('create_post', a, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
            await new_edit_post(chat_id, str(num))
        except Exception as e:
            if code[1] == 'all':
                temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                if temp[8] != None:
                    temp_files = temp[8].split(' ')
                    for i in temp_files:
                        if os.path.isfile(i): os.remove(i)
                db._delete_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                await show_Menu(callback['from']['id'], comment='✅ <b>Пост удален!</b> ✅')
            
    elif code[0] == 'media':
        num = int(code[1])
        temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
        if temp[8] != None:
            temp_files = temp[8].split(' ')
            if os.path.isfile(temp_files[num]): os.remove(temp_files[num])
        temp_files.pop(num)
        temp_files = ' '.join(temp_files)
        if temp_files == '': temp_files = None
        db._update_Table('create_post', {'media_urls': temp_files}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
        await new_edit_post(chat_id, '3')

async def new_edit_post(chat_id: int, shag: str = None, comment: str = None):
    await loading_Message(chat_id)
    if shag == 'pin':
        temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
        if temp[11]: db._update_Table('create_post', {'pin': False}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
        else: db._update_Table('create_post', {'pin': True}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
        await new_edit_post(chat_id, '6')
        return
    
    db._update_Table('create_post', {'shag': shag}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
    temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
    temp_mes = '\n\n<b>Сообщение</b>: ' + comment if comment != None else ''

    media = None
    media_len = 0
    type_media = None
    ib = None
    msg = None
    mess_two = None

    # =================================================================================================================================
    if shag == '1':
        count = db._get_numPost_channel(select_ch[chat_id][0])
        a = '\n\n<b>Текущее название пост</b>: ' + (temp[6] if temp[6] != None else 'Пост №'+str(count+1))
        
        msg = f"⚜️ <b>Создание поста [1/6] - <u>Название поста</u></b> ⚜️{a}\n\n💢 Введите название поста 💢\n\n<i>Название поста - будет отображено только в списке постов</i>\n\n<i>Нажав на кнопку <u><b>Далее</b></u>, название поста будет:</i>\n<u><b>{temp[6] if temp[6] != None else 'Пост №'+str(count+1)}</b></u>{temp_mes}"
        a = 'Пост №'+str(count+1)
        if temp[6] == None: db._update_Table('create_post', {'name': a}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')

        ib = InlineKeyboardMarkup()
        # ============================ [ InlineKeyboardButton ] ============================
        if not temp[12]: 
            ib.add(InlineKeyboardButton("✅ Дальше ✅", callback_data="post_post.2"))
            if temp[6] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.1"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="back_post"))
        else:
            ib.add(InlineKeyboardButton("✅ Сохранить ✅", callback_data="post_post.6"))
            if temp[6] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.1"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.6"))
            ib.add(InlineKeyboardButton("🚪 Выход 🏃", callback_data="back_post"))
        # ==================================================================================
    # =================================================================================================================================
    elif shag == '2':
        a = '<b>Текущее содержание поста:</b>\n\n' + (temp[7] if temp[7] != None else 'Пустой пост')
        msg = f"⚜️ <b>Создание поста [2/6] - <u>Содержание поста</u></b> ⚜️\n\n💢 Введите содержание поста 💢\n\n<i>Нажав на кнопку <u><b>Далее</b></u>, содержание поста <u><b>сохранится</b></u></i>\n{temp_mes}"

        if temp[7] == None: db._update_Table('create_post', {'text': 'Пустой пост'}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')

        ib = InlineKeyboardMarkup()
        # ============================ [ InlineKeyboardButton ] ============================
        if not temp[12]: 
            ib.add(InlineKeyboardButton("✅ Дальше ✅", callback_data="post_post.3"))
            if temp[7] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.2"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.1"))
        else:
            ib.add(InlineKeyboardButton("✅ Сохранить ✅", callback_data="post_post.6"))
            if temp[7] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.2"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.6"))
        ib.add(InlineKeyboardButton("🚪 Выход 🏃", callback_data="back_post"))

        mess_two = await bot.send_message(chat_id, text=a, parse_mode=ParseMode.HTML)
        # ==================================================================================
    # =================================================================================================================================
    elif shag == '3':
        a = '<i>Нажмите на номер изображения, чтобы удалить его</i>\n\n' if temp[8] != None else ''
        msg = f"⚜️ <b>Создание поста [3/6] - <u>Медиафайлы поста</u></b> ⚜️\n\n💢 Отправьте изображения/видео для поста 💢\n\n{a}<i>Нажав на кнопку <u><b>Далее</b></u>, к посту {'медиафайлы <u><b>будут</b></u> прикреплены' if temp[8] != None else 'медиафайлы <u><b>не будут</b></u> прикреплены'}</i>{temp_mes}"

        ib = InlineKeyboardMarkup(row_width=5)
        if temp[8] != None:
            media = types.MediaGroup()
            inlineGroup = []
            temp_files = temp[8].split(' ')

            for i,j in enumerate(temp_files):
                if j.split('.')[-1] == 'jpg': 
                    type_media = 'IMG'
                    media.attach_photo(types.InputFile(j))
                else: 
                    media.attach_video(types.InputFile(j))
                    type_media = 'VIDEO'
                media_len += 1
                inlineGroup.append(InlineKeyboardButton(NUM_SMILES[i], callback_data="delete_media."+str(i)))
                if len(inlineGroup) == 5:
                    ib.row(*inlineGroup)
                    inlineGroup = []
            if len(inlineGroup) > 1: ib.row(*inlineGroup)
            elif len(inlineGroup) == 1: ib.add(inlineGroup[0])
        
            if media_len > 1: mess_two = await bot.send_media_group(chat_id, media=media)
            else: 
                if type_media == 'IMG': mess_two = await bot.send_photo(chat_id, photo=types.InputFile(temp[8]))
                else: mess_two = await bot.send_video(chat_id, video=types.InputFile(temp[8]))
        # ============================ [ InlineKeyboardButton ] ============================
        if media_len > 1: ib.add(InlineKeyboardButton("💫 Поменять местами 💫", callback_data="post_post.change"))
        if not temp[12]: 
            ib.add(InlineKeyboardButton("✅ Дальше ✅", callback_data="post_post.4"))
            if temp[8] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.3"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.2"))
        else:
            ib.add(InlineKeyboardButton("✅ Сохранить ✅", callback_data="post_post.6"))
            if temp[8] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.3"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.6"))
        ib.add(InlineKeyboardButton("🚪 Выход 🏃", callback_data="back_post"))
        # ==================================================================================
    # =================================================================================================================================
    elif shag == '4':
        msg = f"⚜️ <b>Создание поста [4/6] - <u>Кнопки поста</u></b> ⚜️\n\n💢 Введите кнопки поста 💢\n\nФормат ввода:\n<code>Название кнопки #1 -|- https://url.com/</code>\n\n<code>Название кнопки #1 -|- https://url.com/ \nНазвание кнопки #2 -|- https://url.com/</code>\n\n❗️ <b><code>-|-</code>  ОБЯЗАТЕЛЬНО</b> ❗️\n\n<i>Нажав кнопку <u><b>Далее</b></u>, у поста {'<u><b>будут</b></u> кнопки' if temp[8] != None else '<u><b>не будет</b></u> кнопок'}</i>{temp_mes}"

        ib = InlineKeyboardMarkup()
        # ============================ [ InlineKeyboardButton ] ============================
        if not temp[12]: 
            ib.add(InlineKeyboardButton("✅ Дальше ✅", callback_data="post_post.5"))
            if temp[9] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.4"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.3"))
        else:
            ib.add(InlineKeyboardButton("✅ Сохранить ✅", callback_data="post_post.6"))
            if temp[9] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.4"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.6"))
        ib.add(InlineKeyboardButton("🚪 Выход 🏃", callback_data="back_post"))
        # ==================================================================================
        if temp[9] != None:
            ib_two = InlineKeyboardMarkup()

            a = temp[9].split('\n')
            for i in a:
                b = i.split('-')
                b[0] = b[0].strip()
                b[1] = b[1].strip()
                ib_two.add(InlineKeyboardButton(b[0], url=b[1]))
            
            mess_two = await bot.send_message(chat_id, text="<b>Пример кнопок:</b>", reply_markup=ib_two, parse_mode=ParseMode.HTML)
            
    # =================================================================================================================================
    elif shag == '5':
        msg = f"⚜️ <b>Создание поста [5/6] - <u>Дата и время публикации поста</u></b> ⚜️\n💢 Введите дату и время публикации поста 💢\n\nФормат ввода:\n<code>DD.MM.YYYY - HH:MM</code>\n\n<code>01.01.2004 - 18:32\nИли\nСЕЙЧАС - то есть, пост будет опубликован СЕЙЧАС</code>\n\n❗️ <b>Тире - ОБЯЗАТЕЛЬНО</b> ❗️\n❕ <b>Время должно быть больше текущего</b> ❕\n\n<i>Можете нажать <u><b>Далее</b></u>, тогда пост выпуститься <u><b>{'СЕЙЧАС' if temp[10] == None else 'СЕЙЧАС' if temp[10] == 'сейчас' else temp[10]}</b></u></i>{temp_mes}"

        if temp[10] == None: db._update_Table('create_post', {'datetime': 'сейчас'}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')

        ib = InlineKeyboardMarkup()
        # ============================ [ InlineKeyboardButton ] ============================
        if not temp[12]: 
            ib.add(InlineKeyboardButton("✅ Дальше ✅", callback_data="post_post.6"))
            if temp[10] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.5"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.4"))
        else:
            ib.add(InlineKeyboardButton("✅ Сохранить ✅", callback_data="post_post.6"))
            if temp[10] != None: ib.add(InlineKeyboardButton("✂️ Сбросить ✂️", callback_data="delete_post.5"))
            ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="post_post.6"))
        ib.add(InlineKeyboardButton("🚪 Выход 🏃", callback_data="back_post"))
        # ==================================================================================
    # =================================================================================================================================
    elif shag == '6':
        if not temp[12]: db._update_Table('create_post', {'result': True}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
        
        msg = f"⚜️ <b>Создание поста [6/6] - <u>Предпросмотр поста</u></b> ⚜️\n{temp[6]}\n\n🔸 Тип поста: <b>{temp[3]}</b> 🔸\n🔹 Пост будет опубликован: <b>{temp[10]}</b> 🔹"

        mess_two = await post_Post(None, chat_id, None, None, temp[7], temp[8], temp[9])
    
        ib = InlineKeyboardMarkup(row_width=2)
        ib.add(InlineKeyboardButton("✅ Сохранить ✅", callback_data="post_post.result"))
        ib.add(InlineKeyboardButton("🗑 Удалить 🗑", callback_data="delete_post.all"))
        ib.row(InlineKeyboardButton("✏️ Название 💬", callback_data="post_post.1"), InlineKeyboardButton("✏️ Содержание 📃", callback_data="post_post.2"))
        ib.row(InlineKeyboardButton("✏️ Медиафайлы 🖼", callback_data="post_post.3"), InlineKeyboardButton("✏️ Кнопки 📝", callback_data="post_post.4"))
        ib.add(InlineKeyboardButton("✏️ Дата и время 🕒", callback_data="post_post.5"))
        ib.add(InlineKeyboardButton("📌 Закрепить 📌" if not temp[11] else "📍 Открепить 📍", callback_data="post_post.pin"))
        ib.add(InlineKeyboardButton("🚪 Выход 🏃", callback_data="back_post"))
    # =================================================================================================================================
    elif shag == 'result':
        if temp[10] == 'сейчас':
            a = datetime.now(pytz.timezone(LOCAL_TZ))
            a = a.strftime("%d.%m.%Y - %H:%M")
            db._delete_Table('create_post', f'edit={True} AND chat_id={chat_id}')
            await post_Post(chat_id, select_ch[chat_id][0], temp[6], temp[3], temp[7], temp[8], temp[9], a, temp[11])
            await show_Menu(chat_id, comment='✅ <b>Пост успешно выпущен!</b> ✅')
        else:
            a = datetime.now(pytz.timezone(LOCAL_TZ))
            a = a.replace(tzinfo=None)
            b = datetime.strptime(temp[10], "%d.%m.%Y - %H:%M")
            c = b-a
            
            if int(c.total_seconds()) >= 40:
                dateTime = temp[10].split('-')
                dateTime[0] = dateTime[0].strip()
                dateTime[1] = dateTime[1].strip()
                date = dateTime[0].split('.')
                time = dateTime[1].split(':')
                db._insert_Table('plan_posts', {'name': temp[6], 'channel_id': select_ch[chat_id][0], 'chat_id': chat_id, 'media_urls': temp[8],'text': temp[7], 'inline_buttons': temp[9], 'type': temp[3], 'pin': temp[11], 'day': int(date[0]), 'month': int(date[1]), 'year': int(date[2]), 'hour': int(time[0]),'minute': time[1]})
                db._delete_Table('create_post', f'edit={True} AND chat_id={chat_id}')
                await show_Menu(chat_id, comment='✅ <b>Пост успешно запланирован!</b> ✅')
            else:
                a = datetime.now(pytz.timezone(LOCAL_TZ))
                a = a.strftime("%d.%m.%Y - %H:%M")
                db._delete_Table('create_post', f'edit={True} AND chat_id={chat_id}')
                await post_Post(chat_id, select_ch[chat_id][0], temp[6], temp[3], temp[7], temp[8], temp[9], a, temp[11])
                await show_Menu(chat_id, comment='✅ <b>Пост успешно выпущен!</b> ✅')
        return
    # =================================================================================================================================
    
    mess = await bot.send_message(chat_id, msg, reply_markup=ib, parse_mode=ParseMode.HTML)
    if mess_two != None:
        if type(mess_two) == list:
            mess_two = ' '.join([str(i.message_id) for i in mess_two])
        else: mess_two = mess_two.message_id

    await update_Message(chat_id, mess.message_id, mess_two if mess_two != None else None)

async def change_posIMG(chat_id: int) -> None:
    temp = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
    if temp[8] == None: await new_edit_post(chat_id, '3'); return
    
    ib = InlineKeyboardMarkup(row_width=5)

    media = types.MediaGroup()
    media_len = 0
    inlineGroup = []
    temp_files = temp[8].split(' ')

    for i in temp_files:
        if i.split('.')[-1] == 'jpg': media.attach_photo(types.InputFile(i))
        else: media.attach_video(types.InputFile(i))
        media_len += 1
    

    if chat_id in change_pos:
        print('================================================================')
        for i in range(media_len):
            if change_pos[chat_id] != i:
                print(i)
                if i == 0: 
                    inlineGroup.append(InlineKeyboardButton('❎'+NUM_SMILES[i], callback_data="change_change."+str(i)))
                    if i+1 != change_pos[chat_id]: inlineGroup.append(InlineKeyboardButton(NUM_SMILES[i]+'❎'+NUM_SMILES[i+1], callback_data="change_change."+str(i+1)))
                elif media_len-1 == i:
                    inlineGroup.append(InlineKeyboardButton(NUM_SMILES[i]+'❎', callback_data="change_change."+str(i+1)))
                    if i-1 != change_pos[chat_id] and i != media_len-1: inlineGroup.append(InlineKeyboardButton(NUM_SMILES[i-1]+'❎'+NUM_SMILES[i], callback_data="change_change."+str(i+1)))
                else: 
                    if i != change_pos[chat_id] and i+1 != change_pos[chat_id]: inlineGroup.append(InlineKeyboardButton(NUM_SMILES[i]+'❎'+NUM_SMILES[i+1], callback_data="change_change."+str(i+1)))
            
            print(inlineGroup)
            if len(inlineGroup) == 5:
                ib.row(*inlineGroup)
                inlineGroup = []
        
        print('================================================================')
        msg = f"⚜️ <b>Создание поста [3/6] - <u>Поменять местами медиафайлы поста</u></b> ⚜️\n\n💢 Нажмите на номер изображения, чтобы переместить его 💢"
    else:
        for i in range(media_len):
            inlineGroup.append(InlineKeyboardButton(NUM_SMILES[i], callback_data="change_select."+str(i)))
            if len(inlineGroup) == 5:
                ib.row(*inlineGroup)
                inlineGroup = []
        
        msg = f"⚜️ <b>Создание поста [3/6] - <u>Поменять местами медиафайлы поста</u></b> ⚜️\n\n💢 Нажмите на кнопку, между какими изображениями хотите переместить его 💢"
    
    if len(inlineGroup) > 1: ib.row(*inlineGroup)
    elif len(inlineGroup) == 1: ib.add(inlineGroup[0])
    
    if chat_id in change_pos: ib.add(InlineKeyboardButton("🏃‍♀️ Назад 🏃", callback_data="change_start"))
    ib.add(InlineKeyboardButton("🚪 Выход 🏃", callback_data="change_back"))
    
    mess_two = await bot.send_media_group(chat_id, media=media)
    mess_two = ' '.join([str(i.message_id) for i in mess_two])
    
    mess = await bot.send_message(chat_id, msg, reply_markup=ib, parse_mode=ParseMode.HTML)

    await update_Message(chat_id, mess.message_id, mess_two)

'''
    ❎1️⃣     0
    1️⃣❎2️⃣   1
    2️⃣❎3️⃣   2
    3️⃣❎4️⃣   3
    4️⃣❎5️⃣   4
    5️⃣❎6️⃣   5
    6️⃣❎7️⃣   6
    7️⃣❎8️⃣   7
    8️⃣❎9️⃣   8
    9️⃣❎🔟   9
    🔟❎     10
'''
# change_start
# change_back
# change_select.1
# change_change.1

@dp.callback_query_handler(Text(startswith="change_"))
async def process_callback_change(callback: types.CallbackQuery):
    if not db._check_admin(callback['from']['id']): return
    check = await check_select(callback['from']['id'])
    chat_id = callback["from"]["id"]
    
    if check:
        await loading_Message(chat_id)
        
        temp = callback.data.split('_')
        if temp[1] == 'start':
            if chat_id in change_pos: del change_pos[chat_id]
            await change_posIMG(chat_id)
        elif temp[1] == 'back': await new_edit_post(chat_id, '3')
        else: 
            temp2 = temp[1].split('.')
            if temp2[0] == 'select': change_pos[chat_id] = int(temp2[1])
            else: 
                temp_request = db._select_One_Table('create_post', f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')
                temp_split = temp_request[8].split(' ')
                select_index = change_pos[chat_id]
                paste_index = int(temp2[1])
                
                if paste_index < select_index:
                    temp_name = temp_split.pop(select_index)
                    temp_split.insert(paste_index, temp_name)
                else:
                    temp_split.insert(paste_index, temp_split[select_index])
                    temp_split.pop(select_index)
                
                temp_files = ' '.join(temp_split)
                db._update_Table('create_post', {'media_urls': temp_files}, f'chat_id={chat_id} AND edit={True} AND channel_id={select_ch[chat_id][0]}')

                if chat_id in change_pos: del change_pos[chat_id]
            
            await change_posIMG(chat_id)
    else:
        if chat_id in change_pos: del change_pos[chat_id]
        db._update_Table('create_post', {'edit': False}, f'chat_id={chat_id} AND edit={True}')
        await start_Message(chat_id)

@dp.callback_query_handler(Text(startswith="post_"))
async def process_callback_post(callback: types.CallbackQuery):
    if not db._check_admin(callback['from']['id']): return
    check = await check_select(callback['from']['id'])
    chat_id = callback["from"]["id"]
    
    if check:
        await loading_Message(chat_id)

        temp = callback.data.split('_')
        temp_2 = temp[1].split('.')
        if temp_2[1] == 'new':
            if db._exist_Table('create_post', f'chat_id={chat_id} AND type="{temp[2].upper()}" AND channel_id={select_ch[chat_id][0]}'):
                msg = "Вы точно хотите создать новый пост?\n\n❗️ <b><u>Старый прогресс будет удален!</u></b> ❗️"
                ib = InlineKeyboardMarkup()
                ib.add(InlineKeyboardButton("✅ Да ✅", callback_data="post_post.yes_"+temp[2]))
                ib.add(InlineKeyboardButton("❌ Нет ❌", callback_data="post_post.no"))
                
                mess = await bot.send_message(chat_id, msg, reply_markup=ib, parse_mode=ParseMode.HTML)
                await update_Message(chat_id, mess.message_id)
            else:
                db._insert_Table('create_post', {'chat_id': chat_id, 'channel_id': select_ch[chat_id][0], 'type': temp[2].upper(), 'shag': '1', 'edit': True})  
                await new_edit_post(chat_id, '1')
        elif temp_2[1] == 'edit':
            db._update_Table('create_post', {'edit': True}, f'chat_id={chat_id} AND channel_id={select_ch[chat_id][0]} AND type="{temp[2].upper()}"')
            temp_4 = db._select_One_Table('create_post', f'chat_id={chat_id} AND channel_id={select_ch[chat_id][0]} AND type="{temp[2].upper()}"')
            await new_edit_post(chat_id, temp_4[4])
        elif temp_2[1] == 'yes':
            temp2 = db._select_One_Table('create_post', f'chat_id={chat_id} AND type="{temp[2].upper()}" AND channel_id={select_ch[chat_id][0]}')
            if temp2[8] != None:
                temp_files = temp2[8].split(' ')
                for i in temp_files:
                    if os.path.isfile(i): os.remove(i)
            db._delete_Table('create_post', f'chat_id={chat_id} AND type="{temp[2].upper()}" AND channel_id={select_ch[chat_id][0]}')
            db._insert_Table('create_post', {'chat_id': chat_id, 'channel_id': select_ch[chat_id][0], 'type': temp[2].upper(), 'shag': '1', 'edit': True})  
            await new_edit_post(chat_id, '1')
        elif temp_2[1] == 'no': await show_Menu(chat_id)

        elif temp_2[1] == 'change': await change_posIMG(chat_id)

        else: await new_edit_post(chat_id, temp[1].split('.')[1])
    else:
        db._update_Table('create_post', {'edit': False}, f'chat_id={chat_id} AND edit={True}')
        await start_Message(chat_id)

async def message_admin(msg: str):
    request = db.get_admins()
    for i in request:
        mess = await bot.send_message(i, msg, parse_mode=ParseMode.HTML)
        request_user = db._select_One_Table('users', f'chat_id={i}')
        if request_user[2] != None:
            if request_user[3] != None:
                temp = request_user[3].split(' ')
                temp.append(str(mess.message_id))
                temp = ' '.join(temp)
            else: temp = str(mess.message_id)
            db._update_Table('users', {'id_other_messages': temp}, f'chat_id={i}')
            continue
        else: db._update_Table('users', {'id_last_message': mess.message_id}, f'chat_id={i}')


async def on_startup(x): 
    print('''
        ==============================\n
        Бот - включен!\n
        by MaximilianWhite\n
        ==============================
    ''')
    await message_admin('✅ Бот - включен! ✅')
    asyncio.create_task(run_check())
async def on_shutdown(x): 
    print('''
        ==============================\n
        Бот - выключен!\n
        by MaximilianWhite\n
        ==============================
    ''')
    message_admin('❌ Бот - выключен! ❌')
    

# loop = asyncio.get_event_loop()
# loop.create_task(run_check())
executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)