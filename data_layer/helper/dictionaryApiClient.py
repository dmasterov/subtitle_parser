import asyncio
import aiohttp
from typing import List, Dict, Optional
from helper.googleTranslate import translate


class DictionaryApiClient:
    def __init__(self, config):
        # Manage concurrency with a single semaphore shared among instances (best if singleton)
        self.MAX_CONCURRENT_REQUESTS = config.dictionary_api.max_concurrent_requests
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self.API_URL = 'https://api.dictionaryapi.dev/api/v2/entries/en/'
        self.DEFAULT_RETRIES = config.dictionary_api.max_retries
        self.RETRY_BACKOFF_BASE = config.dictionary_api.retry_backoff_base
        self.min_translate_level = config.translation.min_translate_level


    @staticmethod
    def _clean_dict(d: Dict) -> Dict:
        return {k: v for k, v in d.items() if v not in ['', [], None]}

    async def _fetch_data(self, session: aiohttp.ClientSession, word: str) -> Optional[List[Dict]]:
        retries = self.DEFAULT_RETRIES
        for attempt in range(retries):
            async with self.semaphore:  # Limit concurrency
                async with session.get(self.API_URL + word) as response:
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", "1"))
                        sleep_time = max(retry_after, self.RETRY_BACKOFF_BASE * (2 ** attempt))
                        print(f"Rate limited on '{word}'. Sleeping {sleep_time} seconds. Attempt {attempt + 1}/{retries}")
                        await asyncio.sleep(sleep_time)
                        continue
                    elif response.status == 404:
                        print(f"Word '{word}' not found (404).")
                        return None
                    elif response.status != 200:
                        print(f"HTTP error {response.status} for word '{word}'. Aborting after {attempt + 1} attempts.")
                        return None
                    data = await response.json()
                    if isinstance(data, dict) and data.get("error"):
                        return None
                    return data
        print(f"Failed to fetch word '{word}' after {retries} retries.")
        return None

    async def get_from_dictionary(self, session: aiohttp.ClientSession, item: Dict, word: str) -> Optional[List[Dict]]:
        
        data = await self._fetch_data(session, word)
        if not data:
            print(f"No data found for word: {word}")
            return None

        word_entries = []

        for entry in data:
            entry_info = {
                "phonetics": [],
                "meanings": []
            }
            for ph in entry.get("phonetics", []):
                
                ph_dict = self._clean_dict({"text": ph.get("text", "")})
                entry_info["phonetics"].append(ph_dict)
                # audio link
                audio_url = ph.get("audio", None)
                if audio_url:
                    entry_info["audio"] = audio_url

            for meaning in entry.get("meanings", []):
                meaning_info = {
                    "partOfSpeech": meaning.get("partOfSpeech", ""),
                    "definitions": []
                }
                for definition in meaning.get("definitions", []):
                    definition_info = self._clean_dict({
                        "definition": definition.get("definition", ""),
                        "example": definition.get("example", ""),
                        "synonyms": definition.get("synonyms", []),
                        "antonyms": definition.get("antonyms", [])
                    })
                    meaning_info["definitions"].append(definition_info)
                entry_info["meanings"].append(meaning_info)
            word_entries.append(entry_info)
        item['dictionary'] = word_entries