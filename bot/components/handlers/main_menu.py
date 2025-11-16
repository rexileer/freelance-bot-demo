from aiogram import types
from bot.components.connectors import postgres_connector
from bot.components.keyboards import keyboard as kb
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher
from aiogram import F
from bot.components.utils import custom_text
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None


async def start(message: types.Message, state: FSMContext):
    await state.clear()
    name = f"{message.from_user.first_name}{f' {message.from_user.last_name}' if message.from_user.last_name else ''}"
    user = await postgres_connector.get_or_create_user_by_id(message.from_user.id, name)
    ref_id = extract_unique_code(message.text)
    if ref_id:
        if int(ref_id) != message.from_user.id:
            print(ref_id)
            await postgres_connector.add_ref(int(ref_id), message.from_user.id)
    is_sub = await postgres_connector.get_user_subscription_existence(user.id)
    keyboard = await kb.menu_button(is_sub, user.search_switch, trial_subscription_expired=user.trial_subscription_expired)
    if is_sub:
        menu_text = await custom_text('👋Приветствую, %s! Для тех кто подписан', "hello_message_is_sub", formatting_attrs=(name,))
        await message.answer_photo(FSInputFile("bot/media/hello.png"), caption=menu_text, reply_markup=keyboard,
                                            parse_mode="HTML")
    else:
        menu_text = await custom_text('👋Приветствую, %s! Для тех кто не подписан', "hello_message_is_no_sub", formatting_attrs=(name,))
        await message.answer_video(FSInputFile("bot/media/home.mp4"), caption=menu_text, reply_markup=keyboard, parse_mode="HTML")


async def help_command(message: types.Message, state: FSMContext):
    help_text = await custom_text('Текст \help', "help_text_")
    await message.answer(help_text, parse_mode="HTML")



async def in_menu(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    name = f"{callback.from_user.first_name}{f' {callback.from_user.last_name}' if callback.from_user.last_name else ''}"
    user = await postgres_connector.get_or_create_user_by_id(callback.from_user.id, name)
    is_sub = await postgres_connector.get_user_subscription_existence(callback.from_user.id)
    keyboard = await kb.menu_button(is_sub, user.search_switch, trial_subscription_expired=user.trial_subscription_expired)
    if is_sub:
        menu_text = await custom_text('👋Приветствую, %s! Для тех кто подписан', "hello_message_is_sub",
                                      formatting_attrs=(name,))
        try:
            await callback.message.edit_caption(caption=menu_text, reply_markup=keyboard, parse_mode="HTML")
        except:
            await callback.message.answer_photo(FSInputFile("bot/media/hello.png"), caption=menu_text, reply_markup=keyboard,
                                                parse_mode="HTML")
            await callback.message.delete()
    else:
        menu_text = await custom_text('👋Приветствую, %s! Для тех кто не подписан', "hello_message_is_no_sub",
                                      formatting_attrs=(name,))
        await callback.message.answer_video(FSInputFile("bot/media/home.mp4"), caption=menu_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.message.delete()



def register_handlers(dp: Dispatcher):
    dp.message.register(start, CommandStart())
    dp.message.register(help_command, F.text == "/help")
    dp.callback_query.register(in_menu, F.data == "in_menu")
