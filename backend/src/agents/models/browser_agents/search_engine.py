from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class SearchEngineSignals(QObject):
    search_requested = pyqtSignal(str)


def init_search_engine_agent(browser):
    search_engine = Agent(name="search_engine", seed="search_engine")

    # Create signals object as a class attribute
    search_engine.signals = SearchEngineSignals()

    # Connect the signal to the browser's search_engine method
    search_engine.signals.search_requested.connect(browser.search_engine)

    @search_engine.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        # Emit the signal instead of directly calling the method
        search_engine.signals.search_requested.emit(msg.info["query"])

    return search_engine
