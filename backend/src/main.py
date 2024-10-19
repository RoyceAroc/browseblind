import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QSizePolicy,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class BrowserTab(QWidget):
    def __init__(self, parent=None, url="https://google.com"):
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


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrowseBlind")
        self.setGeometry(100, 100, 1024, 768)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        browser_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.clicked.connect(self.add_new_tab)
        self.new_tab_btn.setMaximumWidth(30)

        browser_layout.addWidget(self.new_tab_btn)
        browser_layout.addWidget(self.tabs)

        browser_container = QWidget()
        browser_container.setLayout(browser_layout)

        browser_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(browser_container, stretch=7)

        right_box = QWidget()
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
