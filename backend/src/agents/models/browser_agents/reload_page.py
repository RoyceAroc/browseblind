from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QUrl, QTimer


def init_reload_page_agent(browser):
    reload_page = Agent(name="reload_page", seed="reload_page")

    @reload_page.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        QTimer.singleShot(0, browser.reload_current_tab)

    return reload_page
