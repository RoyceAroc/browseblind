from agents.models.browser import create_browser_agents
from agents.models.decision_agents.processing_agent import init_processing_agent
from agents.models.decision_agents.onload_agent import init_onload_agent
from agents.models.decision_agents.browser_agent import init_browser_agent
from agents.models.decision_agents.read_page_agent import init_read_page_agent
from agents.models.decision_agents.question_agent import init_question_agent
from agents.models.decision_agents.inner_agent import init_inner_agent
from agents.models.inner_agents.click.click_agent import init_click_agent
from agents.models.inner_agents.input.text_agent import init_text_agent


def create_agents(browser):
    browser_agents = create_browser_agents(browser)
    click_agent = init_click_agent(browser)
    text_agent = init_text_agent(browser)

    processing_agent = init_processing_agent(browser)
    onload_agent = init_onload_agent(browser)
    browser_agent = init_browser_agent(browser)
    read_page_agent = init_read_page_agent(browser)
    question_agent = init_question_agent(browser)
    inner_agent = init_inner_agent(browser)

    decision_agents = [
        processing_agent,
        onload_agent,
        browser_agent,
        read_page_agent,
        question_agent,
        inner_agent,
    ]

    return decision_agents + browser_agents + [click_agent, text_agent]
