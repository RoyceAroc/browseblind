from agents.models.browser_agents.reload_page import init_reload_page_agent
from agents.models.browser_agents.search_engine import init_search_engine_agent
from agents.models.browser_agents.url_engine import init_url_engine_agent
from agents.models.browser_agents.close_tab import init_close_tab_agent
from agents.models.browser_agents.go_back import init_go_back_agent
from agents.models.browser_agents.go_forward import init_go_forward_agent
from agents.models.browser_agents.print_page import init_print_page_agent


def create_browser_agents(browser):
    reload_page_agent = init_reload_page_agent(browser)
    search_engine_agent = init_search_engine_agent(browser)
    url_engine_agent = init_url_engine_agent(browser)
    close_tab_agent = init_close_tab_agent(browser)
    go_back_agent = init_go_back_agent(browser)
    go_forward_agent = init_go_forward_agent(browser)
    print_agent = init_print_page_agent(browser)

    agents = [
        reload_page_agent,
        search_engine_agent,
        url_engine_agent,
        close_tab_agent,
        go_back_agent,
        go_forward_agent,
        print_agent,
    ]
    return agents
