import requests


class Downloader:

    def __init__(self):
        self.req = None
        self.download_dir = "dl"

    @staticmethod
    def get_current_dir():
        pass

    def set_download_dir(self, path):
        self.download_dir = path

    def send_request(self, url):
        self.req = requests.get(url)
        print(self.req.status_code)
        print(self.req.headers['content-type'])
        print(self.req.encoding)

    def download_file(self, url):
        self.send_request(url)
        with open('/Users/scott/Downloads/cat3.jpg', 'wb') as f:
            f.write(self.req.content)
