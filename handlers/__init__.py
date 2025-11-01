# handlers/__init__.py

from .start_handler import register_start_handlers
from .analytics_handler import register_analytics_handlers
from .materials_handler import register_materials_handlers
from .signup_handler import register_signup_handlers
from .broadcast_handler import register_broadcast_handlers
from .chat_handler import register_chat_handlers

def register_handlers(bot, data):
    register_start_handlers(bot, data)
    register_analytics_handlers(bot, data)
    register_materials_handlers(bot, data)
    register_signup_handlers(bot, data)
    register_broadcast_handlers(bot, data)
    register_chat_handlers(bot, data)
