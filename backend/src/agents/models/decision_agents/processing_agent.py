from utils.llm_parsing import extract_and_parse_json
from agents.schemas.message import Message
from uagents import Agent, Context
from llms.groq import run_groq
import re


def init_processing_agent(browser):
    processing_agent = Agent(name="processing_agent", seed="processing_agent")

    def find_first_occurrence(s):
        match = re.search(r"[12345]", s)
        if match:
            return int(match.group())
        return 0

    @processing_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        summary = browser.tabs.currentWidget().summary
        promptB = (
            f"""
        You are an AI agent. Your goal is to take a user’s command and choose the next step from the list below. 
        Summary of the page the user is on: {summary}
        User’s command: {msg.info["question"]}
        Which of the following tasks does the user want to do? Respond with [<number>] for which task
        [1] Ask a question regarding information that is on the page
        [2] Using search engine to search anything, go to a url or company website, opening/closing a tab, going back/forward, reload page, print/save the page
        [3] Proceed with in-page functionality (click an anything on the page OR enter information on the page - input field, upload file, etc). Also, respond with """
            + """ {"action": "click" or "input", "data": "None" or "<data here>"}. If user wants to click on button or something, then choose click. If user is searching for a box on the page or trying to enter information, then choose input. For the data key, this is the information the user is trying to fill into the field (usernames and passwords MUST fall under this). Say "None" if user didn't mention anything. ONLY RETURN JSON SCHEMA and task number [3]. """
            + """
        [4] Summarize the page
        [5] Read the whole page in its entirety
        """
        )
        agents_list = msg.agents
        response = run_groq(promptB)
        task_number = find_first_occurrence(response)
        update_obj = {}
        if task_number != 0:
            agent_to_use = ""
            if task_number == 1:
                agent_to_use = "question_agent"
            elif task_number == 3:
                update_obj = extract_and_parse_json(response)
                if update_obj is None:
                    if "click" in msg.info["question"].lower():
                        update_obj = {"action": "click", "data": None}
                    else:
                        update_obj = {"action": "input", "data": None}
                agent_to_use = "inner_agent"
            elif task_number == 2:
                agent_to_use = "browser_agent"
            elif task_number == 4:
                agent_to_use = "onload_agent"
            elif task_number == 5:
                agent_to_use = "read_page_agent"
            found_agent = False
            for agent in agents_list:
                if found_agent:
                    break
                if agent["name"] == agent_to_use:
                    found_agent = True
                    msg.info = {**msg.info, **update_obj}
                    text = "Transferred to <b> " + agent_to_use + " </b> agent"
                    browser.output_area.append(
                        f"""
                        <center><div style="color: #b83e95; font-weight: 800; padding: 3px; font-size: 15px;margin-top: 4px; text-align: center;"><i> {text} </i> </div></center>
                        """
                    )
                    await ctx.send(agent["address"], msg)

    return processing_agent
