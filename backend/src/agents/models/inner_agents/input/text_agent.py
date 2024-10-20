from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QTimer


def init_text_agent(browser):
    text = Agent(name="text_agent", seed="text_agent")

    @text.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        QTimer.singleShot(0, browser.tabs.currentWidget().text_option)

    return text
