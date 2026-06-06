import os
from dotenv import load_dotenv
import telebot
from telebot import types
import random
import json
import time
import sqlite3

conn = sqlite3.connect('bjt.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, cards TEXT, last_drop REAL, promo_used TEXT, progress_time REAL DEFAULT 0)''')
conn.commit()

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def load_rappers():
    with open("rappers.json","r", encoding='utf-8') as f:
        return json.load(f)
rappers = load_rappers()

RARITY = {'common': 'Обычный ⚪️',
            'rare': 'Редкий 🟢',
            'epic': 'Эпический 🟣' ,
            'legendary': 'Легендарный 🟡',
            'mythic': 'Мифический 🔴'
            }

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🆘 Помощь", callback_data='help')
    btn2 = types.InlineKeyboardButton("📢 Наш канал", url="https://t.me/grudikchanel")
    markup.add(btn1, btn2)
    username = message.from_user.first_name

    bot.send_message(message.chat.id, f'🎤 Привет - {username}!\n\n🎤Я RapperBot, у меня есть более 100+ карточек с рэперами!😎🔥\nЗдесь ты найдёшь факты и эксклюзивные карточки по любимым артистам 📀\nОткрывай карточки, изучай и пополняй свои знания о хип-хопе 💥🎶\n\nЕщё больше информации о боте по команде /help или кнопке ниже👇', reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_command(message):
    markup = types.InlineKeyboardMarkup()
    btn2 = types.InlineKeyboardButton('📞 Поддержка', callback_data='support')
    markup.add(btn2)
    bot.send_message(message.chat.id, '<b>🎤 RapperBot | Помощь</b>\n\n📌 Команды:\n<blockquote>/start — запуск бота\n/help — помощь по боту\n/profile - посмотреть профиль\n/rapper — выбить карточку\n/coll или /collection — твоя коллекция\n/promo «ПРОМОКОД» - активировать промокод</blockquote>\n\n<b>📂Если возникли проблемы, ошибки. Можете обратить по кнопке ниже👇</b>', reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['support'])
def support(message):
    text = '''
📌 <b>ПОДДЕРЖКА

Если у тебя возникла проблема с ботом — отправь заявку хелперу -> <a href="tg://user?id=8703166955">поддержка</a> 💬</b>

────────────────────

🧾 <b>ФОРМА ОБРАЩЕНИЯ: </b>

<blockquote>• Суть проблемы
• Когда появилась ошибка (время по МСК)
• Скриншот (если есть)
• юз / ник пользователя</blockquote>

────────────────────

⚠️ <b>ПРАВИЛА:</b>

<blockquote>• Описывай проблему чётко и по делу
• 1 заявка = 1 проблема
• Не дублируй сообщения
• Без спама и оскорблений</blockquote>

────────────────────

⏱️ Ответ даётся в течении 12 часов.
'''
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['profile'])
def profile(message):
    username = message.from_user.first_name

    user_id = message.from_user.id

    user_cards, _, _, _ = get_user(user_id)
    progress = len(user_cards)
    total_cards = len(rappers)
    percent = round((progress / total_cards) * 100, 1)

    def get_rank(progress, total):
        percent = (progress / total) * 100
        if percent == 100:
            return '👑 Легенда'
        elif percent >= 75:
            return '💎 Коллекционер'
        elif percent >= 50:
            return '🔥 Профессионал'
        elif percent >= 25:
            return '🎧 Фанат'
        else:
            return '👶 Новичок'
        
    rank = get_rank(progress, total_cards)
    text = f'''👤 Профиль - <b>{username}</b>

🆔 ID: <b>{user_id}</b>

📊 Прогресс: <b>{progress} / {total_cards}</b>
📈 Собрано: <b>{percent}%</b>

🏆 Ранг: <b>{rank}</b>
'''
    
    photos = bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        file_id = photos.photos[0][0].file_id
        bot.send_photo(message.chat.id, file_id, caption=text, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, text, parse_mode='HTML')


