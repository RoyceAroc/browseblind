import sys
import os
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
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from uagents import Agent, Bureau, Context
from datetime import datetime as dt
from agents.main import create_agents
from agents.schemas.message import Message
import threading
import asyncio
import json
from llms.groq import run_groq
from llms.gemini import run_gemini
from utils.html_parser import get_new_html
import PIL.Image
import PIL.ImageDraw
import re
import string
import random

global main_agent_ctx
main_agent_ctx = None

global agents_list
agents_list = []

global current_msg_id
current_msg_id = ""

main_agent = Agent(name="main_agent", seed="sigmar recovery phrase")


def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for _ in range(length))


class ConsoleLoggingPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        level_str = {0: "INFO", 1: "WARNING", 2: "ERROR"}.get(level, "UNKNOWN")
        print(f"JS [{level_str}] {message} (line {line}) in {source}")


class BrowserTab(QWidget):
    screenshot_completed = pyqtSignal()

    def __init__(self, parent=None, url="https://browseblind.co"):
        super().__init__()
        self.parent_widget = parent
        self.layout = QVBoxLayout()
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet(
            """
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #506159;
                border-radius: 5px;
                background-color: #ffffff;
                font-size: 14px;
                color: #333333;
                margin: 5px;
            }
            QLineEdit:focus {
                border-color: #dbb6a2;
                background-color: #fafafa;
            }
            QLineEdit:hover {
                border-color: #dbb6a2;
            }
        """
        )

        self.web_view = QWebEngineView()

        self.html = None
        self.fields = None
        self.summary = None

        self.page = ConsoleLoggingPage(self.web_view)
        self.web_view.setPage(self.page)

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

    def capture_screenshot(self):
        screenshot = self.web_view.grab()
        screenshot.save("tab.png", "png")
        self.screenshot_completed.emit()

    def run_onload_script(self):
        QTimer.singleShot(100, lambda: self.execute_onload_script(True))

    def v2_onload_script(self):
        self.execute_onload_script()

    def execute_onload_script(self, init=False):
        js = """
        (function() {
                let elements = document.querySelectorAll('*');
                let results = [];

                elements.forEach(function(element) {
                    let elementInfo = {
                        tag: element.tagName,
                        events: [],
                        xpath: getXPath(element)
                    };

                    let eventAttributes = Array.from(element.attributes).filter(attr => 
                        attr.name.startsWith('on')
                    );

                    eventAttributes.forEach(attr => {
                        elementInfo.events.push({
                            type: attr.name.slice(2),
                            source: 'inline'
                        });
                    });

                    if (elementInfo.events.length > 0) {
                        results.push(elementInfo);
                    }

                });

                let final = {
                    "results": results,
                    "innerHTML": document.documentElement.outerHTML
                }
                return JSON.stringify(final, null, 2);
            })();

            function getXPath(element) {
                let parts = [];
                let currentElement = element;

                while (currentElement && currentElement.nodeType === Node.ELEMENT_NODE) {
                    let siblings = Array.from(currentElement.parentNode ? currentElement.parentNode.children : []);
                    let sameTagSiblings = siblings.filter(sibling => sibling.nodeName === currentElement.nodeName);

                    if (sameTagSiblings.length > 1) {
                        let index = sameTagSiblings.indexOf(currentElement) + 1;
                        parts.push(currentElement.nodeName.toLowerCase() + `[${index}]`);
                    } else {
                        parts.push(currentElement.nodeName.toLowerCase());
                    }

                    currentElement = currentElement.parentNode;
                }

                parts.reverse();
                return '/' + parts.join('/');
            }
        """
        self.web_view.page().runJavaScript(
            js, lambda result: self.retrieve_results_callback(result, init)
        )

    def retrieve_results_callback(self, result, init=False):
        output = json.loads(result)
        content = output["innerHTML"]

        response = get_new_html(content, output["results"])
        self.html = response[0]
        self.fields = response[1]

        if init:
            self.screenshot_completed.connect(self.send_message_after_screenshot)
        QTimer.singleShot(10, self.capture_screenshot)

    def in_page_extraction(self, msg):
        action = msg.info["action"]
        question = msg.info["question"]

        action_chosen = "clickable element"
        if "input" in action.lower():
            action_chosen = "input element"

        async def call_agent(xpath):
            if action_chosen == "clickable element":
                found = False
                for agent in agents_list:
                    if found:
                        break
                    if agent["name"] == "click_agent":
                        self.xpath = xpath
                        found = True
                        await main_agent_ctx.send(agent["address"], msg)
            else:
                found = False
                for agent in agents_list:
                    if found:
                        break
                    if agent["name"] == "text_agent":
                        self.xpath = xpath
                        if "data" in msg.info:
                            self.data = msg.info["data"]
                        else:
                            self.data = None
                        found = True
                        await main_agent_ctx.send(agent["address"], msg)

        async def backup():
            prompt = f"""
            Given the following html code, select which {action_chosen} (you need to output the element's ID) matches
            the user's task.
            User's task {user_prompt}
            Website parsed code below:
            {self.html}
            """
            response = run_groq(prompt)
            print(prompt)
            print(response)
            if action_chosen == "clickable element":
                pattern = r"click-(\d+)"
            else:
                pattern = r"input-(\d+)"
            match = re.search(pattern, response.replace(" ", ""))
            if match:
                num = int(match.group(1))
                await call_agent(self.fields[num - 1]["xpath"])
            else:
                browser.output_area.append("\n" + "Couldn't complete operation" "\n")

        user_prompt = question
        prompt = f"""
        Return a bounding box where users asks "{user_prompt}". If not found, return None.
        \n [ymin, xmin, ymax, xmax].
        """
        image = PIL.Image.open("tab.png")
        response = run_gemini(image, prompt)

        js_get_viewport = """
        (function() {
            return JSON.stringify({
                width: window.innerWidth,
                height: window.innerHeight
            });
        })();
        """

        async def handle_viewport_result(viewport_result):
            async def process_paths(result):
                output = json.loads(result)
                new_output = []

                for outer in output["paths"]:
                    found = False
                    for field in self.fields:
                        if found:
                            break
                        if field["xpath"] == outer:
                            found = True
                            new_output.append(outer)

                final_output = []
                for a, path in enumerate(new_output):
                    skip = False
                    for b, check in enumerate(new_output):
                        if skip:
                            break
                        if path in check and a != b:
                            skip = True
                    if not skip:
                        final_output.append(path)

                if len(final_output) == 1:
                    await call_agent(final_output[0])
                else:
                    await backup()

            viewport = json.loads(viewport_result)
            viewport_width = viewport["width"]
            viewport_height = viewport["height"]

            s = response
            match = re.search(r"\[(.*?)\]", s)
            try:
                if match:
                    bounding_box = [float(x) for x in match.group(1).split(",")]
                    ymin, xmin, ymax, xmax = bounding_box

                    viewport_ymin = (ymin * viewport_height) / 1000
                    viewport_xmin = (xmin * viewport_width) / 1000
                    viewport_ymax = (ymax * viewport_height) / 1000
                    viewport_xmax = (xmax * viewport_width) / 1000

                    js2 = f"""
                    (function() {{
                        let paths = {{"paths": []}};
                        const boundaryBoxBrowseBlind = {{
                            top: {viewport_ymin},
                            left: {viewport_xmin},
                            bottom: {viewport_ymax},
                            right: {viewport_xmax}
                        }};

                        const elementsBrowseBlind = document.querySelectorAll('*');
                        elementsBrowseBlind.forEach((element) => {{
                            const rect = element.getBoundingClientRect();
                            if (
                                rect.top < boundaryBoxBrowseBlind.bottom &&
                                rect.bottom > boundaryBoxBrowseBlind.top &&
                                rect.left < boundaryBoxBrowseBlind.right &&
                                rect.right > boundaryBoxBrowseBlind.left
                            ) {{
                                paths.paths.push(getXPath(element));
                            }}
                        }});
                        return JSON.stringify(paths, null, 2);
                    }})();
                    """
                    # Using lambda to bridge between sync and async code
                    future = asyncio.Future()

                    def js_callback(result):
                        asyncio.run(process_paths(result))

                    self.web_view.page().runJavaScript(js2, js_callback)
                else:
                    await backup()
            except Exception:
                await backup()

        if action_chosen == "clickable element":

            def viewport_callback(result):
                asyncio.run(handle_viewport_result(result))

            self.web_view.page().runJavaScript(js_get_viewport, viewport_callback)
        else:
            asyncio.create_task(backup())

    def send_message_after_screenshot(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.send_agent_message())
        finally:
            loop.close()
        self.screenshot_completed.disconnect(self.send_message_after_screenshot)

    async def send_agent_message(self):
        global current_msg_id
        current_msg_id = generate_random_string(10)
        await main_agent_ctx.send(
            agents_list[2]["address"],
            Message(
                agents=agents_list,
                info={"msg_id": generate_random_string(10)},
            ),
        )

    def click_option(self):
        def cb(result):
            self.v2_onload_script()

        browser.output_area.append("\n" + "Clicked element of interest" "\n")

        click_js = (
            """
            (function() {
                let elements = document.querySelectorAll('*');
                let results = [];

                elements.forEach(function(element) {
                    if (getXPath(element) == """
            + f"""  '{self.xpath}' """
            + """) {
                        element.dispatchEvent(new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }));
                        element.click();
                        console.log("CLICKED")
                    }
                });
            })();

            function getXPath(element) {
                let parts = [];
                let currentElement = element;

                while (currentElement && currentElement.nodeType === Node.ELEMENT_NODE) {
                    let siblings = Array.from(currentElement.parentNode ? currentElement.parentNode.children : []);
                    let sameTagSiblings = siblings.filter(sibling => sibling.nodeName === currentElement.nodeName);

                    if (sameTagSiblings.length > 1) {
                        let index = sameTagSiblings.indexOf(currentElement) + 1;
                        parts.push(currentElement.nodeName.toLowerCase() + `[${index}]`);
                    } else {
                        parts.push(currentElement.nodeName.toLowerCase());
                    }

                    currentElement = currentElement.parentNode;
                }

                parts.reverse();
                return '/' + parts.join('/');
            }
        """
        )
        self.web_view.page().runJavaScript(click_js, cb)

    def text_option(self):
        def cb(result):
            self.v2_onload_script()

        browser.output_area.append("\n" + "Inputted into element of interest" "\n")

        text_js = """
        (function() {
            let elements = document.querySelectorAll('*');
            let results = [];

            elements.forEach(function(element) {
                if (getXPath(element) === '%s') {
                    element.dispatchEvent(new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    }));
                    element.click();
                    element.value = '%s';
                    console.log("INPUTTED")
                }
            });
        })();

        function getXPath(element) {
            let parts = [];
            let currentElement = element;

            while (currentElement && currentElement.nodeType === Node.ELEMENT_NODE) {
                let siblings = Array.from(currentElement.parentNode ? currentElement.parentNode.children : []);
                let sameTagSiblings = siblings.filter(sibling => sibling.nodeName === currentElement.nodeName);

                if (sameTagSiblings.length > 1) {
                    let index = sameTagSiblings.indexOf(currentElement) + 1;
                    parts.push(currentElement.nodeName.toLowerCase() + `[${index}]`);
                } else {
                    parts.push(currentElement.nodeName.toLowerCase());
                }

                currentElement = currentElement.parentNode;
            }

            parts.reverse();
            return '/' + parts.join('/');
        }
        """ % (
            self.xpath,
            "" if self.data is None else self.data,
        )

        self.web_view.page().runJavaScript(text_js, cb)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrowseBlind")
        screen_height = QDesktopWidget().screenGeometry().height()
        self.setGeometry(0, 0, screen_height, screen_height)

        self.downloads_dir = os.path.join(
            os.path.expanduser("~"), "Downloads", "browseblind"
        )
        os.makedirs(self.downloads_dir, exist_ok=True)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: white; border-radius: 10px;")
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        browser_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane {
                background-color: #506159;
                border-radius: 10px;
                color: #506159;
                font-weight: 500;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #506159;
                color: #ddd;
                padding: 10px;
                border-radius: 10px;
            }
            QTabBar::tab:selected {
                background-color: #dbb6a2;
                color: #fff;
            }
            QTabBar::tab:hover {
                background-color: #dbb6a2;
                color: #fff;
            }
        """
        )
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        browser_layout.addWidget(self.tabs)

        browser_container = QWidget()
        browser_container.setLayout(browser_layout)

        browser_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(browser_container, stretch=7)

        right_box = QWidget()
        right_box_layout = QVBoxLayout()

        self.output_area = QTextEdit()
        self.output_area.setStyleSheet(
            "padding: 10px; background-color: #E1D2CA; border-radius: 10px;"
        )
        right_box_layout.addWidget(self.output_area)

        self.input_field = QLineEdit()
        self.input_field.setMinimumHeight(100)
        font = QFont()
        font.setPointSize(16)
        self.input_field.setFont(font)
        self.input_field.setAlignment(Qt.AlignTop)
        self.input_field.setStyleSheet(
            "padding: 10px;background-color: #506159; border-radius: 10px;"
        )

        self.input_field.returnPressed.connect(self.on_input_field_return_pressed)
        right_box_layout.addWidget(self.input_field)

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

    def search_engine(self, query):
        self.add_new_tab(),
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.setUrl(
                QUrl("https://www.google.com/search?q=" + query)
            )

    def url_engine(self, url):
        self.add_new_tab(),
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.setUrl(QUrl(url))

    def close_tab(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            index = self.tabs.indexOf(current_tab)
            self.tabs.removeTab(index)
            current_tab.deleteLater()
            if self.tabs.count() == 0:
                self.add_new_tab()

    def go_forward(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.forward()

    def go_back(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.back()

    def print_page(self):
        current_tab = self.tabs.currentWidget()
        if not current_tab:
            return

        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        page_title = self.tabs.tabText(self.tabs.currentIndex())
        safe_title = "".join(
            c for c in page_title if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        if not safe_title:
            safe_title = "webpage"

        pdf_filename = f"{safe_title}_{timestamp}.pdf"
        pdf_path = os.path.join(self.downloads_dir, pdf_filename)

        def callback(data):
            if data:
                with open(pdf_path, "wb") as file:
                    file.write(data)
                self.output_area.append(f"PDF saved to: {pdf_path}")
            else:
                self.output_area.append("Failed to save PDF")

        current_tab.web_view.page().printToPdf(callback)


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
    bureau.add(_)
    agents_list.append({"name": _.name, "address": _.address})

threading.Thread(target=bureau.run).start()

sys.exit(app.exec_())
