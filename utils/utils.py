import pathlib
import re
from constants.constants import DL_DIR
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from pathlib import Path
import shutil

def friendly_filename(name):
    name = friendly_dirname(name)
    return re.sub("[\\\/]",'',name)

def friendly_dirname(name):
    #.gsub(/[^\w\s_-]+/, '')
    # .gsub(/\s+/, '_')
    # pipeline:
    name = re.sub("[\x00-\x1f]",'',name)
    name = re.sub("[\:\<\>\"\|\?\*]",'',name)
    name = re.sub("(^|\b\s)\s+($|\s?\b)", '\\1\\2', name)
    return name.strip()


def get_assignment_name(driver,block):
    s = friendly_filename(get_text_excluding_children(driver,block))
    print("Assesment: "+s)
    return s

def save_html(dir,filename,page_source):
    dir = pathlib.Path(friendly_dirname(dir))
    dir.mkdir(parents=True, exist_ok=True)
    file = dir.joinpath(friendly_filename(filename)+".html")
    with open(file, "w", encoding="utf-8") as f:
        f.write(page_source)

# Why is it so hard to just get the url of a single tab...
# def get_fast_dl(driver,button):
#     windows = len(driver.window_handles)
#     return 

# Because selenium seems to fuck up the url switching to a "download" tab, 
# I have to use the inbuilt download in chrome :(. That also means no etag/metadata 
# but to be honest it's using annotate-au.foundations.blackboard.com and not bbcswebdav system 
# so the tag may not exist in the first place.
def download_file(dest):
    d = Path(DL_DIR)
    time.sleep(2)
    downloading = True
    poll = 1.0
    while downloading:
        for f in os.listdir(d):
            if Path(f).suffix == '.crdownload':
                time.sleep(poll)
                poll *= 1.5
                break
            else:
                _dest = Path(dest).joinpath("MARKED__"+f)
                try:
                    shutil.move(d.joinpath(f),_dest)
                except shutil.SameFileError:
                    os.remove(_dest)
                    shutil.move(d.joinpath(f),_dest)

        if len(os.listdir(d)) == 0:
            downloading = False


# https://stackoverflow.com/a/19040341
def get_text_excluding_children(driver, element):
    return driver.execute_script("""
    return jQuery(arguments[0]).contents().filter(function() {
        return this.nodeType == Node.TEXT_NODE;
    }).text();
    """, element)