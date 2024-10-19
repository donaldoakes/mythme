import os
import json
from typing import Optional
from dotenv import load_dotenv
from mythme.model.query import Criterion, SavedQuery
from mythme.utils.config import config
from mythme.utils.log import logger

load_dotenv()


class QueryData:
    def __init__(self):
        self.queries_file = f"{config.mythme_dir}/queries.json"
        if not os.path.isfile(self.queries_file):
            logger.info(f"Creating queries file: {os.path.abspath(self.queries_file)}")
            self.write([])

    def read(self) -> list[SavedQuery]:
        with open(self.queries_file, "r") as f:
            queries: list[SavedQuery] = []
            for k, v in json.load(f).items():
                queries.append(SavedQuery(name=k, criteria=v))
            queries.sort(key=lambda q: q.name)
            return queries

    def write(self, queries: list[SavedQuery]):
        obj: dict[str, list[dict]] = {}
        for query in queries:
            criteria: list[Criterion] = query.criteria
            obj[query.name] = [c.__dict__ for c in criteria]

        with open(self.queries_file, "w") as f:
            json.dump(obj, f, indent=2)

    def get_queries(self) -> list[SavedQuery]:
        return self.read()

    def get_query(self, name: str) -> Optional[SavedQuery]:
        qs = filter(lambda q: q.name == name, self.read())
        return next(qs, None)

    def save_query(self, query: SavedQuery):
        queries = self.get_queries()
        for q in queries:
            if q.name == query.name:
                q.criteria = query.criteria
                self.write(queries)
                return
        queries.append(query)
        self.write(queries)

    def delete_query(self, name: str):
        idx = -1
        queries = self.get_queries()
        for i, q in enumerate(queries):
            if q.name == name:
                idx = i
                break
        if idx >= 0:
            queries.pop(idx)
            self.write(queries)