def get_user(user_id):
    cursor.execute("SELECT cards, last_drop, promo_used, progress_time FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        cards, last_drop, promo_used, progress_time = result
        if cards:
            cards = cards.split(',')
        else:
            cards = []

        if promo_used:
            promo_used = promo_used.split(',')
        else:
            promo_used = []
        return cards, last_drop, promo_used, progress_time
    else:
        return [], 0, [], 0
    
def save_user(user_id, cards, last_drop, promo_used, progress_time):
    cards_str = ",".join(cards)
    promo_str = ','.join(promo_used)

    cursor.execute("""INSERT OR REPLACE INTO users (user_id, cards, last_drop, promo_used, progress_time) VALUES (?, ?, ?, ?, ?)""", (user_id, cards_str, last_drop, promo_str, progress_time))
    conn.commit()

@bot.message_handler(commands=['rapper'])
def rap(message):
    user_id = message.from_user.id
    user_cards, last_drop, promo_used, progress_time = get_user(user_id)
    current_time = time.time()

    if current_time - last_drop < 43200:
        remaining = int(43200 - (current_time -last_drop))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        bot.send_message(message.chat.id, f'⏳ Подожди {hours}ч. {minutes}м. перед следующим использованием!')
        return

    total_cards = len(rappers)
    
    if len(user_cards) == total_cards:
        bot.send_message(message.chat.id, 'Ты собрал все карточки!\nСпасибо что поучаствовал(а) в моем маленьком проекте!\nВ следующих обновления будет еще больше карточек!')
        return
    
    available_cards = [r for r in rappers if r['name'] not in user_cards]
    weights = [r['chance'] for r in available_cards]
    rapper = random.choices(available_cards, weights = weights, k=1)[0]

    user_cards.append(rapper['name'])
    progress_time = time.time()
    save_user(user_id, user_cards, current_time, promo_used, progress_time)
    
    progress = len(user_cards)
    try:
        with open(rapper['image'], 'rb') as photo:
            bot.send_photo(message.chat.id, photo,
                            caption=f"🎉 <b>Тебе выпала карточка!</b>\n\n🎧 <b>{rapper['name']}</b>\n\n🌟Редкость: {RARITY[rapper['rarity']]}\n💡Факт: {rapper['fact']}\n\n📊 Прогресс: {progress} / {total_cards}\n\n⏳Следующий раз будет через 12 часов!", 
                            parse_mode='HTML'
                            )
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "⚠️ Ошибка загрузки картинки, мы приносим извинения!\n Если вы увидели это сообщение напишите в поддержку!\n\n 😔 Спасибо за понимание!")

