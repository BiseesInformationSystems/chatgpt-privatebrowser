import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QStatusBar,
                              QTabWidget, QWidget, QInputDialog, QFileDialog, QMenu, QDialog,
                              QTextEdit, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox)
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEnginePage, QWebEngineProfile,
                                       QWebEngineDownloadItem)
from PyQt5.QtWebEngineCore import QWebEngineHttpRequest, QWebEngineUrlRequestInterceptor
from adblocker import AdBlocker
#from adblockparser import AdblockRules
import re
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWebEngineCore import QWebEngineCookieStore
import logging
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInfo





logging.basicConfig(filename='browser.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

raw_rules = []



adblocker = AdBlocker(os.path.join(os.path.dirname(os.path.realpath(__file__)), "filters"))

class AdBlockRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, adblocker):
        super().__init__()
        self.adblocker = adblocker

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        url = info.requestUrl().toString()
        if self.adblocker.should_block(url):
            info.block(True)
        else:
            if info.resourceType() == QWebEngineUrlRequestInfo.ResourceTypeStylesheet:
                css_file_path = self.adblocker.create_css_injection()
                info.redirect(QUrl.fromLocalFile(css_file_path))

def disable_cookies(profile):
    settings = profile.settings()
    settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
    settings.setAttribute(QWebEngineSettings.CookiesEnabled, False)
    
    


class CustomWebEngineProfile(QWebEngineProfile):
    def __init__(self, adblocker, parent=None):
        super().__init__(parent)
        self.adblocker = adblocker
        self.setHttpUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')

        adblock_interceptor = AdBlockRequestInterceptor(self.adblocker)
        self.setUrlRequestInterceptor(adblock_interceptor)
        
