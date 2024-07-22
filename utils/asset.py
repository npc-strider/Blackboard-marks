from constants.constants import BASE_URL
import re
import hashlib
import requests
import shutil
import csv
from pathlib import Path


def convert_filename(name, hash):
    _name = name.split('.')
    if len(_name) > 1:
        _name[-2] += ("[" + hash + "]")
    else:
        _name[0] += ("[" + hash + "]")
    return '.'.join(_name)


class RequestStack:
    def __init__(self, token):
        self.request_stack = []
        self.token = token
        super().__init__()

    def add_file(self, url, path):
        self.request_stack.append(Asset(url, path))

    def download_all(self):
        for file in self.request_stack:
            print(f"\tDownloading {file.url}")
            file.download(self.token)


class Asset:
    def __init__(self, url, path):
        self.path = Path(path)
        self.url = re.sub("^" + BASE_URL, "", url)
        # self.file_id = re.findall('file_id=(.+)&',url)
        self.path.mkdir(parents=True, exist_ok=True)
        super().__init__()

    def download(self, session):
        response = session.get(
            BASE_URL + self.url, stream=True, allow_redirects=False)
        headers = response.headers
        if response.status_code == 302 and len(headers['location']) > 0:
            Asset(headers['location'], self.path).download(session)
            return
        elif response.status_code != 200:
            print("[!] Error " + str(response.status_code))
            return response.status_code
        headers = {x: re.sub(r'^"*|"*?$', '', headers.get(x))
                   for x in headers}  # ewww regex
        if 'Content-Disposition' in headers.keys():
            self.original_filename = re.findall(
                'filename="(.+)"', headers['Content-Disposition'])[0]
        else:
            self.original_filename = re.sub(".*/", "", self.url)
        self.etag_hash = hashlib.md5(headers['ETag'].encode()).hexdigest()
        self.filename = convert_filename(
            self.original_filename, self.etag_hash[0:6])

        with open(self.path.joinpath(self.filename), 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        self.write_metadata(headers)

    def write_metadata(self, headers):
        metacsv = [
            ["original_filename", self.original_filename or "error"],
            ["readable_filename", self.filename or "error"],
            ["url", self.url or "error"],
            ["pathhash", hashlib.md5(
                self.url.encode()).hexdigest() or "error"],
            ["etag", headers['ETag'] or "error"],
            ["etaghash", self.etag_hash or "error"],
            ["last-modified", headers["Last-Modified"] or "error"],
            ["content-length", headers["Content-Length"] or "error"],
            ["age", ""],
        ]
        csvpath = self.path.joinpath("ZZZ_metadata")
        csvpath.mkdir(parents=True, exist_ok=True)
        with open(csvpath.joinpath(self.filename + "__metadata.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(metacsv)
