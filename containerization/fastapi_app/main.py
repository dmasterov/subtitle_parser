from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all origins but less secure
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient("mongodb://root:example@mongo:27017")
db = client.video_transcripts
collection = db.transcripts

class Sentence(BaseModel):
    id: str
    word: str
    sentence_with_gap: str

def make_gap(sentence: str, word: str) -> str:
    return sentence.replace(word, word[0] + "_" * (len(word) - 1), 1)

@app.get("/sentence/{word}", response_model=Sentence)
async def get_sentence(word: str):
    doc = await collection.find_one({"word": word})
    if doc:
        return Sentence(
            id=str(doc["_id"]),
            word=doc["word"],
            sentence_with_gap=make_gap(doc["context"][0], word)
        )
    return {"error": "Word not found"}
