from aiogram.utils.keyboard import InlineKeyboardBuilder
# from .btn_models import (
# )
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.components.utils import custom_button
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def menu_button(user_subscription_existence=False, user_search=False, trial_subscription_expired=True):
    buttons = [
        [
            InlineKeyboardButton(text=await custom_button("🆕 Хочу получать заявки", "new_user_menu_button1"),
                                 callback_data="unsubscribed_subject_matters:"),
        ], [
            InlineKeyboardButton(text=await custom_button("⏬ Хочу создать заявку", "new_user_menu_button2"),
                                 callback_data="add_bid"),
        ],
    ]
    if not trial_subscription_expired:
        buttons.append([
            InlineKeyboardButton(text=await custom_button("🆓 Пробная подписка", "free_sub"),
                                 callback_data="free_sub:"),
        ])
    buttons.append([
            InlineKeyboardButton(text=await custom_button("⚙️ Поддержка", "support_url"),
                                 url="https://t.me/Nik1ta_Savelev"),
        ],)
    if user_subscription_existence:
        buttons = [
            [
                InlineKeyboardButton(text=await custom_button("🙋‍♂️ Профиль", "profile_kb"), callback_data="profile"),
                # InlineKeyboardButton(text=await custom_button("💾 Полезное", "useful_kb"), callback_data="useful"),
            ], [
                InlineKeyboardButton(text=await custom_button("🆕 Добавить категории", "add_category_new"),
                                     callback_data="unsubscribed_subject_matters:")
            ],[
                InlineKeyboardButton(text=await custom_button("⏬ Хочу создать заявку", "new_user_menu_button2"),
                                     callback_data="add_bid"),
            ],[
                InlineKeyboardButton(text=await custom_button("💸 Реферальная система", "referral_kb"),
                                     callback_data="referral_system"),
            ], [
                InlineKeyboardButton(text="⛔️ Остановить поиск" if user_search else "🦍 Запустить поиск",
                                     callback_data="switch_search"),
            ], [
            InlineKeyboardButton(text=await custom_button("⚙️ Поддержка", "support_url"),
                                 url="https://t.me/Nik1ta_Savelev"),
        ]
        ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def personal_account_menu(user_search):
    buttons = [
            [
                InlineKeyboardButton(text=await custom_button("🙋‍♂️ Профиль", "profile_kb"), callback_data="profile"),
                # InlineKeyboardButton(text=await custom_button("💾 Полезное", "useful_kb"), callback_data="useful"),
            ], [
                InlineKeyboardButton(text=await custom_button("🆕 Добавить категории", "add_category_new"),
                                     callback_data="unsubscribed_subject_matters:")
            ],[
                InlineKeyboardButton(text=await custom_button("⏬ Хочу создать заявку", "new_user_menu_button2"),
                                     callback_data="add_bid"),
            ],[
                InlineKeyboardButton(text=await custom_button("💸 Реферальная система", "referral_kb"),
                                     callback_data="referral_system"),
            ], [
                InlineKeyboardButton(text="⛔️ Остановить поиск" if user_search else "🦍 Запустить поиск",
                                     callback_data="switch_search"),
            ], [
            InlineKeyboardButton(text=await custom_button("⚙️ Поддержка", "support_url"),
                                 url="https://t.me/Nik1ta_Savelev"),
        ]
        ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



async def new_user_menu_button():
    buttons = [
        [
            InlineKeyboardButton(text=await custom_button("🆕 Хочу получать заявки", "new_user_menu_button1"), callback_data="unsubscribed_subject_matters:"),
        ],[
            InlineKeyboardButton(text=await custom_button("⏬ Хочу создать заявку", "new_user_menu_button2"), callback_data="add_bid"),
        ],[
            InlineKeyboardButton(text=await custom_button("⚙️ Поддержка", "support_url"), url="https://t.me/Nik1ta_Savelev"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def unsubscribed_subject_matters_kb(subject_matters, selected_matters):
    buttons = []
    async for subject_matter in subject_matters:
        buttons.append([
            InlineKeyboardButton(text=("✅ " if subject_matter.id in selected_matters else "") + subject_matter.name,
                                 callback_data=f"unsubscribed_subject_matters:{subject_matter.id}")
        ])
    buttons.extend([[
        InlineKeyboardButton(text=await custom_button("🛒 Выбрать тариф", "get_tariffs_kb"), callback_data="get_tariffs"),
        ],[
        InlineKeyboardButton(text=await custom_button("🔙 В меню", "in_menu_button"), callback_data="in_menu"),
    ]])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def free_sub_kb(subject_matters):
    buttons = []
    async for subject_matter in subject_matters:
        buttons.append([
            InlineKeyboardButton(text=subject_matter.name, callback_data=f"free_sub_selected:{subject_matter.id}")
        ])
    buttons.append([
        InlineKeyboardButton(text=await custom_button("🔙 В меню", "in_menu_button"), callback_data="in_menu"),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def tariffs_kb(tariffs):
    buttons = []
    async for tariff in tariffs:
        buttons.append([
            InlineKeyboardButton(text=f"{tariff.title}", callback_data=f"select_tariff:{tariff.id}")
        ])
    buttons.append([
        InlineKeyboardButton(text=await custom_button("🔙 Назад", "back_btn"), callback_data="unsubscribed_subject_matters:"),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def promo_code_binary():
    buttons = [
        [
            InlineKeyboardButton(text=await custom_button("Да", "Yes"), callback_data="promo_code_binary:1"),
            InlineKeyboardButton(text=await custom_button("Нет", "No"), callback_data="promo_code_binary:0"),
        ],
        [InlineKeyboardButton(text=await custom_button("🔙 Назад", "back_btn"), callback_data="get_tariffs")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def back_button(callback_data):
    buttons = [
        [InlineKeyboardButton(text=await custom_button("🔙 Назад", "back_btn"), callback_data=callback_data)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def payment_kb(payment_link):
    buttons = [
        [InlineKeyboardButton(text="Оплатить", url=payment_link)],
        [InlineKeyboardButton(text=await custom_button("🔙 Назад в меню", "in_menu"), callback_data="in_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def in_menu():
    buttons = [
        [InlineKeyboardButton(text=await custom_button("🔙 Назад в меню", "in_menu"), callback_data="in_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def add_bid_matters(subject_matters):
    buttons = []
    async for subject_matter in subject_matters:
        buttons.append([
            InlineKeyboardButton(text=subject_matter.name, callback_data=f"add_bid_matter:{subject_matter.id}")
        ])
    buttons.append([
        InlineKeyboardButton(text=await custom_button("🔙 В меню", "in_menu_button"), callback_data="in_menu"),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def useful_materials_kb(materials):
    builder = InlineKeyboardBuilder()
    async for material in materials:
        if material.url:
            builder.button(text=material.title, url=material.url)
        else:
            builder.button(text=material.title, callback_data=f"useful_materials:{material.id}")
    builder.button(text=await custom_button("🔙 Назад", "back_btn"), callback_data="personal_account")
    builder.adjust(1)
    return builder.as_markup()


async def profile_kb():
    buttons = [
        [
            InlineKeyboardButton(text=await custom_button("Мои категории", "my_categories_btn"), callback_data="my_categories"),
            # InlineKeyboardButton(text=await custom_button("Пополнить баланс", "top_up_balance_kb"), callback_data="top_up_balance"),
        ],[
            InlineKeyboardButton(text=await custom_button("🔙 Назад", "back_btn"),  callback_data="personal_account"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def my_categories_kb(categories, black_list, search_switch):
    buttons = []
    for category in categories:
        buttons.append([
            InlineKeyboardButton(text=category.name + (" 🔴" if category.id in black_list or not search_switch else " 🟢"),
                                 callback_data=f"switch_my_category:{category.id}")
        ])
    buttons.append([
        InlineKeyboardButton(text=await custom_button("🔙 Назад", "back_btn"),  callback_data="profile"),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def change_payment_varios():
    buttons = [
        [
            InlineKeyboardButton(text=await custom_button("Оплатить с баланса", "balance_varios"), callback_data="change_payment_varios:balance"),
            InlineKeyboardButton(text=await custom_button("Оплатить картой", "card_varios"), callback_data="change_payment_varios:card"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

