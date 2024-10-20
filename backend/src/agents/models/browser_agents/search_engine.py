from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QObject, pyqtSignal


class SearchEngineSignals(QObject):
    search_requested = pyqtSignal(str)


def init_search_engine_agent(browser):
    search_engine = Agent(name="search_engine", seed="search_engine")
    search_engine.signals = SearchEngineSignals()
    search_engine.signals.search_requested.connect(browser.search_engine)

    @search_engine.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        search_engine.signals.search_requested.emit(msg.info["query"])

    return search_engine
