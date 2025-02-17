from abc import ABC, abstractmethod
from selenium.webdriver import Firefox
import tempfile
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from dataclasses_json import config as DCJConfig
from pathlib import Path
#from ..socket_interface import ClientSocket
#from ..config import BrowserParamsInternal, ManagerParamsInternal
#from ..socket_interface import ClientSocket
from typing import NewType
import hashlib
from hashlib import md5

VisitId = NewType("VisitId", int)
BrowserId = NewType("BrowserId", int)
def str_to_path(string: Optional[str]) -> Optional[Path]:
    if string is not None:
        return Path(string)
    return None


def path_to_str(path: Optional[Path]) -> Optional[str]:
    if path is not None:
        return str(path.resolve())
    return None
@dataclass
class ManagerParams(DataClassJsonMixin):
    """
    Configuration for the TaskManager
    The configuration will be the same for all browsers running on the same
    TaskManager.
    It can be used to control storage locations or which watchdogs should
    run
    """

    data_directory: Path = field(
        default=Path.home() / "openwpm",
        metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path),
    )
    """The directory into which screenshots and page dumps will be saved"""
    log_path: Path = field(
        default=Path.home() / "openwpm" / "openwpm.log",
        metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path),
    )
    """The path to the file in which OpenWPM will log. The
    directory given will be created if it does not exist."""
    testing: bool = False
    """A platform wide flag that can be used to only run certain functionality
    while testing. For example, the Javascript instrumentation"""
    memory_watchdog: bool = False
    """A watchdog that tries to ensure that no Firefox instance takes up too much memory.
    It is mostly useful for long running cloud crawls"""
    process_watchdog: bool = False
    """It is used to create another thread that kills off `GeckoDriver` (or `Xvfb`)
    instances that haven't been spawned by OpenWPM. (GeckoDriver is used by
    Selenium to control Firefox and Xvfb a "virtual display" so we simulate having graphics when running on a server).
    """

    num_browsers: int = 1
    _failure_limit: Optional[int] = None
    """The number of command failures the platform will tolerate before raising a
        `CommandExecutionError` exception. Otherwise the default is set to 2 x the
         number of browsers plus 10. The failure counter is reset at the end of each
         successfully completed command sequence.
       For non-blocking command sequences that cause the number of failures to
         exceed `failure_limit` the `CommandExecutionError` is raised when
         attempting to execute the next command sequence."""

    @property
    def failure_limit(self) -> int:
        if self._failure_limit is None:
            return 2 * self.num_browsers + 10
        return self._failure_limit

    @failure_limit.setter
    def failure_limit(self, value: int) -> None:
        self._failure_limit = value

@dataclass
class BrowserParams(DataClassJsonMixin):
    """
    Configuration that might differ per browser

    OpenWPM allows you to run multiple browsers with different
    configurations in parallel and this class allows you
    to customize behaviour of an individual browser
    """

    extension_enabled: bool = True
    cookie_instrument: bool = True
    js_instrument: bool = False
    js_instrument_settings: List[Union[str, dict]] = field(
        default_factory=lambda: ["collection_fingerprinting"]
    )
    http_instrument: bool = False
    navigation_instrument: bool = False
    save_content: Union[bool, str] = False
    callstack_instrument: bool = False
    dns_instrument: bool = False
    seed_tar: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )
    display_mode: Literal["native", "headless", "xvfb"] = "native"
    browser: str = "firefox"
    prefs: dict = field(default_factory=dict)
    tp_cookies: str = "always"
    bot_mitigation: bool = False
    profile_archive_dir: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )

    tmp_profile_dir: Path = field(
        default=Path(tempfile.gettempdir()),
        metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path),
    )
    """
    The tmp_profile_dir defaults to the OS's temporary file folder (typically /tmp) and is where the generated 
    browser profiles and residual files are stored.
    """

    maximum_profile_size: Optional[int] = None
    """
    The total amount of on disk space the generated 
    browser profiles and residual files are allowed to consume in bytes.
    If this option is not set, no checks will be performed

    Rationale
    ---------
    This option can serve as a happy medium between killing a browser after each
    crawl and allowing the application to still perform quickly.

    Used as a way to save space
    in a limited environment with minimal detriment to speed.

    If the maximum_profile_size is exceeded after a CommandSequence
    is completed, the browser will be shut down and a new one will
    be created. **Even with this setting you may temporarily have
    more disk usage than the sum of all maximum_profile_sizes**
    However, this will also ensure that a CommandSequence is
    allowed to complete without undue interruptions.

    Sample values
    -------------
    * 1073741824: 1GB
    * 20971520:  20MB - for testing purposes
    * 52428800:  50MB
    * 73400320:  70MB
    * 104857600: 100MB - IDEAL for 10+ browsers

    """

    recovery_tar: Optional[Path] = None
    donottrack: bool = False
    tracking_protection: bool = False
    custom_params: Dict[Any, Any] = field(default_factory=lambda: {})
