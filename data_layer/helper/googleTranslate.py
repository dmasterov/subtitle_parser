from googletrans import Translator
from typing import Dict
from typing import Optional

async def translate(doc: Dict, word: str, min_translate_level: float, dest_lang: str = 'ru'):
    if doc['cefr_level'] >= min_translate_level + 1:
        async with Translator() as translator:
            result = await translator.translate(word, dest=dest_lang)
            doc['translation'] = result.text