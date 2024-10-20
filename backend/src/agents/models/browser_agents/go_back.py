from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QTimer


def init_go_back_agent(browser):
    go_back = Agent(name="go_back", seed="go_back")

    @go_back.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        QTimer.singleShot(0, browser.go_back)

    return go_back
