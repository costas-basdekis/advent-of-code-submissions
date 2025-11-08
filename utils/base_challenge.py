from abc import ABC
from http.server import HTTPServer
from pathlib import Path
from typing import Dict, List, NoReturn, Tuple

import aox.challenge

import utils
from utils.serve_handler import ChallengeServeHandler


__all__ = ['BaseChallenge']


class BaseChallenge(aox.challenge.BaseChallenge, ABC):
    def get_test_modules(self):
        return super().get_test_modules() + utils.test_modules

    def serve(self, root: Path, prefix: str = "/", index_suffix: str = "index.html", address: Tuple[str, int] = ('', 8000)) -> NoReturn:
        httpd = HTTPServer(server_address=address, RequestHandlerClass=ChallengeServeHandler(prefix=prefix, root=root, index_suffix=index_suffix, translate_path=self.serve_translate_path))
        httpd.serve_forever()

    def serve_translate_path(self, original_path: str, path: str, query: Dict[str, List[str]], fragment: str) -> str:
        return path
