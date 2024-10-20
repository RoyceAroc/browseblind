from agents.schemas.message import Message
from uagents import Agent, Context


def init_inner_agent(browser):
    inner_agent = Agent(name="inner_agent", seed="inner_agent")

    @inner_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        browser.tabs.currentWidget().in_page_extraction(msg)

    return inner_agent
