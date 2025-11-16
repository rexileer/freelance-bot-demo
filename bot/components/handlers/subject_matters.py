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

async def unsubscribed_subject_matters(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, selected_matter = callback.data.split(":")
    state_data = await state.get_data()
    selected_matters = state_data.get("selected_matters", [])
    if selected_matter:
        if int(selected_matter) not in selected_matters:
            selected_matters.append(int(selected_matter))
        else:
            selected_matters.remove(int(selected_matter))
    await state.update_data(selected_matters=selected_matters)
    subject_matters = await postgres_connector.get_unsubscribed_subject_matters(callback.from_user.id)
    keyboard = await kb.unsubscribed_subject_matters_kb(subject_matters, selected_matters)
    if not selected_matter:
        await callback.message.answer_photo(FSInputFile("bot/media/category.png"),
                                            caption=await custom_text("Выберите категории из списка", "select_unsubscribed_subject_matters_list_text"),
                                            reply_markup=keyboard,
                                            parse_mode="HTML")
        await callback.message.delete()
    else:
        await callback.message.edit_reply_markup(reply_markup=keyboard)


async def get_tariffs(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    selected_matters = state_data.get("selected_matters", [])
    if not selected_matters:
        return await callback.answer(await custom_text("Выберите хотя бы одну категорию", "select_matter_error"))
    tariffs = await postgres_connector.get_tariffs()
    keyboard = await kb.tariffs_kb(tariffs)
    try:
        await callback.message.edit_text(await custom_text("Выберите тариф из списка:", "select_tariff_text"),
                                         reply_markup=keyboard)
    except:
        await callback.message.answer(await custom_text("Выберите тариф из списка:", "select_tariff_text"),
                                         reply_markup=keyboard)
        await callback.message.delete()


async def select_tariff(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, tariff_id = callback.data.split(":")
    await state.update_data(tariff_id=int(tariff_id))
    keyboard = await kb.promo_code_binary()
    await callback.message.edit_text(await custom_text("У вас есть промокод?", "promo_code_question"),
                                     reply_markup=keyboard)

def calculate_signature(*args) -> str:
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def generate_payment_link(
    merchant_login: str,  # Merchant login
    merchant_password_1: str,  # Merchant password
    cost: decimal,  # Cost of goods, RU
    number: int,  # Invoice number
    description: str,  # Description of the purchase
    is_test = 0,
    previous_invid = None,
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
        'InvoiceID': number,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test
    }
    if previous_invid:
        robokassa_payment_url = "https://auth.robokassa.ru/Merchant/Recurring"
        data["PreviousInvoiceID"] = previous_invid
    else:
        data["Recurring"] = True
    return f'{robokassa_payment_url}?{parse.urlencode(data)}'


async def send_invoice(state, bot, user_id, promo_code=None):
    state_data = await state.get_data()
    payment_text = "Выбранные категории:\n"
    count_matters = 0
    async for matter in await postgres_connector.get_selected_subject_matters(state_data["selected_matters"]):
        count_matters += 1
        payment_text += f"{matter.name}\n"
    tariff = await postgres_connector.get_tariff_by_id(state_data["tariff_id"])
    payment_amount = tariff.price * count_matters
    payment_text += f"Тариф: {tariff.title}\n"
    if promo_code:
        payment_amount = payment_amount / 100 * (100 - promo_code.discount)
        payment_text += f"\nСкидка по промокоду: {promo_code.discount}%\n"
    payment_text += f"Итого: {payment_amount}\n"
    check = await postgres_connector.create_empty_check(f'tariff_payment:{state_data["tariff_id"]}:{repr(state_data["selected_matters"])}:{payment_amount}', user_id)
    await postgres_connector.add_payment(user_id, tariff, check.id)
    payment_link = generate_payment_link(merchant_login="FreelanceBot",
                      merchant_password_1="hkrZG2C8geFBpZv51ZQ1",
                      cost=100.0,
                      number=check.id,
                      description="TestPayment",
                      is_test=1)
    keyboard = await kb.payment_kb(payment_link)
    await bot.send_message(text="Оплата подписки", chat_id=user_id, reply_markup=keyboard)
    # return await bot.send_invoice(
    #     chat_id=user_id,
    #     title=f"Оплата подписки",
    #     description=payment_text,
    #     payload=f'tariff_payment:{state_data["tariff_id"]}:{repr(state_data["selected_matters"])}:{payment_amount}',
    #     provider_token=os.getenv("PROVIDER_TOKEN"),
    #     currency='RUB',
    #     start_parameter='bot',
    #     prices=[types.LabeledPrice(
    #         label="Руб", amount=100 * 100
    #     )],
    #     reply_markup=keyboard
    # )

async def promo_code_binary(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, action = callback.data.split(":")
    action = bool(int(action))
    if action:
        await callback.message.edit_text(await custom_text("Введите промокод", "select_promo_code_question"))
        await state.set_state(UserFactory.promo_code)
    else:
        if not await postgres_connector.get_user_subscription_existence(callback.from_user.id):
            await send_invoice(state, bot, callback.from_user.id)
            await callback.message.delete()
        else:
            keyboard = await kb.change_payment_varios()
            text = await custom_text(f'Выберите способ оплаты:', "change_payment_varios_text")
            await callback.message.edit_text(text, reply_markup=keyboard)


async def change_payment_varios(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, action = callback.data.split(":")
    data = await state.get_data()
    if data.get("promo_code", None):
        promo_code = await postgres_connector.get_promo_code_by_name(data.get("promo_code", None))
    else:
        promo_code = None
    if action == "card":
        await send_invoice(state, bot, callback.from_user.id, promo_code)
        await callback.message.delete()
    else:
        state_data = await state.get_data()
        count_matters = 0
        async for matter in await postgres_connector.get_selected_subject_matters(state_data["selected_matters"]):
            count_matters += 1
        tariff = await postgres_connector.get_tariff_by_id(state_data["tariff_id"])
        payment_amount = tariff.price * count_matters
        if promo_code:
            payment_amount = payment_amount / 100 * (100 - promo_code.discount)
        user = await postgres_connector.get_user_by_id(callback.from_user.id)
        if user.balance < payment_amount:
            return await callback.answer(await custom_text(f'Недостаточно средств', "low_balance"))
        await postgres_connector.take_away_money(user, payment_amount)
        await postgres_connector.top_up_ref_balance(callback.from_user.id, payment_amount)
        await postgres_connector.create_subscription(state_data["selected_matters"], state_data["tariff_id"], callback.from_user.id)
        keyboard = await kb.menu_button(await postgres_connector.get_user_subscription_existence(callback.from_user.id),
                                        user.search_switch, trial_subscription_expired=user.trial_subscription_expired)
        text = await custom_text(f'Оплата прошла успешно', "success_payment_order_direction")
        await callback.message.answer_photo(FSInputFile("bot/media/succ_payment.png"),
                                   caption=text,
                                   reply_markup=keyboard,
                                   parse_mode="HTML")
        await callback.message.delete()


async def select_promo_code(message: types.Message, state: FSMContext, bot: Bot):
    promo_code = await postgres_connector.get_promo_code_by_name(message.text)
    if not promo_code:
        keyboard = await kb.promo_code_binary()
        return await message.answer(await custom_text("Промокод не найден, ввести еще раз?", "promo_code_question_retry"),
                                         reply_markup=keyboard)
    else:
        await message.answer(await custom_text("Скидка %s% по промокоду '%s' применена", "promo_code_succ", (promo_code.discount, promo_code.name)))
    if not await postgres_connector.get_user_subscription_existence(message.from_user.id):
        await send_invoice(state, bot, message.from_user.id, promo_code)
    else:
        await state.update_data(promo_code=promo_code)
        keyboard = await kb.change_payment_varios()
        text = await custom_text(f'Выберите способ оплаты:', "change_payment_varios_text")
        await message.answer(text, reply_markup=keyboard)


async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def success_payment(message: types.Message):
    _, tariff_id, selected_matters, payment_amount = message.successful_payment.invoice_payload.split(":")
    tariff_id, selected_matters, payment_amount = int(tariff_id), eval(selected_matters), int(payment_amount)
    await postgres_connector.top_up_ref_balance(message.from_user.id, payment_amount)
    await postgres_connector.create_subscription(selected_matters, tariff_id, message.from_user.id)
    user = await postgres_connector.get_user_by_id(message.from_user.id)
    keyboard = await kb.menu_button(await postgres_connector.get_user_subscription_existence(message.from_user.id), user.search_switch, trial_subscription_expired=user.trial_subscription_expired)
    text = await custom_text(f'Оплата прошла успешно', "success_payment_order_direction")
    await message.answer_photo(FSInputFile("bot/media/succ_payment.png"),
                                        caption=text,
                                        reply_markup=keyboard,
                                        parse_mode="HTML")
    await message.delete()


async def add_bid(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    categories = await postgres_connector.get_all_subject_matters()
    keyboard = await kb.add_bid_matters(categories)
    try:
        await callback.message.edit_text(await custom_text("Выберите категорию заявки", "add_bid_category_text"),
                                         reply_markup=keyboard)
    except:
        await callback.message.answer(await custom_text("Выберите категорию заявки", "add_bid_category_text"),
                                         reply_markup=keyboard)
        await callback.message.delete()


async def add_bid_matter(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, selected_matter = callback.data.split(":")
    await state.update_data(selected_matter_id=int(selected_matter))
    await callback.message.edit_text(await custom_text("Введите свои контактные данные", "add_bid_matter_text"),  parse_mode="HTML")
    await state.set_state(BidFactory.author)


async def add_bid_author(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(author=message.text)
    await message.answer(await custom_text("Опишите свою задачу (к задаче можно прикрепить файл\фото\видео)", "add_bid_author_text"),
                                     parse_mode="HTML")
    await state.set_state(BidFactory.content)


async def add_bid_content(message: types.Message, state: FSMContext, bot: Bot):
    file_id = None
    if message.photo:
        file_type = "photo"
        file_id = str(message.photo.pop().file_id)
    elif message.video:
        file_type = "video"
        file_id = message.video.file_id
    elif message.document:
        file_type = "document"
        file_id = message.document.file_id

    if not file_id:
        if message.text:
            data = await state.get_data()
            await postgres_connector.add_bid(data["author"], message.text, [], [data["selected_matter_id"]])
            user = await postgres_connector.get_user_by_id(message.from_user.id)
            keyboard = await kb.in_menu()
            await message.answer(await custom_text("Ваша заявка успешно опубликована", "add_bid_successfully"),
                                 reply_markup=keyboard)
            await state.clear()
        return
    file = await bot.get_file(file_id=file_id)
    file_path = file.file_path
    filetype = file_path.split('.')[-1]
    fpath = f"bot/media/{file_id}.{filetype}"
    await state.update_data({f"media_group_{file_id}": {"path": fpath, "file_type": file_type},
                             "last_photo_message_at": int(time.time())})
    await bot.download_file(file_path, fpath)
    if message.caption:
        await state.update_data({"caption": message.caption})

    data = await state.get_data()
    if not data.get("selected_first_photo", None):
        await state.update_data(selected_first_photo=file_id)
        while True:
            data = await state.get_data()
            if int(time.time()) - data["last_photo_message_at"] < 5:
                await asyncio.sleep(1)
            else:
                break
        state_data = await state.get_data()
        if state_data["selected_first_photo"] == file_id:
            files = []
            for key, value in state_data.items():
                if key.startswith("media_group_"):
                    files.append({"tg_file_id": re.sub("media_group_", "", key),
                                  "file_type": value["file_type"],
                                  "path": value["path"]})
            await postgres_connector.add_bid(state_data["author"], state_data.get("caption", None), files, [state_data["selected_matter_id"]])
            user = await postgres_connector.get_user_by_id(message.from_user.id)
            keyboard = await kb.menu_button(await postgres_connector.get_user_subscription_existence(message.from_user.id), user.search_switch, trial_subscription_expired=user.trial_subscription_expired)
            await message.answer(await custom_text("Ваша заявка успешно опубликована", "add_bid_successfully"), reply_markup=keyboard)
            await state.clear()


async def free_sub(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    subject_matters = await postgres_connector.get_unsubscribed_subject_matters(callback.from_user.id)
    keyboard = await kb.free_sub_kb(subject_matters)
    try:
        await callback.message.edit_text(await custom_text("Выберите категорию из списка", "free_sub_text"),
                                         reply_markup=keyboard)
    except:
        try:
            await callback.message.edit_caption(
                caption=await custom_text("Выберите категории из списка", "free_sub_text"),
                reply_markup=keyboard)
        except:
            await callback.message.answer(await custom_text("Выберите категории из списка", "free_sub_text"),
                                             reply_markup=keyboard)
            await callback.message.delete()


async def free_sub_selected(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, sub_id = callback.data.split(":") #create_subscription
    await postgres_connector.create_free_sub(int(sub_id), callback.from_user.id)
    keyboard = await kb.in_menu()
    try:
        await callback.message.edit_caption(
            caption=await custom_text("Пробная подписка на 3 дня успешно приобретена", "subfreetext"),
            reply_markup=keyboard)
    except:
        await callback.message.answer(await custom_text("Пробная подписка на 3 дня успешно приобретена", "subfreetext"),
                                      reply_markup=keyboard)
        await callback.message.delete()


def register_handlers(dp: Dispatcher):
    dp.callback_query.register(unsubscribed_subject_matters, F.data.startswith("unsubscribed_subject_matters:"))
    dp.callback_query.register(promo_code_binary, F.data.startswith("promo_code_binary:"))
    dp.callback_query.register(change_payment_varios, F.data.startswith("change_payment_varios:"))
    dp.callback_query.register(get_tariffs, F.data == "get_tariffs")
    dp.callback_query.register(add_bid, F.data == "add_bid")
    dp.callback_query.register(select_tariff, F.data.startswith("select_tariff:"))
    dp.callback_query.register(add_bid_matter, F.data.startswith("add_bid_matter:"))
    dp.callback_query.register(free_sub_selected, F.data.startswith("free_sub_selected:"))
    dp.callback_query.register(free_sub, F.data.startswith("free_sub:"))
    dp.message.register(select_promo_code, UserFactory.promo_code, F.text)
    dp.message.register(add_bid_author, BidFactory.author, F.text)

    dp.message.register(add_bid_content, BidFactory.content, F.photo)
    dp.message.register(add_bid_content, BidFactory.content, F.file)
    dp.message.register(add_bid_content, BidFactory.content, F.video)
    dp.message.register(add_bid_content, BidFactory.content, F.text)

    dp.pre_checkout_query.register(process_pre_checkout_query)
    dp.message.register(success_payment, F.successful_payment and
                        F.successful_payment.invoice_payload.startswith("tariff_payment"))