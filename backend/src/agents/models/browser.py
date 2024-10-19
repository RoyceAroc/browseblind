from agents.models.browser_agents.reload_page import init_reload_page_agent


def create_browser_agents(browser):
    reload_page_agent = init_reload_page_agent(browser)
    agents = reload_page_agent
    return agents
