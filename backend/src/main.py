import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTabWidget,
    QSizePolicy,
    QDesktopWidget,
    QTextEdit,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer
from utils.html_parser import get_new_html
from uagents import Agent, Bureau, Context, Model
import asyncio
import threading
from agents.main import create_agents
from agents.schemas.message import Message

global main_agent_ctx
main_agent_ctx = None

global agents_list
agents_list = []

global current_msg_id
current_msg_id = "random_msg_id_generated_each_time"

main_agent = Agent(name="main_agent", seed="sigmar recovery phrase")


class BrowserTab(QWidget):
    def __init__(self, parent=None, url="https://nextgenfile.com"):
        super().__init__()
        self.parent_widget = parent
        self.layout = QVBoxLayout()
        self.url_bar = QLineEdit()
        self.web_view = QWebEngineView()

        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.layout.addWidget(self.url_bar)

        self.web_view.setUrl(QUrl(url))
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.web_view.titleChanged.connect(self.update_title)

        self.web_view.loadFinished.connect(self.run_onload_script)

        self.layout.addWidget(self.web_view)

        self.setLayout(self.layout)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.web_view.setUrl(QUrl(url))

    def update_url_bar(self, q):
        self.url_bar.setText(q.toString())

    def update_title(self, title):
        if self.parent_widget:
            index = self.parent_widget.indexOf(self)
            self.parent_widget.setTabText(index, title if title else "New Tab")

    def run_onload_script(self):
        js = """
            (function() {
                return document.documentElement.outerHTML;
            })();
        """
        self.web_view.page().runJavaScript(js, self.retrieve_results)

    def capture_screenshot(self):
        screenshot = self.web_view.grab()
        screenshot.save("screenshot.png", "png")

    def retrieve_results(self, result):
        parsed_code, elements = get_new_html(result)
        print(parsed_code)
        QTimer.singleShot(1000, self.capture_screenshot)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrowseBlind")
        screen_height = QDesktopWidget().screenGeometry().height()
        self.setGeometry(0, 0, screen_height, screen_height)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        browser_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        browser_layout.addWidget(self.tabs)

        browser_container = QWidget()
        browser_container.setLayout(browser_layout)

        browser_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(browser_container, stretch=7)

        right_box = QWidget()
        right_box_layout = QVBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.on_input_field_return_pressed)
        right_box_layout.addWidget(self.input_field)

        self.output_area = QTextEdit()
        right_box_layout.addWidget(self.output_area)

        right_box.setLayout(right_box_layout)
        right_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(right_box, stretch=3)

        self.add_new_tab()

    def add_new_tab(self):
        new_tab = BrowserTab(parent=self.tabs)
        self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentWidget(new_tab)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    async def send_input_to_python(self):
        input_text = self.input_field.text()
        await main_agent_ctx.send(
            agents_list[1]["address"],
            Message(agents=agents_list, info={"question": input_text}),
        )
        self.output_area.append("Input received: " + input_text)
        self.input_field.clear()

    def on_input_field_return_pressed(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.send_input_to_python())
        finally:
            loop.close()

    def reload_current_tab(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.reload()


app = QApplication(sys.argv)
browser = Browser()
browser.show()
browser.showMaximized()


@main_agent.on_event("startup")
async def send_message(ctx: Context):
    global main_agent_ctx
    main_agent_ctx = ctx


agents = create_agents(browser)
bureau = Bureau()
bureau.add(main_agent)

agents_list.append({"name": "main_agent", "address": main_agent.address})

for _ in agents:
    print(_)
    bureau.add(_)
    agents_list.append({"name": _.name, "address": _.address})

threading.Thread(target=bureau.run).start()

sys.exit(app.exec_())
