from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QTimer


def init_print_page_agent(browser):
    print_page = Agent(name="print_page", seed="print_page")

    @print_page.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        QTimer.singleShot(0, browser.print_page)

    return print_page
