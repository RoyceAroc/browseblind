from agents.schemas.message import Message
from uagents import Agent, Context
from llms.gemini import run_gemini
import PIL.Image


def init_onload_agent(browser):
    onload_agent = Agent(name="onload_agent", seed="onload_agent")

    @onload_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        promptA = """
        Given the following screenshot of the web page please give a 1-2 sentence summary of what you see and what the page is about as if I’m a blind person and can’t see. If there is a navbar, then list its components and talk about it last.
        """
        image = PIL.Image.open("tab.png")
        response = run_gemini(image, promptA)
        browser.output_area.append("Summary of page: " + response)
        browser.tabs.currentWidget().summary = response

    return onload_agent
