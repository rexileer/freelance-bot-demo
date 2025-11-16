from bot.components.connectors import postgres_connector
import html
import re

async def custom_text(default_text, key, formatting_attrs=None, html_escape=True):
    string = await postgres_connector.get_or_create_custom_text(key, default_text)
    string = re.sub("(%)([^s])", r"%%\2", string)
    if not formatting_attrs:
        return string
    else:
        if html_escape:
            formatting_attrs = tuple([html.escape(str(attr)) if attr else None for attr in formatting_attrs])
    try:
        return string % formatting_attrs
    except:
        return default_text % formatting_attrs


async def custom_button(default_text, key):
    return await postgres_connector.get_or_create_custom_button(key, default_text)
