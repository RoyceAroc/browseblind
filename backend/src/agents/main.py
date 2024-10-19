from agents.models.browser import create_browser_agents
from agents.schemas.message import Message
from uagents import Agent, Context
from llms.groq import run_groq

import re


def find_first_occurrence(s):
    match = re.search(r"[1234]", s)
    if match:
        return int(match.group())
    return 0


def _find_first_occurrence(s):
    match = re.search(r"[12345678]", s)
    if match:
        return int(match.group())
    return 0


def create_agents(browser):
    browser_agents = create_browser_agents(browser)

    processing_agent = Agent(name="processing_agent", seed="processing_agent")
    browser_agent = Agent(name="browser_agent", seed="browser_agent")

    @browser_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        promptD = (
            f"""
        You are an AI agent. Your goal is to take a user’s command and choose the next step from the list below. 
        User’s command: {msg.info["question"]}"""
            + """
        Respond with [<number>] for where number is which task from below and the json schema if you choose [1] or [2] 
        [1] Use a search engine to search anything. Also respond with {"type": type, "query": query} which is json where type is one of [TEXT, IMAGE, VIDEOS] of what type of information the user is trying to search (choose one of the three). Query is what the user wants to search on the search engine.
        [2] Visit a specific url. Also respond with {“url”: url} which starts with “https://”
        [3] Close the current tab 
        [4] Go backward on current tab
        [5] Go forward on current tab
        [6] Reload the current tab
        [7] Print the page
        [8] Save the page
        """
        )
        agents_list = msg.agents
        response = run_groq(promptD)
        task_number = _find_first_occurrence(response)
        if task_number != 0:
            agent_to_use = ""
            if task_number == 6:
                agent_to_use = "reload_page"
            found_agent = False
            for agent in agents_list:
                if found_agent:
                    break
                if agent["name"] == agent_to_use:
                    found_agent = True
                    await ctx.send(agent["address"], msg)

    @processing_agent.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        promptB = f"""
        You are an AI agent. Your goal is to take a user’s command and choose the next step from the list below. 
        User’s command: {msg.info["question"]}
        Which of the following tasks does the user want to do? Respond with [<number>] for which task
        [1] Ask a question about the page
        [2] Proceed with in-page functionality (click an element on the page, enter information on the page - input field, upload file, etc)
        [3] Proceed with browser functionality (using search engine to search anything, going to a url, opening/closing a tab, going back/forward, reload page, print/save the page)
        [4] Summarize/read the page
        """
        agents_list = msg.agents
        response = run_groq(promptB)
        task_number = find_first_occurrence(response)
        if task_number != 0:
            agent_to_use = ""
            if task_number == 3:
                agent_to_use = "browser_agent"
            found_agent = False
            for agent in agents_list:
                if found_agent:
                    break
                if agent["name"] == agent_to_use:
                    found_agent = True
                    await ctx.send(agent["address"], msg)

    return [processing_agent, browser_agent] + browser_agents
