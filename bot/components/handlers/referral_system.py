from aiogram import types
from bot.components.connectors import postgres_connector
from bot.components.keyboards import keyboard as kb
from aiogram import Bot, Dispatcher
from aiogram import F
from bot.components.utils import custom_text


async def referral_system_menu(callback: types.CallbackQuery):
    user = await postgres_connector.get_user_by_id(callback.from_user.id)
    count_referrals = await postgres_connector.get_count_referrals(user)
    text = await custom_text("Реферальная ссылка: %s\n" + \
                             "Баланс: %s\n" + \
                             "Число активных рефералов: %s\n" + \
                             "За каждого активного реферала, твой баланс пополняется на 10% от оплаты его тарифа", "referral_system_menu",
                             formatting_attrs=(
                                 f"https://t.me/jobalertbot_bot?start={callback.from_user.id}",
                                 user.balance if user.balance else "0",
                                 str(count_referrals),
                             ))
    keyboard = await kb.back_button("personal_account")
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except:
        try:
            await callback.message.edit_caption(caption=text, reply_markup=keyboard, parse_mode="HTML")
        except:
            await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.message.delete()



def register_handlers(dp: Dispatcher):
    dp.callback_query.register(referral_system_menu, F.data == "referral_system")
