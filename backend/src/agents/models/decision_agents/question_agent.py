from agents.schemas.message import Message
from uagents import Agent, Context
from llms.gemini import run_gemini
from voice_model import play_sound
import PIL.Image


def init_question_agent(browser):
    question_agent = Agent(name="question_agent", seed="question_agent")

    @question_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        parsed_code = browser.tabs.currentWidget().html
        promptA = f"""
        Given the following screenshot of the web page plus the html. I want you to answer the user question.
        User question ${msg.info["question"]}
        Parsed HTML: {parsed_code}
        """
        image = PIL.Image.open("tab.png")
        response = run_gemini(image, promptA)
        browser.output_area.append(
            f"""
            <div style=" color: #3b8edb; font-weight: 800; padding: 3px; padding-left: 10px; font-size: 20px; margin-top: 5px;"> {response} </div>
            """
        )
        play_sound(response)

    return question_agent
