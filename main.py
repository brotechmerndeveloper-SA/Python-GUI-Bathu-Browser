import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPalette, QColor


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = QWebEngineView()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        self.setLayout(layout)


class TabbedBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.urlbar = None
        self.theme_btn = None
        self.current_theme = "netflix"
        self.browser_name = "Bathu Browser"
        self.search_engine = "brave"  # Brave Search as default
        self.initUI()

    def initUI(self):
        # Create navigation toolbar FIRST
        navtb = QToolBar("Navigation")
        navtb.setMovable(False)
        navtb.setStyleSheet("""
            QToolBar {
                background-color: #141414;
                border: none;
                padding: 5px;
                spacing: 5px;
            }
            QToolBar QToolButton {
                background-color: #E50914;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 30px;
            }
            QToolBar QToolButton:hover {
                background-color: #F40612;
            }
            QToolBar QToolButton:pressed {
                background-color: #B2070F;
            }
        """)
        self.addToolBar(navtb)

        # New tab button
        new_tab_btn = QAction("➕", self)
        new_tab_btn.setStatusTip("Open new tab")
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(new_tab_btn)

        # Back button
        back_btn = QAction("◀", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(self.navigate_back)
        navtb.addAction(back_btn)

        # Forward button
        forward_btn = QAction("▶", self)
        forward_btn.setStatusTip("Forward to next page")
        forward_btn.triggered.connect(self.navigate_forward)
        navtb.addAction(forward_btn)

        # Reload button
        self.reload_btn = QAction("🔄", self)
        self.reload_btn.setStatusTip("Reload page")
        self.reload_btn.triggered.connect(self.navigate_reload)
        navtb.addAction(self.reload_btn)

        # Home button
        home_btn = QAction("🏠", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # Address bar
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Search with Brave or enter website address...")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.urlbar.setStyleSheet("""
            QLineEdit {
                background-color: #2D2D2D;
                color: white;
                border: 2px solid #404040;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                selection-background-color: #E50914;
            }
            QLineEdit:focus {
                border-color: #E50914;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        navtb.addWidget(self.urlbar)

        # Theme toggle button
        self.theme_btn = QAction("🎬", self)
        self.theme_btn.setStatusTip("Change theme")
        self.theme_btn.triggered.connect(self.toggle_theme)
        navtb.addAction(self.theme_btn)

        # Create menu bar
        self.createMenus()

        # Create tab widget with Netflix style
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #141414;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #2D2D2D;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #E50914;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #404040;
            }
            QTabBar::close-button {
                image: url(none);
                subcontrol-origin: padding;
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                background-color: #E50914;
                border-radius: 8px;
            }
        """)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)

        # Create initial tab with CUSTOM HOME PAGE
        self.add_new_tab(self.get_netflix_home_page_html(), is_html=True)

        # Set central widget
        self.setCentralWidget(self.tabs)

        # Status bar with Netflix style
        self.status = QStatusBar()
        self.status.setStyleSheet("""
            QStatusBar {
                background-color: #141414;
                color: #808080;
                border-top: 1px solid #2D2D2D;
            }
        """)
        self.setStatusBar(self.status)
        self.status.showMessage(f"Welcome to {self.browser_name} - Powered by Brave Search")

        # Set window properties
        self.setWindowTitle(self.browser_name)
        self.setGeometry(100, 100, 1400, 900)

        # Add shortcuts
        self.add_shortcuts()

        # Set Netflix theme AFTER all UI elements are created
        self.setApplicationStyle("netflix")

    def get_search_url(self, query):
        """Get search URL based on selected search engine"""
        search_engines = {
            "brave": f"https://search.brave.com/search?q={query}",
            "duckduckgo": f"https://duckduckgo.com/?q={query}",
            "bing": f"https://www.bing.com/search?q={query}",
            "yahoo": f"https://search.yahoo.com/search?p={query}",
            "startpage": f"https://www.startpage.com/sp/search?query={query}",
            "ecosia": f"https://www.ecosia.org/search?q={query}",
            "google": f"https://www.google.com/search?q={query}"
        }
        return search_engines.get(self.search_engine, search_engines["brave"])

    def get_netflix_home_page_html(self):
        """Return Netflix-style HTML for Nexus Browser homepage"""
        search_engine_name = "Brave Search"
        search_engine_icon = "🦁"
        search_engine_desc = "Privacy-first with independent index"

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.browser_name} - Home</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    background: #141414;
                    color: white;
                    min-height: 100vh;
                    overflow-x: hidden;
                }}
                .netflix-header {{
                    background: linear-gradient(to bottom, rgba(0,0,0,0.8) 0%, transparent 100%);
                    padding: 20px 50px;
                    position: fixed;
                    width: 100%;
                    top: 0;
                    z-index: 1000;
                }}
                .logo {{
                    color: #E50914;
                    font-size: 2.5em;
                    font-weight: bold;
                    font-family: 'Arial Black', sans-serif;
                }}
                .hero {{
                    height: 100vh;
                    background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                                url('https://assets.nflxext.com/ffe/siteui/vlv3/5e16108c-fd30-46de-9bb8-0b4e1bbbc509/29d8d7d7-83cc-4b5f-aa9b-6fd4f68bfaa6/IN-en-20240205-popsignuptwoweeks-perspective_alpha_website_large.jpg');
                    background-size: cover;
                    background-position: center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    padding: 0 20px;
                }}
                .hero-content {{
                    max-width: 800px;
                    z-index: 2;
                }}
                .hero h1 {{
                    font-size: 4em;
                    font-weight: bold;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }}
                .hero p {{
                    font-size: 1.5em;
                    margin-bottom: 30px;
                    opacity: 0.9;
                }}
                .search-info {{
                    background: linear-gradient(135deg, #FF2000, #FF9300);
                    color: white;
                    padding: 15px 25px;
                    border-radius: 8px;
                    margin-bottom: 25px;
                    font-size: 1.2em;
                    font-weight: bold;
                    border: 2px solid #FF9300;
                    box-shadow: 0 4px 15px rgba(255, 32, 0, 0.3);
                }}
                .brave-icon {{
                    font-size: 1.3em;
                    margin-right: 10px;
                }}
                .search-container {{
                    background: rgba(0,0,0,0.7);
                    padding: 40px;
                    border-radius: 8px;
                    backdrop-filter: blur(10px);
                    border: 1px solid #333;
                }}
                .search-input {{
                    width: 100%;
                    padding: 15px 20px;
                    font-size: 1.2em;
                    background: rgba(255,255,255,0.1);
                    border: 2px solid #333;
                    border-radius: 4px;
                    color: white;
                    outline: none;
                    margin-bottom: 20px;
                }}
                .search-input:focus {{
                    border-color: #FF2000;
                }}
                .search-input::placeholder {{
                    color: #ccc;
                }}
                .quick-links {{
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    flex-wrap: wrap;
                    margin-top: 20px;
                }}
                .netflix-btn {{
                    background: #E50914;
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 4px;
                    font-size: 1.1em;
                    font-weight: bold;
                    cursor: pointer;
                    transition: background 0.3s ease;
                    text-decoration: none;
                    display: inline-block;
                }}
                .netflix-btn:hover {{
                    background: #F40612;
                }}
                .brave-btn {{
                    background: linear-gradient(135deg, #FF2000, #FF9300);
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 4px;
                    font-size: 1.1em;
                    font-weight: bold;
                    cursor: pointer;
                    transition: transform 0.2s ease;
                    text-decoration: none;
                    display: inline-block;
                }}
                .brave-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(255, 32, 0, 0.4);
                }}
                .link-btn {{
                    background: transparent;
                    border: 1px solid #666;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 4px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                }}
                .link-btn:hover {{
                    border-color: #E50914;
                    color: #E50914;
                }}
                .features {{
                    padding: 80px 50px;
                    background: #141414;
                }}
                .feature-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 30px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .feature-card {{
                    background: #2D2D2D;
                    padding: 30px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #E50914;
                    transition: transform 0.3s ease;
                }}
                .feature-card:hover {{
                    transform: translateY(-5px);
                }}
                .feature-icon {{
                    font-size: 3em;
                    margin-bottom: 20px;
                }}
                .feature-card h3 {{
                    color: #E50914;
                    margin-bottom: 15px;
                    font-size: 1.3em;
                }}
                .brave-feature {{
                    border-left-color: #FF2000;
                }}
                .brave-feature h3 {{
                    color: #FF9300;
                }}
                .netflix-footer {{
                    background: #141414;
                    border-top: 1px solid #333;
                    padding: 30px 50px;
                    text-align: center;
                    color: #808080;
                }}
                @media (max-width: 768px) {{
                    .hero h1 {{
                        font-size: 2.5em;
                    }}
                    .hero p {{
                        font-size: 1.2em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="netflix-header">
                <div class="logo">{self.browser_name}</div>
            </div>

            <div class="hero">
                <div class="hero-content">
                    <h1>Welcome to {self.browser_name}</h1>
                    <p>Experience the web in Netflix style - Dark, Beautiful, and Fast</p>

                    <div class="search-info">
                        <span class="brave-icon">🦁</span>
                        Powered by Brave Search - {search_engine_desc}
                    </div>

                    <div class="search-container">
                        <input type="text" class="search-input" id="searchInput" 
                               placeholder="Search with Brave Search... (Press Enter to search)"
                               onkeypress="handleSearch(event)">

                        <div class="quick-links">
                            <a href="https://search.brave.com" class="brave-btn">Brave Search</a>
                            <a href="https://www.netflix.com" class="netflix-btn">Netflix</a>
                            <a href="https://www.youtube.com" class="link-btn">YouTube</a>
                            <a href="https://www.github.com" class="link-btn">GitHub</a>
                        </div>
                    </div>
                </div>
            </div>

            <div class="features">
                <div class="feature-grid">
                    <div class="feature-card brave-feature">
                        <div class="feature-icon">🦁</div>
                        <h3>Brave Search Powered</h3>
                        <p>Privacy-first search with independent index. No tracking, no profiling.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎬</div>
                        <h3>Netflix Style</h3>
                        <p>Beautiful dark theme with iconic red accents and smooth animations</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <h3>Privacy Focused</h3>
                        <p>Brave Search ensures your searches remain private and secure</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3>Lightning Fast</h3>
                        <p>Optimized for speed with Brave's fast search results</p>
                    </div>
                </div>
            </div>

            <div class="netflix-footer">
                <p>&copy; 2025 {self.browser_name}. 🦁 Powered by Brave Search for private, independent searching.</p>
            </div>

            <script>
                function handleSearch(event) {{
                    if (event.key === 'Enter') {{
                        const query = document.getElementById('searchInput').value;
                        if (query) {{
                            window.location.href = 'https://search.brave.com/search?q=' + encodeURIComponent(query);
                        }}
                    }}
                }}

                // Focus search input on page load
                document.getElementById('searchInput').focus();

                // Add some interactive effects
                document.addEventListener('DOMContentLoaded', function() {{
                    const featureCards = document.querySelectorAll('.feature-card');
                    featureCards.forEach(card => {{
                        card.addEventListener('mouseenter', function() {{
                            this.style.transform = 'translateY(-5px)';
                        }});
                        card.addEventListener('mouseleave', function() {{
                            this.style.transform = 'translateY(0)';
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """

    def createMenus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #141414;
                color: white;
                border: none;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #E50914;
            }
            QMenu {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #404040;
                border-radius: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #E50914;
            }
            QMenu::separator {
                background-color: #404040;
                height: 1px;
            }
        """)

        # File menu
        file_menu = menubar.addMenu("&File")

        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        new_window_action = QAction("New Window", self)
        new_window_action.setShortcut("Ctrl+N")
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        dark_mode_action = QAction("Toggle Theme", self)
        dark_mode_action.setShortcut("Ctrl+D")
        dark_mode_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(dark_mode_action)

    def setApplicationStyle(self, theme):
        self.current_theme = theme

        if theme == "netflix":
            # Netflix theme - Black and Red
            netflix_palette = QPalette()
            netflix_palette.setColor(QPalette.Window, QColor(20, 20, 20))  # #141414
            netflix_palette.setColor(QPalette.WindowText, Qt.white)
            netflix_palette.setColor(QPalette.Base, QColor(45, 45, 45))  # #2D2D2D
            netflix_palette.setColor(QPalette.AlternateBase, QColor(20, 20, 20))
            netflix_palette.setColor(QPalette.ToolTipBase, QColor(229, 9, 20))  # #E50914
            netflix_palette.setColor(QPalette.ToolTipText, Qt.white)
            netflix_palette.setColor(QPalette.Text, Qt.white)
            netflix_palette.setColor(QPalette.Button, QColor(45, 45, 45))  # #2D2D2D
            netflix_palette.setColor(QPalette.ButtonText, Qt.white)
            netflix_palette.setColor(QPalette.BrightText, Qt.red)
            netflix_palette.setColor(QPalette.Link, QColor(229, 9, 20))  # #E50914
            netflix_palette.setColor(QPalette.Highlight, QColor(229, 9, 20))  # #E50914
            netflix_palette.setColor(QPalette.HighlightedText, Qt.white)

            QApplication.setPalette(netflix_palette)
            if self.theme_btn:
                self.theme_btn.setText("🎬")

    def toggle_theme(self):
        self.setApplicationStyle("netflix")

    def add_shortcuts(self):
        # Ctrl+T for new tab
        new_tab = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab.activated.connect(lambda: self.add_new_tab())

        # Ctrl+W to close tab
        close_tab = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab.activated.connect(self.close_current_tab)

        # Ctrl+L to focus address bar
        focus_url = QShortcut(QKeySequence("Ctrl+L"), self)
        focus_url.activated.connect(self.focus_address_bar)

        # Ctrl+R to reload
        reload = QShortcut(QKeySequence("Ctrl+R"), self)
        reload.activated.connect(self.navigate_reload)

        # Ctrl+Q to quit
        quit_app = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_app.activated.connect(self.close)

        # Ctrl+D for theme toggle
        theme_toggle = QShortcut(QKeySequence("Ctrl+D"), self)
        theme_toggle.activated.connect(self.toggle_theme)

    def add_new_tab(self, url=None, label="New Tab", is_html=False):
        browser_tab = BrowserTab()
        i = self.tabs.addTab(browser_tab, label)
        self.tabs.setCurrentIndex(i)

        # Connect signals
        browser_tab.browser.urlChanged.connect(
            lambda q, browser=browser_tab.browser: self.update_urlbar(q, browser))
        browser_tab.browser.loadFinished.connect(
            lambda _, browser=browser_tab.browser, index=i: self.update_tab_title(browser, index))
        browser_tab.browser.loadStarted.connect(
            lambda: self.status.showMessage("Loading..."))
        browser_tab.browser.loadFinished.connect(
            lambda ok: self.status.showMessage("Ready" if ok else "Load failed"))

        if is_html:
            # Load custom HTML content
            browser_tab.browser.setHtml(url, QUrl("about:blank"))
        elif url is None:
            # Load custom home page
            browser_tab.browser.setHtml(self.get_netflix_home_page_html(), QUrl("about:blank"))
        else:
            # Load external URL
            browser_tab.browser.setUrl(QUrl(url))

        return browser_tab

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        if self.tabs.count() > 1:
            self.tabs.removeTab(current_index)

    def current_tab_changed(self, i):
        if i >= 0 and self.urlbar is not None:
            current_browser = self.tabs.widget(i).browser
            self.update_urlbar(current_browser.url(), current_browser)

    def get_current_browser(self):
        if self.tabs.currentWidget() is not None:
            return self.tabs.currentWidget().browser
        return None

    def navigate_back(self):
        browser = self.get_current_browser()
        if browser:
            browser.back()

    def navigate_forward(self):
        browser = self.get_current_browser()
        if browser:
            browser.forward()

    def navigate_reload(self):
        browser = self.get_current_browser()
        if browser:
            browser.reload()

    def navigate_home(self):
        browser = self.get_current_browser()
        if browser:
            # Load custom Netflix home page HTML
            browser.setHtml(self.get_netflix_home_page_html(), QUrl("about:blank"))

    def navigate_to_url(self):
        if self.urlbar is None:
            return

        url = self.urlbar.text()
        browser = self.get_current_browser()
        if not browser:
            return

        if not url:
            return

        if not url.startswith(('http://', 'https://', 'file://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                # Use Brave Search
                url = self.get_search_url(url)

        browser.setUrl(QUrl(url))

    def update_urlbar(self, q, browser=None):
        if (self.urlbar is not None and
                browser == self.get_current_browser()):
            current_url = q.toString()
            # Show empty for home page, actual URL for other pages
            if current_url == "about:blank":
                self.urlbar.setText("")
                self.urlbar.setPlaceholderText(f"{self.browser_name} - Powered by Brave Search 🦁")
            else:
                self.urlbar.setText(current_url)
                self.urlbar.setCursorPosition(0)

    def update_tab_title(self, browser, index):
        title = browser.page().title()
        current_url = browser.url().toString()

        # Customize what's shown in the tab
        if current_url == "about:blank":
            display_title = f"{self.browser_name} 🦁"
        elif title:
            display_title = title
            if len(display_title) > 25:
                display_title = display_title[:25] + "..."
        else:
            display_title = "New Tab 🦁"

        self.tabs.setTabText(index, display_title)

        # Update window title
        if index == self.tabs.currentIndex():
            self.setWindowTitle(f"{display_title} - {self.browser_name}")

    def focus_address_bar(self):
        if self.urlbar is not None:
            self.urlbar.selectAll()
            self.urlbar.setFocus()

    def new_window(self):
        new_browser = TabbedBrowser()
        new_browser.show()


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Bathu Browser")
    app.setApplicationDisplayName("Bathu Browser")

    app.setStyle('Fusion')

    window = TabbedBrowser()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()