class BrowserTab(QWebEngineView):
    #favicon_changed = pyqtSignal(QIcon)
    def __init__(self, private_browser_instance, adblocker, custom_profile, parent=None):
        super().__init__(parent)
        self.private_browser_instance = private_browser_instance
        self.adblocker = adblocker

        self.web_page = QWebEnginePage(custom_profile, self)
        self.setPage(self.web_page)

        

        self.page().loadFinished.connect(self.on_load_finished)
        self.iconChanged.connect(self.on_icon_changed)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.create_context_menu)

        self.custom_profile = custom_profile

        
        
    def on_icon_changed(self, icon):
        self.setWindowIcon(icon)
    

    def create_context_menu(self, pos):
        menu = self.page().createStandardContextMenu()

        save_page_action = QAction("Save Page", menu)
        save_page_action.triggered.connect(self.save_page)
        menu.addAction(save_page_action)

        menu.exec_(self.mapToGlobal(pos))

        


    def save_page(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Page", "", "HTML files (*.html);;All files (*.*)")
        if file_name:
            self.page().save(file_name, QWebEngineDownloadItem.CompleteHtmlSaveFormat)
            
            
    
        
    def open_link_in_new_tab(self):
        hit_test_result = self.page().hitTestContent(self.context_menu_event_pos)
        if hit_test_result.isValid() and hit_test_result.type() == QWebEngineContextMenuData.LinkType:
            link_url = hit_test_result.linkUrl()
            new_tab = self.private_browser_instance.add_tab(BrowserTab(self.private_browser_instance.adblocker, self.private_browser_instance.custom_profile), "New Tab")
            new_tab.setUrl(link_url)

        
    def on_load_finished(self, success):
        
        if success:
            css_content = self.adblocker.create_css_injection()
            self.page().runJavaScript(f"const style = document.createElement('style'); style.innerHTML = `{css_content}`; document.head.appendChild(style);")
            
            
 
class PrivateBrowser(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('./favicon.ico'))
        self.adblocker = AdBlocker('./filters')  # Move this line before self.initUI()
        self.initUI()
        
    
    def update_tab_icon(self, tab_index):
        current_tab = self.tabs.widget(tab_index)
        if current_tab:
            self.tabs.setTabIcon(tab_index, current_tab.page().icon())
    
    def update_favicon(self, icon):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            self.tabs.setTabIcon(self.tabs.currentIndex(), icon)        
            
        
    def add_new_tab(self):
        custom_profile = CustomWebEngineProfile(self.adblocker)
        new_tab = BrowserTab(self, self.adblocker, custom_profile)
        self.add_tab(new_tab, "New Tab")
        new_tab.setUrl(QUrl("https://www.google.com"))

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))


    def manage_bookmarks(self):
        bookmark, ok = QInputDialog.getItem(self, 'Bookmarks', 'Select a bookmark:', self.bookmarks, 0, False)

        if ok and bookmark:
            self.navigate_to_bookmark(bookmark)

        add_bookmark_btn = QAction(QIcon('./add_bookmark_icon.png'), 'Add Bookmark', self)
        add_bookmark_btn.triggered.connect(self.add_bookmark)
        self.navtb.addAction(add_bookmark_btn)

    def add_bookmark(self):
        current_url = self.tabs.currentWidget().url().toString()
        self.bookmarks.append(current_url)
        
    def update_ui(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            self.urlbar.setText(current_tab.url().toString())
            self.urlbar.setCursorPosition(0)
            self.setWindowTitle(f"{current_tab.title()} - Private Browser")
            self.resize(1280, 1024)

    def find_text(self):
        search_text, ok = QInputDialog.getText(self, "Find Text", "Enter the text to search:")
        if ok and search_text:
            self.tabs.currentWidget().page.findText(search_text)

    def initUI(self):
        self.tabs = QTabWidget(self)
        self.tabs.setMovable(True)
        custom_profile = CustomWebEngineProfile(self.adblocker)
        browser_tab = BrowserTab(self, self.adblocker, custom_profile)  # Pass `self` as the first argument
        self.add_tab(browser_tab, "New Tab")
        
        #self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

       
       
        #browser_tab = BrowserTab(custom_profile)

        self.navtb = QToolBar("Navigation")
        self.addToolBar(self.navtb)

        back_btn = QAction(QIcon('./back_icon.png'), 'Back', self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navtb.addAction(back_btn)

        add_new_tab_btn = QAction(QIcon('./add_new_tab_icon.png'), 'Add New Tab', self)
        add_new_tab_btn.triggered.connect(self.add_new_tab)
        self.navtb.addAction(add_new_tab_btn)

        next_btn = QAction(QIcon('./forward_icon.png'), 'Forward', self)
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navtb.addAction(next_btn)

        reload_btn = QAction(QIcon('./reload_icon.png'), 'Reload', self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navtb.addAction(reload_btn)

        home_btn = QAction(QIcon('./home_icon.png'), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        self.navtb.addAction(home_btn)

        self.navtb.addSeparator()

        self.urlbar = QLineEdit()
        # Set font size for the URL bar
        font = self.urlbar.font()
        font.setPointSize(14)  # Set the desired font size
        self.urlbar.setFont(font)

        self.urlbar.returnPressed.connect(self.navigate_to_url)

        self.navtb.addWidget(self.urlbar)

        bookmarks_btn = QAction(QIcon('./bookmarks_icon.png'), 'Bookmarks', self)
        bookmarks_btn.triggered.connect(self.manage_bookmarks)
        self.navtb.addAction(bookmarks_btn)

        self.bookmarks = []

        self.tabs.currentChanged.connect(self.update_ui)


        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.find_text)

        self.show()
        self.navigate_home()
        
    def add_tab(self, widget, title):
        new_tab_index = self.tabs.addTab(widget, title)
        self.tabs.setCurrentIndex(new_tab_index)

        widget.page().iconChanged.connect(self.update_ui)
        widget.page().iconChanged.connect(lambda: self.update_tab_icon(new_tab_index))
        widget.loadFinished.connect(self.tab_load_finished)


   

    def tab_load_finished(self):
        current_tab = self.tabs.currentWidget()
        title = current_tab.page().title()
        short_title = title[:30] + "..." if len(title) > 30 else title  # Limit the title length to 30 characters
        index = self.tabs.currentIndex()
        self.tabs.setTabText(index, short_title)

        if current_tab:
            self.tabs.setTabText(self.tabs.currentIndex(), current_tab.page().title())
            self.tabs.setTabIcon(self.tabs.currentIndex(), current_tab.page().icon())


    def create_new_tab_with_url(self, url):
        new_tab = BrowserTab(self.adblocker, custom_profile)
        self.addTab(new_tab, "New Tab")
        new_tab.setUrl(url)
        
    

    def close_tab(self, index):
        if self.tabs.count() > 1:
            browser_tab = self.tabs.widget(index)
            self.tabs.removeTab(index)
            browser_tab.deleteLater()    

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

   


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Private Browser")
    app.setOrganizationName("Private Browser")
    app.setOrganizationDomain("Private Browser")

    main_window = PrivateBrowser()
    main_window.show()

    sys.exit(app.exec_())
if __name__ == "__main__":
    main()