@bot.message_handler(commands=['promo'])
def promo(message):
    user_id = message.from_user.id
    user_cards, last_drop,promo_used, progress_time = get_user(user_id)

    member = bot.get_chat_member('@grudikchanel', message.from_user.id)
    if member.status in ['left', 'kicked']:
        markup = types.InlineKeyboardMarkup()
        btn2 = types.InlineKeyboardButton("➕ Подписаться", url="https://t.me/grudikchanel")
        markup.add(btn2)
        bot.send_message(message.chat.id, '❌ Подпишитесь на канал что бы использовать промокод!', reply_markup=markup)
        return

    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, '❌ Введите промокод: /promo «ПРОМОКОД»')
        return
    
    promo_code = message.text.split()[1].upper()

    with open('promo.json', 'r', encoding='utf-8') as f:
        promos = json.load(f)

    promo_found = None

    for promo in promos:
        if promo['code'] == promo_code:
            promo_found = promo
            break

    if promo_code in promo_used:
        bot.send_message(message.chat.id, '❌ Ты уже использовал этот промокод!')
        return

    if not promo_found:
        bot.send_message(message.chat.id, '❌ Промокод не существует!')
        return
    
    if promo_found['uses'] <= 0:
        bot.send_message(message.chat.id, '❌ Промокод больше не активен!')
        return
    
    with open("rappers.json", "r", encoding='utf-8') as f:
        rappers = json.load(f)

    if promo_found['type'] == 'random':
        avaible = [
            rapper for rapper in rappers
            if rapper["name"] not in user_cards
            ]

        if not avaible:
            bot.reply_to(message, "❌ У тебя уже есть все карточки!")
            return
        
        reward_rapper = random.choice(avaible)

    elif promo_found['type'] == 'fixed':
        reward_rapper = None
        for r in rappers:
            if r['name'] == promo_found['reward']:
                reward_rapper = r
                break

        if reward_rapper['name'] in user_cards:
            bot.reply_to(message, "❌ У тебя уже есть эта карточка!")
            return
        
        if not reward_rapper:
            bot.send_message(message.chat.id, '❌ Ошибка: награда не найдена')
            return

    elif promo_found['type'] == 'rarity':
        filtered = [r for r in rappers if r['rarity'] == promo_found['rarity'] and r["name"] not in user_cards]

        if not filtered:
            bot.send_message(message.chat.id, '❌ Ошибка: награда не найдена')
            return

        reward_rapper = random.choice(filtered)
        
        if not filtered:
            bot.reply_to(message, "❌ Утебя уже есть все карточки этой редкости!")
            return
        
    else:
        bot.send_message(message.chat.id, '❌ Неизвестный тип промокода')
        return
    
    promo_found['uses'] -= 1

    with open('promo.json', 'w', encoding='utf-8') as f:
        json.dump(promos, f, ensure_ascii=False, indent=4)

    user_id = message.from_user.id
    user_cards, last_drop, promo_used, progress_time = get_user(user_id)

    if reward_rapper['name'] not in user_cards:
        user_cards.append(reward_rapper['name'])
        progress_time = time.time()

    promo_used.append(promo_code)
    save_user(user_id, user_cards, last_drop, promo_used, progress_time)

    progress = len(user_cards)
    total_cards = len(rappers)

    with open(reward_rapper['image'], 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption= 
                       f'🎁 <b>Промокод активирован!</b>\n\n'
                       f'🎧 <b>{reward_rapper["name"]}</b>\n\n'
                       f'🌟 Редкость: {RARITY[reward_rapper["rarity"]]}\n'
                       f'💡  Факт: {reward_rapper["fact"]}\n\n'
                       f'📊 Прогресс: {progress} / {total_cards}',
                       parse_mode='HTML'
                       )

@bot.message_handler(commands=['collection', 'coll'])
def collection(message):
    user_id = message.from_user.id
    user_cards, _, _, _  = get_user(user_id)

    if not user_cards:
        bot.send_message(message.chat.id, '❌ У тебя пока нет карточек!\nИспользуй - /rapper')
        return

    progress = len(user_cards)
    total_cards = len(rappers)

    markup = types.InlineKeyboardMarkup(row_width=2)

    btn1 = types.InlineKeyboardButton('🔴 Мифические', callback_data="coll_mythic")
    btn2 = types.InlineKeyboardButton('🟡 Легендарные', callback_data="coll_legendary")
    btn3 = types.InlineKeyboardButton('🟣 Эпические', callback_data="coll_epic")
    btn4 = types.InlineKeyboardButton('🟢 Редкие', callback_data="coll_rare")
    btn5 = types.InlineKeyboardButton('⚪️ Обычные', callback_data="coll_common")

    markup.add(btn1, btn2, btn3, btn4, btn5)

    bot.send_message(message.chat.id, 
                     f'<b>🎒 Твоя коллекция:</b>\n\n'
                     f'📊 Прогресс: <b>{progress} / {total_cards}</b>\n\n'
                     f'👇 Выбери редкость', 
                     parse_mode='HTML', reply_markup=markup
                     )

    
