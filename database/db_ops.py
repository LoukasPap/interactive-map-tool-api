import os
import helpers
from database.AtlasSearchQueryBuilder import AtlasSearchQueryBuilder

from database.db import get_db  # Import the singleton db accessor
db = get_db() 

from dotenv import load_dotenv
load_dotenv()

MONGODB_NAME = os.environ.get("MONGODB_DB")
MONGODB_ATLAS_SEACH_FIELDS = ["Title","Description","Notes", "Obverse", "Reverse", "Name", "Context"]
ORIGINS: str = str(os.environ.get("ORIGINS"))


async def search_text(include_input: str | None, exclude_input: str | None, documents_limit: int | None):
    output = helpers.format_search_input(include_input, exclude_input)
    user_in_keywords, user_in_phrases, user_ex_keywords, user_ex_phrases = output
    
    builder = AtlasSearchQueryBuilder(index="KeywordSearch", paths=MONGODB_ATLAS_SEACH_FIELDS, fuzzy_max_edits=1)
    pipeline = builder.build_pipeline(
        include_keywords=user_in_keywords,
        include_phrases=user_in_phrases,
        exclude_keywords=user_ex_keywords,
        exclude_phrases=user_ex_phrases,
        limit=documents_limit
    )
    
    print(pipeline)
    results = db["Points"].aggregate(pipeline)
    
    return helpers.parse_json(results)