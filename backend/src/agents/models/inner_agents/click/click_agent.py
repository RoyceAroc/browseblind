from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QTimer


def init_click_agent(browser):
    click = Agent(name="click_agent", seed="click_agent")

    @click.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        QTimer.singleShot(0, browser.tabs.currentWidget().click_option)

    return click
