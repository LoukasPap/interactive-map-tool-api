from typing import Tuple
from bson import json_util
import json

def format_search_input(include_input: str | None, exclude_input: str | None):
    in_keywords: list = []
    in_phrases: list = []
    ex_keywords: list = []
    ex_phrases: list = []
    
    if include_input is not None:
        in_keywords, in_phrases = separate_keywords_phrases(include_input)
    
    if exclude_input is not None:
        ex_keywords, ex_phrases = separate_keywords_phrases(exclude_input)
        
    return (in_keywords, in_phrases, ex_keywords, ex_phrases)

def separate_keywords_phrases(input: str) -> Tuple[list[str], list[str]]:
    splitted_input: list = input.split(",")
    
    keywords: list = []
    phrases: list = []
    for token in splitted_input:
        if '"' in token and token.count('"') == 2:
            phrases.append(token.strip('"'))
        else:
            keywords.append(token)
     
    return keywords, phrases

# Helper to convert ObjectId to string for JSON
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def parse_json(data):
    return json.loads(json_util.dumps(data))
