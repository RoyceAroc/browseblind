from agents.models.browser_agents.reload_page import init_reload_page_agent
from agents.models.browser_agents.search_engine import init_search_engine_agent


def create_browser_agents(browser):
    reload_page_agent = init_reload_page_agent(browser)
    search_engine_agent = init_search_engine_agent(browser)
    agents = [reload_page_agent, search_engine_agent]
    return agents
