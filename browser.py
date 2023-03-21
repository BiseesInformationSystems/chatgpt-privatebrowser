import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QStatusBar,
                             QVBoxLayout, QTabWidget, QWidget, QInputDialog)
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QInputDialog, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QDialog, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
#from PyQt5.QtWebEngineCore import QWebEngineProfile, QWebEngineCookieStore
from PyQt5.QtWebEngineWidgets import QWebEngineProfile



from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem

class WebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked and isMainFrame:
            self.parent().parent().create_new_tab_with_url(url)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class BrowserTab(QWebEngineView):
    favicon_changed = pyqtSignal(QIcon)
    def __init__(self, private_browser_instance):
        super().__init__(private_browser_inst)
        self.private_browser_instance = private_browser_instance
        self.page().iconChanged.connect(self._icon_changed)
        self.private_browser_instance = private_browser_instance
        self.context_menu_event_pos = None
        # Connect the downloadRequested signal to the handle_download_requested slot
        settings = self.settings()
        default_font_size = settings.fontSize(QWebEngineSettings.DefaultFontSize)
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, default_font_size + 2)

        self.page().profile().downloadRequested.connect(self.handle_download_requested)
        
        self.custom_profile = CustomWebEngineProfile()
        self.page().setProfile(self.custom_profile)

        self.setPage(WebPage(self))
    
    def favicon(self):
        return self.page().icon()

    
    def _icon_changed(self, icon):
        self.favicon_changed.emit(icon)

    def handle_download_requested(self, download):
        if download.type() == QWebEngineDownloadItem.UserRequested:
            download.cancel()
            self.private_browser_instance.create_new_tab_with_url(download.url())
    
    #def __init__(self):
    #    super().__init__()
        
    def __init__(self, private_browser_instance):
        super().__init__()
        self.private_browser_instance = private_browser_instance    

    def createWindow(self, _type):
        
        
        new_tab = BrowserTab(self.parent().parent())
        self.parent().parent().addTab(new_tab, "New Tab")
        return new_tab
        
    def open_link_in_new_tab(self):
        hit_test_result = self.page().hitTestContent(self.context_menu_event_pos)
        if hit_test_result.isValid() and hit_test_result.type() == QWebEngineContextMenuData.LinkType:
            link_url = hit_test_result.linkUrl()
            new_tab = self.parent().parent().add_tab(BrowserTab(self.private_browser_instance), "New Tab")
            new_tab.setUrl(link_url)


    #def open_link_in_new_tab(self, event):
    #        hit_test = self.page().hitTestContent(event.pos())
    #        if hit_test.linkUrl().isValid():
    #            self.parent().parent().create_new_tab_with_url(hit_test.linkUrl())
        
    #def contextMenuEvent(self, event):
    #    menu = QMenu(self)
    #    save_action = QAction('Save Page', self)
    #    
    #    save_page_action = menu.addAction("Save Page")#

    #    #save_action.triggered.connect(self.parent().parent().save_page)
    #    save_page_action.triggered.connect(self.parent().parent().save_page)

        
    #    #save_page_action.triggered.connect(self.parent().save_page)

    #    # Add other context menu actions here...
    #    menu.addAction(save_page_action)
    #    menu.exec_(event.globalPos())
    #    menu.addAction(save_action)


    def contextMenuEvent(self, event):
        self.context_menu_event_pos = event.pos()
        # Create the standard context menu
        context_menu = self.page().createStandardContextMenu()

        # Add a separator
        context_menu.addSeparator()

        # Back action
        back_action = QAction('Back', self)
        back_action.triggered.connect(self.back)
        context_menu.addAction(back_action)

        # Forward action
        forward_action = QAction('Forward', self)
        forward_action.triggered.connect(self.forward)
        context_menu.addAction(forward_action)

        # Reload action
        reload_action = QAction('Reload', self)
        reload_action.triggered.connect(self.reload)
        context_menu.addAction(reload_action)

        # Open Link in New Tab action
        #open_link_in_new_tab_action = QAction("Open Link in New Tab", self)
        #open_link_in_new_tab_action.triggered.connect(self.open_link_in_new_tab)
        #open_link_in_new_tab_action.triggered.connect(lambda: self.open_link_in_new_tab(event.pos()))

        #context_menu.addAction(open_link_in_new_tab_action)

        # Save Page action
        #save_page_action = QAction('Save Page', self)
        #save_page_action.triggered.connect(lambda: self.parent().parent().save_current_page())
        #context_menu.addAction(save_page_action)

        # View Page Source action
        #view_source_action = QAction('View Page Source', self)
        #view_source_action.triggered.connect(self.view_page_source)
        #context_menu.addAction(view_source_action)

        # Show the context menu at the cursor's position
        context_menu.exec_(event.globalPos())


    def save_page(self):
        current_page = self.page()
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix("html")
        file_name, _ = file_dialog.getSaveFileName(self, "Save Page As", "", "HTML Files (*.html);;All Files (*)")

        if file_name:
            request = QWebEngineDownloadRequest(current_page.url())
            request.setSavePageFormat(QWebEngineDownloadRequest.CompleteHtmlSaveFormat)
            request.setPath(file_name)
            current_page.profile().download(request)

    def view_page_source(self):
        current_page = self.page()
        current_page.toHtml(self.show_page_source)

    def show_page_source(self, source):
        source_dialog = QDialog(self)
        source_dialog.setWindowTitle("Page Source")
        
        text_edit = QTextEdit(source_dialog)
        text_edit.setPlainText(source)
        text_edit.setReadOnly(True)
        
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        source_dialog.setLayout(layout)
        
        source_dialog.resize(800, 600)
        source_dialog.exec_()
    
        
class PrivateBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the application icon
        self.setWindowIcon(QIcon('./favicon.ico'))

        self.initUI()


    
    def update_favicon(self, icon):
        current_tab_index = self.tabs.currentIndex()
        self.tabs.setTabIcon(current_tab_index, icon)
    
    
    def current_tab(self):
        return self.tabs.currentWidget()
        
    def save_current_page(self):
        self.current_tab().save_page()    

    def find_text(self):
        search_text, ok = QInputDialog.getText(self, "Find Text", "Enter the text to search:")
        if ok and search_text:
            self.tabs.currentWidget().page().findText(search_text)
    
    #def save_page(self):
    #    options = QFileDialog.Options()
    #    options |= QFileDialog.ReadOnly
    #    file_name, _ = QFileDialog.getSaveFileName(self, "Save Page As", "", "HTML Files (*.html);;All Files (*)", options=options)
    #    if file_name:
    #        self.web_view.page().save(file_name, QWebEngineDownloadItem.SingleHtmlSaveFormat)
    #        #page_html = self.tabs.currentWidget().page().toHtml()
    #        #with open(file_name, 'w', encoding='utf-8') as f:
    #       #    f.write(page_html)
    
    

    # ...

    
    def create_new_tab_with_url(self, url):
        new_tab = BrowserTab(self)
        new_tab_index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(new_tab_index)
        new_tab.setUrl(url)    
        

    # ...


    
    def initUI(self):
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        
        
        
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

        self.add_tab(BrowserTab(self), "New Tab")
        
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.find_text)

        self.show()
        self.navigate_home()

    def update_ui(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            self.urlbar.setText(current_tab.url().toString())
            self.urlbar.setCursorPosition(0)
            self.setWindowTitle(f"{current_tab.title()} - Private Browser")
            self.resize(1280, 1024)
            
    #def add_tab(self, widget=None, title="New Tab"):
    #    if not widget:
    #        widget = BrowserTab(self)
    #    new_tab_index = self.tabs.addTab(widget, title)        
    #    self.tabs.setCurrentIndex(new_tab_index)

    #    widget.urlChanged.connect(lambda q: self.urlbar.setText(q.toString()))
    #    widget.loadFinished.connect(lambda: self.tabs.setTabText(self.tabs.currentIndex(), widget.page().title()))
        
        
    def add_tab(self, widget, title):
        new_tab_index = self.tabs.addTab(widget, title)
        self.tabs.setCurrentIndex(new_tab_index)

        widget.urlChanged.connect(lambda q: self.urlbar.setText(q.toString()))
        widget.loadFinished.connect(self.tab_load_finished)
        widget.page().iconChanged.connect(self.update_favicon)  

        
        

        

        new_tab_index = self.tabs.addTab(widget, title)
        self.tabs.setCurrentIndex(new_tab_index)

        widget.urlChanged.connect(lambda q: self.urlbar.setText(q.toString()))
        widget.loadFinished.connect(lambda: self.tabs.setTabText(self.tabs.currentIndex(), widget.page().title()))
        widget.favicon_changed.connect(lambda icon, index=new_tab_index: self.tabs.setTabIcon(index, icon))   
    
    def add_new_tab(self):
        self.add_tab(BrowserTab(self), "New Tab")
        
    def tab_load_finished(self):
        current_tab = self.tabs.currentWidget()
        title = current_tab.page().title()
        short_title = title[:30] + "..." if len(title) > 30 else title  # Limit the title length to 30 characters
        index = self.tabs.currentIndex()
        self.tabs.setTabText(index, short_title)
        
        
        if current_tab:
            self.tabs.setTabText(self.tabs.currentIndex(), current_tab.page().title())
            self.tabs.setTabIcon(self.tabs.currentIndex(), current_tab.favicon())
        
            
    def create_new_tab_with_url(self, url):
        new_tab = BrowserTab()
        self.addTab(new_tab, "New Tab")
        new_tab.setUrl(url)    

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)
        
        
        

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

    def navigate_to_bookmark(self, bookmark_url):
        q = QUrl(bookmark_url)
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

def main():
    app = QApplication(sys.argv)
    mainWin = PrivateBrowser()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


