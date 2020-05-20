import os
import random
import string
from http import cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

database = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            link = urlparse(self.path)
            shorten = link.path[1:]
            long = ''

            cookie = cookies.SimpleCookie(self.headers["Cookie"])

            if cookie and shorten in cookie:
                long = cookie[shorten].value
            else:
                if shorten in database:
                    long = database[shorten]
                else:
                    self.send_error(404, 'not found')

                # self.send_response(200)
                self.send_response(301)
                self.send_header('Content-type', 'text-html')
                name = shorten
                cookie = cookies.SimpleCookie()
                cookie[name] = database[shorten]
                cookie[name]['path'] = name
                cookie[name]['domain'] = "http://localhost:8080"

                self.send_header("Set-Cookie", cookie.output(header='', sep=''))
                # self.end_headers()

            if not long.startswith("http://"):
                long = "http://" + long
                long = long.replace('///', '//')

            # self.send_response(301)
            self.send_header('Location', long)
            self.end_headers()

        except IOError:
            print(database)
            self.send_error(404, 'not found')


class UrlShortener:
    key = ''

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.file_reader()
        self.shorten_url()
        self.file_writer()

    def generator(self, length=7):
        letters = string.ascii_letters + '0123456789'
        return ''.join(random.choice(letters) for i in range(length))

    def shorten_url(self):
        print(database)
        if self.url not in database.values():
            self.key = self.generator()
            database[self.key] = self.url

        else:
            for k in database.keys():
                if database[k] == self.url:
                    self.key = k
                    return k

    def file_reader(self):
        if os.path.exists('database.txt'):
            with open('database.txt', 'r') as database_file:
                data = database_file.read().split('\n')
                for d in data:
                    d = d.split(',')
                    database[d[0]] = d[1]

    def file_writer(self):
        lines = ''
        with open('database.txt', 'w') as database_file:
            for _url in database.keys():
                lines += f'{_url},{database[_url]}\n'
            database_file.write(lines[:-1] if lines[-1:] == '\n' else lines)

    def __repr__(self):
        return 'http://localhost:8080/' + self.key


if __name__ == '__main__':
    PORT = 8080

    with HTTPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f'.:.:.:.:. Serving on {"0.0.0.0"}:{PORT} .:.:.:.:.')
        long_url = input('Enter a URL: ')
        short_url = UrlShortener(long_url)
        print(f'Your short URL --> {short_url} (copy it in browser)')

        httpd.serve_forever()
