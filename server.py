#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import pymorphy2
import re


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_response_morphy(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def analyze_sentense(self, sentence):
        morph = pymorphy2.MorphAnalyzer()
        if sentence == '':
            result = {'status': 'error', 'message': 'Пустая строка!'}
            return result
        # match = re.search('[^а-яА-Я0-9ёЁ ]', sentence)
        match = re.search('[a-zA-Z]', sentence)
        if match:
            result = {'status': 'error', 'message': 'Поддерживается только кириллица'}
            return result
        splitted = sentence.split()
        num_words = 0
        target_word = ''
        if splitted[0].isnumeric():
            target_word = splitted[1]
            num_words = len(splitted) - 1
        else:
            target_word = splitted[0]
            num_words = len(splitted)
        normal_form = morph.parse(target_word)[0]
        lexeme = normal_form.lexeme
        declined_word = []
        for lex in lexeme:
            if lex.word not in declined_word:
                declined_word.append(lex.word)
        result = {'status': 'ok', 'declined_word': declined_word, 'num_words': num_words}
        return result

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) 
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data)
        if 'sentence' in body:
            result = self.analyze_sentense(body['sentence'])
            logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                         str(self.path), str(self.headers), post_data.decode('utf-8'))
            self._set_response_morphy()
            self.wfile.write(bytes(json.dumps(result, ensure_ascii=False), 'utf-8'))
            return
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