@bot.message_handler(commands=['top'])
def top_player(message):
    conn = sqlite3.connect("bjt.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, cards, progress_time FROM users")
    users = cursor.fetchall()
    conn.close()
    leaderboard = []

    for user_id, cards_json, progress_time in users:
        try:
            if cards_json:
                cards = cards_json.split(',')
            else:
                cards = []

            card_count = len(cards)

            try:
                user = bot.get_chat(user_id)
                username = user.first_name

            except:
                username = f"ID {user_id}"
            leaderboard.append((username, card_count, progress_time))

        except:
            continue
    leaderboard.sort(key=lambda x: (-x[1], x[2]))
    text = "🏆 <b>Топ коллекционеров:</b>\n\n"
    medals = ["🥇", "🥈", "🥉 "]

    for i, (username, count, _) in enumerate(leaderboard[:10]):

        if i < 3:
            place = medals[i]
        else:
            place = f"{i+1}."

        text += f"{place} <b>{username}</b> - {count} карточек\n"

    bot.send_message(message.chat.id, text, parse_mode="HTML")

        
        

@bot.message_handler(content_types=['text'])
def echo(message):
    if message.text.lower() == 'помощь':
        help_command(message)
        return
    elif message.text.lower() in ['репер', 'рэпер']:
        rap(message)
        return
    elif message.text.lower() == 'коллекция':
        collection(message)
        return
    elif message.text.lower() == 'топ':
        top_player(message)
        return
    elif message.text.lower() == 'профиль':
        profile(message)
        return
    
    """
    elif message.text.lower() == 'сука':
        bot.send_message(message.chat.id, 'Ты шо дебил?')
        bot.send_message(message.chat.id, 'Незя матюки казать!')
        bot.send_message(message.chat.id, '70 лет ада вывели на матюки')
        bot.send_message(message.chat.id, 'Незя матюки казати бля')
        bot.send_message(message.chat.id, 'ты шо дебил чи шо ты')
        bot.send_message(message.chat.id, 'фак ю') 
    """


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'help': 
        help_command(call.message)
    elif call.data == 'rapper':
        rap(call.message)
    elif call.data == 'support':
        support(call.message)
    elif call.data.startswith("coll_"):

        rarity = call.data.replace("coll_", "")

        user_id = call.from_user.id
        user_cards, _, _, _ = get_user(user_id)

        rarity_names = {
            'mythic': '🔴 Мифических',
            'legendary': '🟡 Легендарных',
            'epic': '🟣 Эпических',
            'rare': '🟢 Редких',
            'common': '⚪ Обычных'
        }

        filtered = [
            r['name']
            for r in rappers
            if r['rarity'] == rarity
            and r['name'] in user_cards
        ]

        if filtered:
            text = f"{rarity_names[rarity]} карточки:\n\n"

            for name in filtered:
                text += f"• {name}\n"

        else:
            text = f"{rarity_names[rarity]} карточек пока нет 😔"

        markup = types.InlineKeyboardMarkup(row_width=2)

        btn1 = types.InlineKeyboardButton(
            "🔴 Мифики",
            callback_data="coll_mythic"
        )

        btn2 = types.InlineKeyboardButton(
            "🟡 Легендарные",
            callback_data="coll_legendary"
        )

        btn3 = types.InlineKeyboardButton(
            "🟣 Эпики",
            callback_data="coll_epic"
        )

        btn4 = types.InlineKeyboardButton(
            "🟢 Редкие",
            callback_data="coll_rare"
        )

        btn5 = types.InlineKeyboardButton(
            "⚪ Обычные",
            callback_data="coll_common"
        )

        markup.add(btn1, btn2, btn3, btn4, btn5)

        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    else:
        bot.send_message(call.message.chat.id, 'кнопка пока в разработке')
    bot.answer_callback_query(call.id)


bot.infinity_polling(timeout=30, long_polling_timeout=30)