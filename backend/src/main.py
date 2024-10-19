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
import json


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
        self.input_field.returnPressed.connect(self.send_input_to_python)
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

    def send_input_to_python(self):
        input_text = self.input_field.text()
        print("Input received:", input_text)
        self.output_area.append("Input received: " + input_text)
        self.input_field.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    browser.showMaximized()
    sys.exit(app.exec_())
