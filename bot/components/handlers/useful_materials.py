from aiogram import types
from bot.components.connectors import postgres_connector
from bot.components.keyboards import keyboard as kb
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.types import FSInputFile
from bot.components.utils import custom_text

async def all_materials(callback: types.CallbackQuery):
    materials = await postgres_connector.get_useful_materials()
    keyboard = await kb.useful_materials_kb(materials)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


async def get_material(callback: types.CallbackQuery):
    _, material_id = callback.data.split(":")
    material = await postgres_connector.get_useful_material_by_id(int(material_id))
    keyboard = await kb.back_button("useful")
    if material.image:
        await callback.message.answer_photo(
            FSInputFile(f"bot/media/{material.image}"),
            caption=material.text if material.text else material.title,
            reply_markup=keyboard,
        )
        await callback.message.delete()
    elif material.video:
        print(material.video)
        await callback.message.answer_video(
            FSInputFile(f"bot/media/{material.video}"),
            caption=material.text if material.text else material.title,
            reply_markup=keyboard
        )
        await callback.message.delete()
    else:
        try:
            await callback.message.edit_text(
                material.text, reply_markup=keyboard)
        except:
            try:
                await callback.message.edit_caption(
                    caption=material.text, reply_markup=keyboard
                )
            except:
                await callback.message.answer(material.text, reply_markup=keyboard)
                await callback.message.delete()


def register_handlers(dp: Dispatcher):
    dp.callback_query.register(all_materials, F.data == "useful")
    dp.callback_query.register(get_material, F.data.startswith("useful_materials"))

