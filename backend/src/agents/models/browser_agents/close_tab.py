from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QTimer


def init_close_tab_agent(browser):
    close_tab = Agent(name="close_tab", seed="close_tab")

    @close_tab.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        QTimer.singleShot(0, browser.close_tab)

    return close_tab
