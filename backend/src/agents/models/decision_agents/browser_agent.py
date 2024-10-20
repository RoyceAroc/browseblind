from agents.schemas.message import Message
from uagents import Agent, Context
from llms.groq import run_groq
from utils.llm_parsing import extract_and_parse_json
import re


def find_first_occurrence(s):
    match = re.search(r"[1234567]", s)
    if match:
        return int(match.group())
    return 0


def init_browser_agent(browser):
    browser_agent = Agent(name="browser_agent", seed="browser_agent")

    @browser_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        promptD = (
            f"""
        You are an AI agent. Your goal is to take a user’s command and choose the next step from the list below. 
        User’s command: {msg.info["question"]}"""
            + """
        Respond with [<number>] for where number is which task from below and the json schema if you choose [1] or [2] 
        [1] Use a search engine to search anything keybased where the user has intent on searching something and none of the options below. Also respond with {"query": query} which is json where query is what the user wants to search on the search engine. You MUST responsd with a json with before. 
        [2] Visit a specific url (if the user query implies a url then convert to appropriate url - for example a company name then visit company name website). Also respond with {“url”: url} which starts with “https://”. You MUST respond with a json with before.
        [3] Close the current tab 
        [4] Go back on the current page to previous page
        [5] Go forward on the current pag
        [6] Reload the current tab
        [7] Print the page (aka save it as a pdf)
        """
        )
        agents_list = msg.agents
        response = run_groq(promptD)
        task_number = find_first_occurrence(response)
        update_obj = {}
        if task_number != 0:
            agent_to_use = ""
            if task_number == 1:
                agent_to_use = "search_engine"
                update_obj = extract_and_parse_json(response)
                if update_obj is None:
                    update_obj = {"query": msg.info["question"]}
            elif task_number == 2:
                agent_to_use = "url_engine"
                update_obj = extract_and_parse_json(response)
                if update_obj is None:
                    update_obj = {"url": "https://google.com"}
            elif task_number == 3:
                agent_to_use = "close_tab"
            elif task_number == 4:
                agent_to_use = "go_back"
            elif task_number == 5:
                agent_to_use = "go_forward"
            elif task_number == 6:
                agent_to_use = "reload_page"
            elif task_number == 7:
                agent_to_use = "print_page"
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

    return browser_agent
