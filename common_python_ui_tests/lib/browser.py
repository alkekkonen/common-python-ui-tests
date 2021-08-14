import logging

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from browserstack.local import Local

log = logging.getLogger(__name__)
driver_local = None


class WebDriverProvider:
    """
    Initialize Selenium webdriver, use Chrome as default
    """

    def __init__(self, config, use_driver_proxy=False):
        self.__config = config
        self.__browser = BROWSER_NAMES_MAP[config.browser] if config.browser else 'chrome'
        self.__options = None
        self.__driver = None
        self.__seleniumwire__options = None
        self.__browser_stack_options = None
        self.__browser_stack_local_options = None
        self.use_driver_proxy = use_driver_proxy

    def prepare_options(self):
        self.create_related_options()
        browser_options = self.__options
        default_options = {
            '--no-sandbox',
            '--window-size=1600,1266',
            '--ignore-certificate-errors'
        }

        for option in default_options:
            browser_options.add_argument(option)

        if self.__config.headless:
            browser_options.add_argument('--headless')
            browser_options.add_argument('--disable-gpu')
            browser_options.add_argument('--disable-dev-shm-usage')
        return self

    def create_driver(self):
        if self.__browser == "chrome":
            driver = WrappedChrome(chrome_options=self.__options)
        elif self.__browser == "firefox":
            driver = WrappedFirefox(firefox_options=self.__options)
        elif self.__browser == "browser_stack":
            global driver_local
            if self.__config.browser_stack.binary_path:
                driver_local = Local(binarypath=self.__config.browser_stack.binary_path)
            else:
                driver_local = Local()
            driver_local.stop()
            driver_local.start(**self.__browser_stack_local_options)
            driver = WrappedRemote(**self.__browser_stack_options)
        else:
            raise ValueError(f"Unsupported browser: '{self.__browser}'")

        self.__driver = driver
        self.__driver.implicitly_wait(10)
        self.__driver.set_page_load_timeout(20)
        if self.__browser == "browser_stack" and not self.__browser_stack_options.get('desired_capabilities').get('os',
                                                                                                                  None):
            # don't maximize window for mobile device
            pass
        else:
            self.__driver.maximize_window()

        return self

    def create_related_options(self):
        if self.__browser == "chrome":
            self.__options = webdriver.ChromeOptions()
            if self.use_driver_proxy:
                self.__seleniumwire__options = {'request_storage_base_dir': '/tmp'}
        elif self.__browser == "firefox":
            self.__options = Options()
        elif self.__browser == "browser_stack":
            self.__options = Options()
            self.__browser_stack_local_options = {"key": self.__config.browser_stack.key, "forcelocal": "true"}
            self.__browser_stack_options = {"command_executor": self.__config.browser_stack.command_executor,
                                            "desired_capabilities": self.__config.browser_stack.desired_capabilities[
                                                self.__config.client_type]}
        else:
            raise ValueError(f"Cannot find options for '{self.__browser}' browser")

    def get_instance(self):
        return self.__driver


class IEWebDriverProvider(WebDriverProvider):
    """
    Initialize Selenium webdriver for IE only
    """

    def __init__(self, config):
        super().__init__(config)
        self.__config = config
        self.__browser = BROWSER_NAMES_MAP[config.browser] if config.browser else 'internet_explorer'
        self.__options = None
        self.__driver = None

    def prepare_options(self):
        self.create_related_options()
        return self

    def create_driver(self):
        if self.__browser == "internet_explorer":
            driver = WrappedIe(capabilities=self.__options)
        else:
            raise ValueError(f"IE driver provider does not support '{self.__browser}' browser")

        self.__driver = driver
        self.__driver.maximize_window()
        return self

    def create_related_options(self):
        ie_capabilities = DesiredCapabilities.INTERNETEXPLORER.copy()
        ie_capabilities.pop("platform", None)
        ie_capabilities.pop("version", None)
        ie_capabilities["se:ieOptions"] = {}
        ie_capabilities["se:ieOptions"]["ie.ensureCleanSession"] = True
        self.__options = ie_capabilities
        return self

    def get_instance(self):
        return self.__driver


class WrappedBrowser:
    """
    Functions to interact with iFrames
    """

    IFRAME_FOCUS = None

    def switch_to_iframe(self, wait_time, frame_name):
        WebDriverWait(self, wait_time).until(
            EC.frame_to_be_available_and_switch_to_it(frame_name)
        )
        self.IFRAME_FOCUS = frame_name

    def switch_back_from_iframe(self):
        super().switch_to_default_content()
        self.IFRAME_FOCUS = None


class WrappedChrome(WrappedBrowser, webdriver.Chrome):
    pass


class WrappedFirefox(WrappedBrowser, webdriver.Firefox):
    pass


class WrappedIe(WrappedBrowser, webdriver.Ie):
    pass


class WrappedRemote(WrappedBrowser, webdriver.Remote):
    pass


class Downloads:
    """
    Function for changing download settings directly from the test steps
    """
    @staticmethod
    def set_files_download_capabilities(browser, download_dir):
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        }
        browser.create_options().add_experimental_option('prefs', prefs)

        # Enable downloading files in headless mode
        # Workaround for Chromium issue (see chromium/issues/detail?id=696481)
        browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        browser.execute("send_command", params)


# To handle '--browser' arg variants only, can be removed
BROWSER_NAMES_MAP = {
    'chrome': 'chrome',
    'firefox': 'firefox',
    'ff': 'firefox',
    'internet_explorer': 'internet_explorer',
    'ie': 'internet_explorer',
    'browser-stack': 'browser_stack'
}
