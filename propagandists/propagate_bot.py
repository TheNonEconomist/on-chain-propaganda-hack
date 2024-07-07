from __future__ import annotations

import asyncio
from os import getenv
from typing import TypedDict

from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, F, html, Router
from aiogram.filters import Command
from aiogram.fsm.scene import After, Scene, SceneRegistry, on
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from aiogram.methods import (
    SendSticker

)

from features import *
from mappings import *

TOKEN = getenv("TG_BOT_TOKEN")
BUTTON_CANCEL = KeyboardButton(text="❌ Cancel")
BUTTON_BACK = KeyboardButton(text="🔙 Back")


class FSMData(TypedDict, total=False):
    purpose: str
    community: str
    content: object


class CancellableScene(Scene):
    """
    This scene is used to handle cancel and back buttons,
    can be used as a base class for other scenes that needs to support cancel and back buttons.
    """

    @on.message(F.text.casefold() == BUTTON_CANCEL.text.casefold(), after=After.exit())
    async def handle_cancel(self, message: Message):
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())

    @on.message(F.text.casefold() == BUTTON_BACK.text.casefold(), after=After.back())
    async def handle_back(self, message: Message):
        await message.answer("Back.")




class RandomPropagandaScene(
    CancellableScene, state="random"
):
    @on.message.enter()  # Marker for handler that should be called when a user enters the scene.
    async def on_enter(self, message: Message):
        await message.answer(
            "",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [BUTTON_BACK, BUTTON_CANCEL],
                ],
                resize_keyboard=True,
            ),
        )

    @on.leave()
    async def random_propaganda(self, message: Message): #TODO: would be nice to add a functionality here where it adds on to a new sticker set...
        data: FSMData = await self.wizard.get_data()
        await self.show_results(message, language=message.text, **data)

    
class EducationScene(CancellableScene, state="education"):

    @on.message.enter()  # Marker for handler that should be called when a user enters the scene.
    async def on_enter(self, message: Message):
        await message.answer(
            "What are you concerned about atm?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Could this be Rug?"), 
                        KeyboardButton(text="We HATE the original team")
                    ],  
                    [BUTTON_BACK, BUTTON_CANCEL],
                ],
                resize_keyboard=True,
            ),
        )

    # TODO: need to add sticker functionality to this ...
    @on.message(F.text.casefold() == "Could this be Rug?!?", after=After.exit())
    async def rug_aware(self, message: Message):
        await message.reply("Hold On, Generating Dank Propaganda for Your Community...")

    @on.message(F.text.casefold() == "We HATE the original team", after=After.exit())
    async def CTO_aware(self, message: Message):
        await message.reply("There's always more to Learn!")
    
    @on.leave()
    async def random_propaganda(self, message: Message): #TODO: would be nice to add a functionality here where it adds on to a new sticker set...
        data: FSMData = await self.wizard.get_data()
        await self.show_results(message, language=message.text, **data)


class PriceTalkScene(CancellableScene, state="price_talk"):
    @on.message.enter()  # Marker for handler that should be called when a user enters the scene.
    async def on_enter(self, message: Message):
        prediction = grab_next_hour_price_prediction(token_address="0x1141b1e844CB93c0804D814a1AB718315ef3A4D2", chain="BASE")
        await message.reply(
            "Token price MIGHT CHANGE BY {}".format(prediction),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [BUTTON_BACK, BUTTON_CANCEL],
                ],
                resize_keyboard=True,
            ),
        )

class PurposeScene(
    CancellableScene, state="purpose"  # Handle callback queries even if user in any scene
):
    """
    Default scene for the bot.

    This scene is used to handle all messages that are not handled by other scenes.
    """

    @on.message.enter()  # Marker for handler that should be called when a user enters the scene.
    async def on_enter(self, message: Message):
        await message.answer(
            "Gm Gn ser. I mean I don't know where u are but I can help u. Wut do u need?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Just Generate Dank Propaganda"), 
                     KeyboardButton(text="Teach Me Something"), 
                     KeyboardButton(text="Price Talk Only")],
                    [BUTTON_BACK, BUTTON_CANCEL], 
                ], 
                resize_keyboard=True),
        )


    @on.message(F.text.casefold() == "Just Generate Dank Propaganda", after=After.goto(RandomPropagandaScene))
    async def dank_propaganda(self, message: Message):
        await message.reply("Hold On, Generating Dank Propaganda for Your Community...")

    @on.message(F.text.casefold() == "Teach Me Something", after=After.goto(EducationScene))
    async def education_mode(self, message: Message):
        await message.reply("There's always more to Learn!")

    @on.message(F.text.casefold() == "Price Talk Only", after=After.goto(PriceTalkScene))
    async def price_talk(self, message: Message):
        pass

class DefaultScene(
    Scene,
    reset_data_on_enter=True,  # Reset state data
    reset_history_on_enter=True,  # Reset history
    callback_query_without_state=True,  #
):
    start_demo = on.message(F.text.casefold() == "demo", after=After.goto(PurposeScene))

    @on.message(Command("demo"))
    async def demo(self, message: Message):
        await message.answer(
            "Demo started",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Go to form", callback_data="start")]]
            ),
        )

    @on.callback_query(F.data == "start", after=After.goto(PurposeScene))
    async def demo_callback(self, callback_query: CallbackQuery):
        await callback_query.answer(cache_time=0)
        await callback_query.message.delete_reply_markup()

    @on.message.enter()  # Mark that this handler should be called when a user enters the scene.
    @on.message()
    async def default_handler(self, message: Message):
        await message.answer(
            "Start demo?\nYou can also start demo via command /demo",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Demo")]],
                resize_keyboard=True,
            ),
        )
# async def main():
    
#     # Initialize Bot instance with default bot properties which will be passed to all API calls
#     bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

#     dp = Dispatcher()

#     dp.include_router(form_router)

#     # Start event dispatching
#     await dp.start_polling(bot)


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()

    # Scene registry should be the only one instance in your application for proper work.
    # It stores all available scenes.
    # You can use any router for scenes, not only `Dispatcher`.
    registry = SceneRegistry(dispatcher)
    print("registry....")
    # All scenes at register time converts to Routers and includes into specified router.
    registry.add(
        DefaultScene,
        PurposeScene,
        RandomPropagandaScene,
        EducationScene,
        PriceTalkScene
    )
    print("------")

    return dispatcher


def main() -> None:
    dp = create_dispatcher()
    print("----- dispatcher -----")
    bot = Bot(token=TOKEN)
    print("----- TOKEN -----")
    dp.run_polling(bot)
    print("----- BOT -----")


if __name__ == "__main__":
    # Recommended to use CLI instead of this snippet.
    # `aiogram run polling scene_example:create_dispatcher --token BOT_TOKEN --log-level info`
    asyncio.run(main())