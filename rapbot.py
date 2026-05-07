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

cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, cards TEXT, last_drop REAL, promo_used TEXT)''')
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

    user_cards, _, _ = get_user(user_id)
    progress = len(user_cards)
    total_cards = len(rappers)

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
🏆 Ранг: <b>{rank}</b>
'''
    
    photos = bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        file_id = photos.photos[0][0].file_id
        bot.send_photo(message.chat.id, file_id, caption=text, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, text, parse_mode='HTML')


def get_user(user_id):
    cursor.execute("SELECT cards, last_drop, promo_used FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        cards, last_drop, promo_used = result
        if cards:
            cards = cards.split(',')
        else:
            cards = []

        if promo_used:
            promo_used = promo_used.split(',')
        else:
            promo_used = []
        return cards, last_drop, promo_used
    else:
        return [], 0, []
    
def save_user(user_id, cards, last_drop, promo_used):
    cards_str = ",".join(cards)
    promo_str = ','.join(promo_used)

    cursor.execute("""INSERT OR REPLACE INTO users (user_id, cards, last_drop, promo_used) VALUES (?, ?, ?, ?)""", (user_id, cards_str, last_drop, promo_str))
    conn.commit()

@bot.message_handler(commands=['rapper'])
def rap(message):
    user_id = message.from_user.id
    user_cards, last_drop, promo_used = get_user(user_id)
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
    save_user(user_id, user_cards, current_time, promo_used)
    
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
    user_cards, last_drop,promo_used = get_user(user_id)

    member = bot.get_chat_member('@grudikchanel', message.from_user.id)
    if member.status not in ['member', 'creator', 'administrator']:
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
        reward_rapper = random.choice(rappers)

    elif promo_found['type'] == 'fixed':
        reward_rapper = None
        for r in rappers:
            if r['name'] == promo_found['reward']:
                reward_rapper = r
                break
        if not reward_rapper:
            bot.send_message(message.chat.id, '❌ Ошибка: награда не найдена')
            return

    elif promo_found['type'] == 'rarity':
        filtered = [r for r in rappers if r['rarity'] == promo_found['rarity']]

        reward_rapper = random.choice(filtered)

        if not reward_rapper:
            bot.send_message(message.chat.id, '❌ Ошибка: награда не найдена')
            return
        
    else:
        bot.send_message(message.chat.id, '❌ Неизвестный тип промокода')
        return
    
    promo_found['uses'] -= 1

    with open('promo.json', 'w', encoding='utf-8') as f:
        json.dump(promos, f, ensure_ascii=False, indent=4)

    user_id = message.from_user.id
    user_cards, last_drop, promo_used = get_user(user_id)

    if reward_rapper['name'] not in user_cards:
        user_cards.append(reward_rapper['name'])

    promo_used.append(promo_code)
    save_user(user_id, user_cards, last_drop, promo_used)
    bot.send_message(message.chat.id, f'🎁<b>Промокод активирован!</b>\n\n🎧Ты получил: <b>{reward_rapper["name"]}</b>\n📊Прогресс: {len(user_cards)} карточки (-ек)', parse_mode='HTML')

@bot.message_handler(commands=['collection', 'coll'])
def collection(message):
    user_id = message.from_user.id
    user_cards, _, _  = get_user(user_id)

    total_cards = len(rappers)
    user_collection = []

    if not user_cards:
        bot.send_message(message.chat.id, '❌ У тебя пока нет карточек!\nИспользуй - /rapper')
        return

    for rapper in rappers:
        if rapper['name'] in user_cards:
            user_collection.append(rapper)
    collections = {
        'mythic': [],
        'legendary': [],
        'epic': [],
        'rare': [],
        'common': []
    }
    for rapper in user_collection:
        rarity = rapper['rarity']
        collections[rarity].append(rapper['name'])

    collection_text = '🎒 Твоя коллекция:\n\n'
    if collections['mythic']:
        collection_text += '🔴 Мифические:\n'
        for name in collections['mythic']:
            collection_text += f'• {name}\n'
        collection_text += "\n"

    if collections['legendary']:
        collection_text += '🟡 Легендарные:\n'
        for name in collections['legendary']:
            collection_text += f'• {name}\n'
        collection_text += "\n"

    if collections['epic']:
        collection_text += '🟣 Эпические:\n'
        for name in collections['epic']:
            collection_text += f'• {name}\n'
        collection_text += "\n"

    if collections['rare']:
        collection_text += '🟢 Редкие:\n'
        for name in collections['rare']:
            collection_text += f'• {name}\n'
        collection_text += "\n"

    if collections['common']:
        collection_text += '⚪️ Обычные:\n'
        for name in collections['common']:
            collection_text += f'• {name}\n'
        collection_text += "\n"
    
    progress = len(user_cards)
    collection_text += f'📊 Прогресс: {progress} / {total_cards}'

    bot.send_message(message.chat.id, collection_text)

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


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'help':
        help_command(call.message)
    elif call.data == 'rapper':
        rap(call.message)
    elif call.data == 'support':
        support(call.message)
    else:
        bot.send_message(call.message.chat.id, 'кнопка пока в разработке')
    bot.answer_callback_query(call.id)


bot.infinity_polling()