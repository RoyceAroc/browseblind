from agents.schemas.message import Message
from uagents import Agent, Context
from utils.html_parser import get_new_html
from llms.gemini import run_gemini
import PIL.Image


def init_read_page_agent(browser):
    read_page_agent = Agent(name="read_page_agent", seed="read_page_agent")

    @read_page_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        parsed_code = browser.tabs.currentWidget().html
        promptA = f"""
        Given the following screenshot of the web page plus the html. I want you to read the contents on the website in a readable format to a human going through the different parts of the page and using proper grammar.
        Parsed HTML: {parsed_code}
        """
        image = PIL.Image.open("tab.png")
        response = run_gemini(image, promptA)
        browser.output_area.append("Reading page: " + response)

    return read_page_agent
