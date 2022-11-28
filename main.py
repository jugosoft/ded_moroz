import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import csv
import pandas as pd
import random
import os

TOKEN = os.getenv('TOKEN')
URL_PHOTO = os.getenv('URL_PHOTO')

bot = Bot(token=TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['hollyRandom'])
async def random_Santas(message: types.Message):
    while True:
        try:
            data_csv = pd.read_csv('sdklaus_data.csv', encoding='Windows-1251')
            donee_finish = []
            santa_finish = []
            id = data_csv['name_santas'].tolist()

            for i in range(len(id)):
                santa_id = id[i]
                santa_finish.append(id[i])
                donee_list = data_csv['name_santas'].tolist()
                for finish in donee_finish:
                    donee_list.remove(finish)
                if id[i] in donee_list:
                    donee_list.remove(id[i])
                print(i, santa_id, id, donee_list)
                r = random.randint(0, len(donee_list) - 1)
                print(r)
                donee_id = donee_list[r]
                donee_list.append(id[i])
                donee_finish.append(donee_id)
                print(santa_id, donee_id)
        except:
            continue
        break
    data_csv = pd.read_csv('sdklaus_data.csv', encoding='Windows-1251')
    data_csv['name_id'] = data_csv['name_id'].astype('str')
    id_list = data_csv['name_id'].tolist()
    name_donne_list = data_csv['name_santas'].tolist()
    preferences_list = data_csv['preferences_user'].tolist()
    for index in range(len(santa_finish)):
        index_santa = name_donne_list.index(santa_finish[index])
        chat_id_santa = id_list[index_santa]
        index_donee = name_donne_list.index(donee_finish[index])
        name_donee = name_donne_list[index_donee]
        preferences_donne = preferences_list[index_donee]
        await bot.send_message(chat_id=chat_id_santa,
                                text=f'🦊Твой подопечный: {name_donee}, \n\n 🌟Его увлечения: {preferences_donne}')
        #await bot.send_message(chat_id=-823023035, text = f'Народ, у нас тут пара: \n\n Санта: {name_donne_list[index_santa]} \n\n Подопечный: {name_donee}')



@dp.message_handler(commands=['start_game'])
async def start_msg(message: types.Message):
    field_names= ["full_name", "name_id", "url_user",'name_user','login_user','name_santas','preferences_user']
    with open('sdklaus_data.csv', mode="w", newline='', encoding='Windows-1251') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)

# Создаём форму и указываем поля
class Form(StatesGroup):
    name = State() # ФИО
    preferences = State() # Предпочтения
    santas_login = State() # ИД и логины участников

@dp.message_handler(commands=['start'])
async def start_msg(message: types.Message):

    data_csv = pd.read_csv('sdklaus_data.csv', encoding='Windows-1251')
    data_csv['name_id']=data_csv['name_id'].astype('str')
    id_list = data_csv['name_id'].unique().tolist()
    print(id_list)
    id_txt=str(message.from_user.id)
    print(id_txt)

    if id_txt not in id_list:
        await Form.name.set()
        await bot.send_photo(chat_id=message.chat.id, photo=URL_PHOTO,
        caption='☃️Привет Санта🎅🏻, присаживайся к огоньку🔥, я как раз готовлю список📝 тайныйх Сант, не подскажешь свое ФИО?')
        # await message.reply('☃️Привет Санта🎅🏻, присаживайся к огоньку🔥, я как раз готовлю список📝 тайныйх Сант, не п
    else:

        await message.reply(text=f'Ты уже зарегестрирован, если нужно поменять данные, обращайся к @KatanaMedoeda')



# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('🧹Я все стëр, можно начать заново :)')

# Сюда приходит ответ с именем
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        data['santas_login'] = message.from_user.username
    exit = '/cancel' # Чтобы /cancel как гиперссылка была
    await Form.next()
    await message.reply("🤔Расскажи о своих предпочтениях и увлечениях, так Санте будет проще🎁 \n\n Если произошла ошибка нажми " + exit)


@dp.message_handler(state=Form.preferences)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['preferences'] = message.text
        markup = types.ReplyKeyboardRemove()
        full_name = message.from_user.full_name # полное имя
        name_id = message.from_user.id # ид
        url_user = message.from_user.url # ссылка
        name_user = message.from_user.first_name # имя
        login_user = data['santas_login'] # логин
        name_santas = data['name'] #
        preferences_user = data['preferences'] #
        # хуйня santaList(login_user) = name_santas + 'увлечения: ' + preferences_user
        # Создаем лист со славарем по CSV файл
        santa_list = []
        santa_list.append(full_name)
        santa_list.append(name_id)
        santa_list.append(url_user)
        santa_list.append(name_user)
        santa_list.append(login_user)
        santa_list.append(name_santas)
        santa_list.append(preferences_user)
        # Выгружаем дату обновляем и сохроняем новую
        # field_names = ["full_name", "name_id", "url_user", 'name_user', 'login_user', 'name_santas', 'preferences_user']
        with open('sdklaus_data.csv', 'a', encoding='Windows-1251') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(santa_list)
        #await bot.send_message(chat_id=-823023035, text=f'⚡️Так народ, у нас новый САНТА: \n\n 📝Полное имя: {full_name} \n 🛰ид: {name_id} \n 🎅🏻ФИО: {name_santas} \n ☃️Увлечения: {preferences_user} \n 🛠Ссылка: {url_user} \n 🐦Имя: {name_user} \n 📲Логин: @{login_user}')
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Твоя анкета: \n\n 😺ФИО:', md.bold(data['name'])),
                md.text('🌟Предпочтения:', md.bold(data['preferences'])), '\n \n Спасибо за регистрацию, я передал данные Санте🙌',
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,

        )


    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
