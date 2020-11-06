import re
from datetime import datetime
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from loader import dp, bot
from keyboards.inline.setup_button_inline import setup_button
from utils.db_api import quick_commands as commands


@dp.message_handler(text="Настройки")
async def setup_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно настроить",
                         reply_markup=setup_button)


@dp.callback_query_handler(text_contains="sub_on_schedule")  # Not finished
async def subscribe_to_the_schedule(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer('Укажите время, в которое хотите получать расписание. '
                              'Например, "12:45"')
    await StatesOfBot.schedule_state.set()


@dp.message_handler(state=StatesOfBot.schedule_state)
async def set_subscribe(message: Message, state: FSMContext):
    if re.match(r'^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$', message.text):
        await message.answer(f"Время получения расписания установлено на: {message.text}")
        await commands.update_user_mailing_time(mailing_time=message.text,
                                                id=message.from_user.id)
        await state.finish()
    else:
        await message.answer(f"Указано некорректное время. Попробуйте еще раз.")


@dp.callback_query_handler(text_contains="advertisement")  # Completed
async def advertising(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer("Подробности @scytheofdeath")


@dp.callback_query_handler(text_contains="reset_setup", state=None)  # Not finished
async def reset_settings(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer("Настройки группы и подписки сброшены")
    await call.message.answer(f'Здравствуйте, {call.message.chat.full_name}!\n'
                              f'Введите название вашей группы, скопировав из списка\n'
                              f'Например: 2ИС-2', reply_markup=ReplyKeyboardRemove())

    file_name_group = open('/home/alien/PycharmProjects/ScheduleBotTelegram/data/name_groups.txt')
    await bot.send_document(chat_id=call.message.chat.id, document=file_name_group)
    file_name_group.close()

    await commands.delete_user_name_group(id=call.message.chat.id)
    await commands.delete_user_mailing_time(id=call.message.chat.id)
    await StatesOfBot.start_state.set()
