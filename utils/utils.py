from selenium.webdriver.remote.webdriver import WebDriver
import pathlib
import re
from typing import Union
from constants.constants import DL_DIR, URL_LIST
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from pathlib import Path
import shutil


def friendly_filename(name):
    name = friendly_dirname(name)
    return re.sub("[\\\/]", '', name)


def friendly_dirname(name):
    # .gsub(/[^\w\s_-]+/, '')
    # .gsub(/\s+/, '_')
    # pipeline:
    name = re.sub("[\x00-\x1f]", '', name)
    name = re.sub("[\:\<\>\"\|\?\*]", '', name)
    name = re.sub("(^|\b\s)\s+($|\s?\b)", '\\1\\2', name)
    return name.strip()


def get_assignment_name(driver: WebDriver, block):
    s = friendly_filename(get_text_excluding_children(driver, block))
    print("Assesment: " + s)
    return s


def save_html(dir, filename, driver: WebDriver, page_log_file=False):
    if page_log_file:
        with open(URL_LIST, "a", encoding="utf-8") as f:
            f.write(driver.current_url + "\n")
    dir = pathlib.Path(friendly_dirname(dir))
    dir.mkdir(parents=True, exist_ok=True)
    file = dir.joinpath(friendly_filename(filename) + ".html")
    with open(file, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

# NOTE: Switching to a "download" tab causes issues so we must use the in built
# download in Chrome, which does not have etag or metadata information.
# Files are using annotate-au.foundations.blackboard.com and not bbcswebdav system
# so the tag may not exist in the first place.


def download_file(dest):
    d = Path(DL_DIR)
    time.sleep(10)   # sorry for blocking!
    downloading = True
    poll = 1.0
    while downloading:
        for f in os.listdir(d):
            if Path(f).suffix == '.crdownload':
                time.sleep(poll)
                poll *= 1.5
                break
            else:
                _dest = Path(dest).joinpath("MARKED__" + f)
                try:
                    shutil.move(str(d.joinpath(f)), _dest)
                except shutil.SameFileError:
                    os.remove(_dest)
                    shutil.move(str(d.joinpath(f)), _dest)

        if len(os.listdir(d)) == 0:
            downloading = False


# https://stackoverflow.com/a/19040341
def get_text_excluding_children(driver, element):
    return driver.execute_script("""
    return jQuery(arguments[0]).contents().filter(function() {
        return this.nodeType == Node.TEXT_NODE;
    }).text();
    """, element)
