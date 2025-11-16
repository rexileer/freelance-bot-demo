from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse
from aiogram import Bot
import os
from bot.components.connectors import postgres_connector
from bot.components.keyboards import keyboard as kb
from aiogram.types import FSInputFile

async def parse_response(request: str) -> dict:
    """
    :param request: Link.
    :return: Dictionary.
    """
    params = {}

    for item in urlparse(request).query.split('&'):
        key, value = item.split('=')
        params[key] = value
    return params

def calculate_signature(*args) -> str:
    """Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


async def check_signature_result(
    order_number: int,  # invoice number
    received_sum: decimal,  # cost of goods, RU
    received_signature: hex,  # SignatureValue
    password: str  # Merchant password
) -> bool:
    signature = calculate_signature(received_sum, order_number, password)
    print(signature.lower(), received_signature.lower())
    if signature.lower() == received_signature.lower():
        return True
    return False


@csrf_exempt
async def result_payment(request):
    merchant_password_2 = "HPTCb75kG26gPSy8VkBy"
    param_request = await parse_response(request.get_full_path())
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']
    check_result = await check_signature_result(number, cost, signature, merchant_password_2)
    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(bot_token)
    await bot.send_message(text=f"{check_result}, {number}", chat_id=1414395118)
    if check_result:
        check = await postgres_connector.get_check_by_id(number)
        if check.data.startswith("top_up_balance"):
            _, payment_amount = check.data.split(":")
            payment_amount = int(payment_amount)
            await postgres_connector.top_up_user_balance(check.user_id, payment_amount)
            user = await postgres_connector.get_user_by_id(check.user_id)
            keyboard = await kb.menu_button(await postgres_connector.get_user_subscription_existence(check.user_id),
                                            user.search_switch)
        else:
            _, tariff_id, selected_matters, payment_amount = check.data.split(":")
            tariff_id, selected_matters, payment_amount = int(tariff_id), eval(selected_matters), int(payment_amount)
            await postgres_connector.top_up_ref_balance(check.user_id, payment_amount)
            await postgres_connector.create_subscription(selected_matters, tariff_id, check.user_id)
            user = await postgres_connector.get_user_by_id(check.user_id)
            keyboard = await kb.menu_button(await postgres_connector.get_user_subscription_existence(check.user_id),
                                            user.search_switch)
        await bot.send_photo(photo=FSInputFile("bot/media/succ_payment.png"), chat_id=user.id, caption="Оплата прошла успешно", reply_markup=keyboard)
        await postgres_connector.dell_check(check)
        return HttpResponse("Оплата прошла успешно")
    else:
        return HttpResponse("Ошибка подписи", status=400)
