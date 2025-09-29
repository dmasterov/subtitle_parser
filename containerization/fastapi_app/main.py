from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import random
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse


def get_nested(data, keys, default=None):
    for key in keys:
        if isinstance(data, list) and isinstance(key, int):
            if 0 <= key < len(data):
                data = data[key]
            else:
                return default
        elif isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = AsyncIOMotorClient("mongodb://root:example@mongo:27017")
    app.state.db = app.state.client["video_transcripts"]
    yield
    app.state.client.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WordItem(BaseModel):
    word: str
    definition: str
    translation: Optional[str] = None
    audio_url: Optional[str] = None
    pronounciation: Optional[str] = None


@app.get("/words", response_model=List[WordItem])
async def get_words(limit: int = 10):
    cursor = app.state.db.transcripts.find().limit(limit)
    results = []
    async for document in cursor:
        results.append(WordItem(**document))
    return results


@app.get("/exercise/fill-gap")
async def fill_gap_exercise():
    doc = await app.state.db.transcripts.aggregate([
        {"$sample": {"size": 1}}
    ]).to_list(length=1)
    if not doc:
        raise HTTPException(status_code=404, detail="No transcripts available")
    word = get_nested(doc, [0, 'word'], default="")
    indexes = random.sample(range(len(word)), k=min(2, max(1, len(word)//2)))
    masked = list(word)
    for i in indexes:
        masked[i] = "_"
    masked_word = "".join(masked)
    definition = get_nested(doc, [0, 'dictionary', 0, 'meanings', 0, 'definitions', 0, 'definition'], default="")
    context = get_nested(doc, [0, 'context', 0], default="")
    return {
        "id": str(doc[0].get("_id")),
        "original_word": word,
        "masked_word": masked_word,
        "context": context,
        "definition": definition,
        "translation": get_nested(doc, [0, 'translation'], "")
    }


@app.get("/exercise/match")
async def match_exercise():
    docs = await app.state.db.transcripts.aggregate([{"$sample": {"size": 5}}]).to_list(length=5)
    if not docs:
        raise HTTPException(status_code=404, detail="No transcripts")
    words = [d['word'] for d in docs]
    definitions = [get_nested(d, ['dictionary', 0, 'meanings', 0, 'definitions', 0, 'definition'], default="") 
                   for d in docs]
    # random.shuffle(definitions)
    return {
        "words": words,
        "definitions": definitions,
        "answers": {w: d for w, d in zip(words, definitions)}
    }


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="http://localhost:8080/index.html")