from DrissionPage import ChromiumOptions, Chromium
import sys
import os
from logger import logging


class BrowserManager:
    def __init__(self, extension_path=None):
        self.browser = None
        self.extension_path = extension_path

    def init_browser(self):
        co = self._get_browser_options()
        self.browser = Chromium(co)
        return self.browser
    
    def _get_browser_path(self):
        """获取浏览器可执行文件路径"""
        # 先尝试获取Edge浏览器路径
        edge_path = self._get_edge_path()
        if edge_path:
            return edge_path, "edge"
        
        # 如果Edge不存在，尝试获取Chrome浏览器路径
        chrome_path = self._get_chrome_path()
        if chrome_path:
            return chrome_path, "chrome"
        
        # 两个浏览器都不存在时抛出异常
        raise FileNotFoundError("未找到Edge或Chrome浏览器，请确保已安装其中任意一个浏览器")

    def _get_edge_path(self):
        """获取Edge浏览器可执行文件路径"""
        if sys.platform == "win32":
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
        elif sys.platform == "darwin":
            paths = [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ]
        elif sys.platform == "linux":
            paths = [
                "/usr/bin/microsoft-edge",
                "/usr/bin/microsoft-edge-stable"
            ]
        else:
            return None
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def _get_chrome_path(self):
        """获取Chrome浏览器可执行文件路径"""
        if sys.platform == "win32":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
        elif sys.platform == "darwin":
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]
        elif sys.platform == "linux":
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable"
            ]
        else:
            return None
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def _get_browser_options(self):
        """获取浏览器配置"""
        co = ChromiumOptions()
        
        browser_path, browser_type = self._get_browser_path()
        logging.info(f'browser_path: {browser_path}, browser_type: {browser_type}')

        if browser_path and os.path.exists(browser_path):
            co.set_paths(browser_path)
        try:
            extension_path = self._get_extension_path()
            if extension_path:
                co.add_extension(extension_path)
                logging.info('extension.loaded')
            else:
                logging.warning('extension.not.loaded')
        except Exception as e:
            logging.warning(f'extension.load.error {str(e)}')

        co.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36"
        )
        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")
        proxy = os.getenv('BROWSER_PROXY')
        if proxy:
            logging.info(f'using.proxy {proxy}')
            co.set_proxy(proxy)
        co.auto_port()
        co.headless(os.getenv('BROWSER_HEADLESS', 'True').lower() == 'true')

        if sys.platform == "darwin":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")

        return co

    def _get_extension_path(self):
        if self.extension_path and os.path.exists(self.extension_path):
            return self.extension_path
            
        script_dir = os.path.dirname(os.path.abspath(__file__))
        extension_path = os.path.join(script_dir, "turnstilePatch")
        
        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "turnstilePatch")
        
        if os.path.exists(extension_path):
            required_files = ['manifest.json', 'script.js']
            if all(os.path.exists(os.path.join(extension_path, f)) for f in required_files):
                return extension_path
            else:
                logging.warning(f'not.all.required.files {required_files}')
        else:
            raise FileNotFoundError(f'extension.not.found {extension_path}')
        
        return None

    def quit(self):
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
