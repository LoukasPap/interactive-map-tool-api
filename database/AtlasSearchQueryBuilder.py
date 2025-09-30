from copy import deepcopy
from typing import List, Optional, Dict, Any

class AtlasSearchQueryBuilder:
    def __init__(self,
                 index: str = "KeywordSearch",
                 paths: Optional[List[str]] = None,
                 fuzzy_max_edits: int = 0,
                 phrase_slop: int = 0):
        self.index = index
        self.paths = paths or ["Title", "Description"]
        self.fuzzy_max_edits = fuzzy_max_edits
        self.phrase_slop = phrase_slop

    def _text_clause(self, query: str, path: Optional[List[str]] = None, fuzzy: Optional[int] = None) -> Dict[str, Any]:
        p = path or self.paths
        clause = {"text": {"query": query, "path": p}}
        if fuzzy is None:
            fuzzy = self.fuzzy_max_edits
        if fuzzy and isinstance(fuzzy, int) and fuzzy > 0:
            clause["text"]["fuzzy"] = {"maxEdits": int(fuzzy)}
        return clause

    def _phrase_clause(self, phrase: str, path: Optional[List[str]] = None, slop: Optional[int] = None) -> Dict[str, Any]:
        p = path or self.paths
        clause = {"phrase": {"query": phrase, "path": p}}
        if slop is None:
            slop = self.phrase_slop
        if slop and isinstance(slop, int) and slop > 0:
            clause["phrase"]["slop"] = int(slop)
        return clause

    def build_pipeline(self,
                       include_keywords: Optional[List[str]] = None,
                       include_phrases: Optional[List[str]] = None,
                       exclude_keywords: Optional[List[str]] = None,
                       exclude_phrases: Optional[List[str]] = None,
                       index: Optional[str] = None,
                       paths: Optional[List[str]] = None,
                       limit: Optional[int] = None,
                       project: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        include_keywords = include_keywords or []
        include_phrases = include_phrases or []
        exclude_keywords = exclude_keywords or []
        exclude_phrases = exclude_phrases or []

        idx = index or self.index
        paths_use = paths or self.paths

        should_clauses = []
        must_not_clauses = []

        # include keywords -> add to should
        for kw in include_keywords:
            if not kw:
                continue
            should_clauses.append(self._text_clause(kw, path=paths_use))

        # include phrases -> add to should
        for ph in include_phrases:
            if not ph:
                continue
            should_clauses.append(self._phrase_clause(ph, path=paths_use))

        # exclude keywords -> mustNot
        for kw in exclude_keywords:
            if not kw:
                continue
            must_not_clauses.append(self._text_clause(kw, path=paths_use))

        # exclude phrases -> mustNot
        for ph in exclude_phrases:
            if not ph:
                continue
            must_not_clauses.append(self._phrase_clause(ph, path=paths_use))

        compound_body: Dict[str, Any] = {}
        if should_clauses:
            compound_body["should"] = should_clauses
            compound_body["minimumShouldMatch"] = 1
        if must_not_clauses:
            compound_body["mustNot"] = must_not_clauses

        if not compound_body:
            raise ValueError("No include/exclude clauses provided; supply at least one include or exclude")

        search_stage = {
            "$search": {
                "index": idx,
                "compound": compound_body
            }
        }

        pipeline = [search_stage,
                    {"$addFields": {"score": {"$meta": "searchScore"}}},
                    # {"$sort": {"score": -1}}
                    ]

        if limit:
            pipeline.append({"$limit": int(limit)})

        return pipeline
