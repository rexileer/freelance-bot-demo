import re

from aiogram import types
from bot.components.connectors import postgres_connector
from bot.components.keyboards import keyboard as kb
from aiogram import Bot, Dispatcher
from aiogram import F
from bot.components.utils import custom_text
from aiogram.fsm.context import FSMContext
from bot.components.factory import UserFactory, BidFactory
import os
from aiogram.types import PreCheckoutQuery
import time
import asyncio
import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse
from aiogram.types import FSInputFile

async def menu(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await postgres_connector.user_search_switch(callback.from_user.id)
    keyboard = await kb.personal_account_menu(user.search_switch)
    is_sub = await postgres_connector.get_user_subscription_existence(callback.from_user.id)
    menu_text = await custom_text("Выберите пункт меню", "personal_account_menu")
    if is_sub:
        try:
            await callback.message.edit_caption(caption=menu_text, reply_markup=keyboard, parse_mode="HTML")
        except:
            await callback.message.answer_photo(FSInputFile("bot/media/hello.png"), caption=menu_text,
                                                reply_markup=keyboard,
                                                parse_mode="HTML")
            await callback.message.delete()
    else:
        await callback.message.answer_video(FSInputFile("bot/media/home.mp4"), caption=menu_text, reply_markup=keyboard,
                                            parse_mode="HTML")
        await callback.message.delete()


async def switch_search(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await postgres_connector.user_search_switch(callback.from_user.id)
    keyboard = await kb.personal_account_menu(user.search_switch)
    await callback.message.edit_caption(caption=await custom_text("Выберите пункт меню", "personal_account_menu"),
                                     reply_markup=keyboard)



async def profile(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    user = await postgres_connector.user_search_switch(callback.from_user.id)
    keyboard = await kb.profile_kb()
    try:
        await callback.message.edit_text(await custom_text("Баланс: <b>%s</b>₽", "profile_menu", (str(user.balance),)),
                                     reply_markup=keyboard, parse_mode="HTML")
    except:
        try:
            await callback.message.edit_caption(
                caption=await custom_text("Баланс: <b>%s</b>₽", "profile_menu", (str(user.balance),)),
                reply_markup=keyboard, parse_mode="HTML"
            )
        except:
            await callback.message.answer(
                await custom_text("Баланс: <b>%s</b>₽", "profile_menu", (str(user.balance),)),
                reply_markup=keyboard, parse_mode="HTML")
            await callback.message.delete()


async def my_categories(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await postgres_connector.user_search_switch(callback.from_user.id)
    categories = await postgres_connector.get_my_subject_matters(user.id)
    black_list = await postgres_connector.get_black_list_by_user(user)
    keyboard = await kb.my_categories_kb(categories, [matter.id async for matter in black_list], user.search_switch)
    try:
        await callback.message.edit_text(await custom_text("Ваши категории:", "your_categories"),
                                         reply_markup=keyboard, parse_mode="HTML")
    except:
        await callback.message.answer(await custom_text("Ваши категории:", "your_categories"),
                                         reply_markup=keyboard, parse_mode="HTML")
        await callback.message.delete()


async def switch_my_category(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, category_id = callback.data.split(":")
    category_id = int(category_id)
    await postgres_connector.switch_my_category(callback.from_user.id, category_id)
    user = await postgres_connector.get_user_by_id(callback.from_user.id)
    categories = await postgres_connector.get_my_subject_matters(user.id)
    black_list = await postgres_connector.get_black_list_by_user(user)
    keyboard = await kb.my_categories_kb(categories, [matter.id async for matter in black_list], user.search_switch)
    await callback.message.edit_text(await custom_text("Ваши категории:", "your_categories"),
                                     reply_markup=keyboard)


async def top_up_balance(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    keyboard = await kb.back_button("profile")
    await callback.message.edit_text(await custom_text("Введите сумму", "get_amount_for_top_up_balance"),
                                     reply_markup=keyboard)
    await state.set_state(UserFactory.top_up_balance)


def calculate_signature(*args) -> str:
    """Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def generate_payment_link(
    merchant_login: str,  # Merchant login
    merchant_password_1: str,  # Merchant password
    cost: decimal,  # Cost of goods, RU
    number: int,  # Invoice number
    description: str,  # Description of the purchase
    is_test = 0,
    robokassa_payment_url = 'https://auth.robokassa.ru/Merchant/Index.aspx',
) -> str:
    """URL for redirection of the customer to the service.
    """
    signature = calculate_signature(
        merchant_login,
        cost,
        number,
        merchant_password_1
    )

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'InvId': number,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test
    }
    return f'{robokassa_payment_url}?{parse.urlencode(data)}'



async def get_amount(message: types.Message, state: FSMContext, bot: Bot):
    if not message.text.isnumeric():
        keyboard = await kb.back_button("profile")
        return await message.edit_text(await custom_text("Я ожидаю число", "give_me_int_durak_blyat"),
                                         reply_markup=keyboard)
    check = await postgres_connector.create_empty_check(
        f'top_up_balance:{message.text}', message.from_user.id)
    payment_link = generate_payment_link(merchant_login="FreelanceBot",
                                         merchant_password_1="hkrZG2C8geFBpZv51ZQ1",
                                         cost=100.0,
                                         number=check.id,
                                         description="TestPayment",
                                         is_test=1)
    keyboard = await kb.payment_kb(payment_link)
    await bot.send_message(text="Пополнение счета", chat_id=message.from_user.id, reply_markup=keyboard)
    # await bot.send_invoice(
    #     chat_id=message.from_user.id,
    #     title=f"Пополнение счета",
    #     description=f"Пополнение счета на {message.text} рублей",
    #     payload=f'top_up_balance:{message.text}',
    #     provider_token=os.getenv("PROVIDER_TOKEN"),
    #     currency='RUB',
    #     start_parameter='bot',
    #     prices=[types.LabeledPrice(
    #         label="Руб", amount=100 * 100
    #     )],
    #     reply_markup=keyboard
    # )


async def success_payment(message: types.Message):
    _, payment_amount = message.successful_payment.invoice_payload.split(":")
    payment_amount = int(payment_amount)
    await postgres_connector.top_up_user_balance(message.from_user.id, payment_amount)
    user = await postgres_connector.get_user_by_id(message.from_user.id)
    keyboard = await kb.menu_button(await postgres_connector.get_user_subscription_existence(message.from_user.id), user.search_switch, trial_subscription_expired=user.trial_subscription_expired)
    text = await custom_text(f'Оплата прошла успешно', "success_payment_order_direction")
    await message.answer_photo(FSInputFile("bot/media/succ_payment.png"),
                               caption=text,
                               reply_markup=keyboard,
                               parse_mode="HTML")
    await message.delete()


def register_handlers(dp: Dispatcher):
    dp.callback_query.register(menu, F.data == "personal_account")
    dp.callback_query.register(switch_search, F.data == "switch_search")
    dp.callback_query.register(profile, F.data == "profile")
    dp.callback_query.register(my_categories, F.data == "my_categories")
    dp.callback_query.register(top_up_balance, F.data == "top_up_balance")
    dp.callback_query.register(switch_my_category, F.data.startswith("switch_my_category:"))
    dp.message.register(get_amount, UserFactory.top_up_balance, F.text)
    dp.message.register(success_payment, F.successful_payment and
                        F.successful_payment.invoice_payload.startswith("top_up_balance"))