class ClientSocket:
    """A client socket for sending messages"""

    def __init__(self, serialization="json", verbose=False):
        """`serialization` specifies the type of serialization to use for
        non-string messages. Supported formats:
            * 'json' uses the json module. Cross-language support. (default)
            * 'dill' uses the dill pickle module. Python only.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if serialization != "json" and serialization != "dill":
            raise ValueError("Unsupported serialization type: %s" % serialization)
        self.serialization = serialization
        self.verbose = verbose

    def connect(self, host, port):
        if self.verbose:
            print("Connecting to: %s:%i" % (host, port))
        self.sock.connect((host, port))

    def send(self, msg):
        """
        Sends an arbitrary python object to the connected socket. Serializes
        using dill if not string, and prepends msg len (4-bytes) and
        serialization type (1-byte).
        """
        if isinstance(msg, bytes):
            serialization = b"n"
        elif isinstance(msg, str):
            serialization = b"u"
            msg = msg.encode("utf-8")
        elif self.serialization == "dill":
            msg = dill.dumps(msg, dill.HIGHEST_PROTOCOL)
            serialization = b"d"
        elif self.serialization == "json":
            msg = json.dumps(msg).encode("utf-8")
            serialization = b"j"
        else:
            raise ValueError(
                "Unsupported serialization type set: %s" % self.serialization
            )
        if self.verbose:
            print("Sending message with serialization %s" % serialization)

        # prepend with message length
        msg = struct.pack(">Lc", len(msg), serialization) + msg
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def close(self):
        self.sock.close()
@dataclass
class BrowserParamsInternal(BrowserParams):
    browser_id: Optional[BrowserId] = None
    profile_path: Optional[Path] = None
    cleaned_js_instrument_settings: Optional[List[Dict[str, Any]]] = None


@dataclass
class ManagerParamsInternal(ManagerParams):
    storage_controller_address: Optional[Tuple[str, int]] = None
    logger_address: Optional[Tuple[str, ...]] = None
    screenshot_path: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )
    source_dump_path: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )

class BaseCommand(ABC):
    """
    Base class for all Commands in OpenWPM

    See `custom_command.py` for instructions on how
    to implement your own and `openwpm/commands` for
    all commands that are already implemented
    """

    def set_visit_browser_id(self, visit_id, browser_id):
        self.visit_id = visit_id
        self.browser_id = browser_id

    def set_start_time(self, start_time):
        self.start_time = start_time

    @abstractmethod
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParamsInternal,
        manager_params: ManagerParamsInternal,
        extension_socket: ClientSocket,
    ) -> None:
        """This method gets called in the Browser process

        :parameter webdriver: WebDriver is a Selenium class used to control
            browser. You can simulate arbitrary interactions and extract almost
            all browser state with the tools that Selenium gives you
        :parameter browser_params: Contains the per browser configuration
            E.g. which instruments are enabled
        :parameter manager_params: Per crawl parameters E.g. where to store files
        :parameter extension_socket: Communication channel to the storage provider

            TODO: Further document this once the StorageProvider PR has landed
            This allows you to send data to be persisted to storage.
        """
        pass



# from selenium import webdriver
# from hashlib import md5
# import gzip
# import json
# import logging
# import os
# import random
# import sys
# import time
# import traceback
# from glob import glob
# driver = webdriver.Firefox()

# # Navigate to a web page
# driver.get("https://www.ebay.co.uk/")
# time.sleep(3)

# # Create a DumpPageSourceCommand instance with a suffix (if needed)
# dump_command = DumpPageSourceCommand(suffix="example")

# # Execute the command to save the page source
# dump_command.execute(
#     webdriver=driver,
#     browser_params={},  # Replace with appropriate browser parameters
#     manager_params={
#         "source_dump_path": "./dump/"
#     },  # Replace with the path where you want to save the source
#     extension_socket=None,  # Optional extension socket
# )

# # Close the browser
# input("Press Enter to close the browser...")
# driver.quit()