from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QTimer


def init_go_forward_agent(browser):
    go_forward = Agent(name="go_forward", seed="go_forward")

    @go_forward.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        QTimer.singleShot(0, browser.go_forward)

    return go_forward
