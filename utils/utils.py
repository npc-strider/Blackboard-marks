import pathlib
import re

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

# https://stackoverflow.com/a/19040341
def get_text_excluding_children(driver, element):
    return driver.execute_script("""
    return jQuery(arguments[0]).contents().filter(function() {
        return this.nodeType == Node.TEXT_NODE;
    }).text();
    """, element)