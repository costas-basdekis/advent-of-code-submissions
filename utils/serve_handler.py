from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
import os
from pathlib import Path
from typing import Callable, Dict, List
from urllib.parse import parse_qs, urlparse


__all__ = ["ChallengeServeHandler", "ChallengeServeRequestHandler"]


class ChallengeServeHandler:
    root: str
    prefix: str
    index_suffix: str
    translate_path: Callable[[str, str, Dict[str, List[str]], str], str]

    def __init__(self, prefix: str, root: Path, index_suffix: str, translate_path: Callable[[str, str, str, str], str]):
        self.prefix = prefix
        self.root = str(root)
        self.index_suffix = index_suffix
        self.translate_path = translate_path

    def __call__(self, request, client_address, server, *, directory = None):
        return ChallengeServeRequestHandler(request, client_address, server, root=directory or self.root, prefix=self.prefix, index_suffix=self.index_suffix, serve_translate_path=self.translate_path)


class ChallengeServeRequestHandler(SimpleHTTPRequestHandler):
    prefix: str
    index_suffix: str
    serve_translate_path: Callable[[str, str, Dict[str, List[str]], str], str]

    def __init__(self, request, client_address, server, *, root = None, prefix = "", index_suffix = "", serve_translate_path = lambda _1, path, _2, _3: path):
        self.prefix = prefix
        self.index_suffix = index_suffix
        self.serve_translate_path = serve_translate_path
        super().__init__(request, client_address, server, directory=root)

    def do_GET(self):
        parse_result = urlparse(self.path)
        path, query_string, fragment = parse_result.path, parse_result.query, parse_result.fragment
        query = parse_qs(query_string)
        original_path = path
        if path == "/":
            path = f"{self.prefix}{self.index_suffix}"
        path = self.serve_translate_path(original_path, path, query, fragment)
        if path == "/favicon.ico" and not os.path.isdir(path):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        if not path.startswith(self.prefix):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        self.path = path
        return super().do_GET()
