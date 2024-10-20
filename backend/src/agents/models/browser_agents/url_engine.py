from agents.schemas.message import Message
from uagents import Agent, Context
from PyQt5.QtCore import QObject, pyqtSignal


class SearchEngineSignals(QObject):
    url_requested = pyqtSignal(str)


def init_url_engine_agent(browser):
    url_engine = Agent(name="url_engine", seed="url_engine")
    url_engine.signals = SearchEngineSignals()
    url_engine.signals.url_requested.connect(browser.url_engine)

    @url_engine.on_message(model=Message)
    async def handler(ctx: Context, sender: str, msg: Message):
        url_engine.signals.url_requested.emit(msg.info["url"])

    return url_engine
