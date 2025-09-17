import asyncio
import aiohttp
from helper.googleTranslate import translate
from helper.cefrAnalyzer import CEFRWordAnalyzer
from helper.transcriptFetcher import TranscriptYtFetcher
from helper.configHelper import load_config
from helper.writeToMongo import MongoClient
from multiprocessing import Pool
from helper.dictionaryApiClient import DictionaryApiClient
from helper.processTranscript import TranscriptProcessor
from helper.googleTranslate import translate

config = load_config('config.yaml')

async def enrich_word(word, doc, session, dictionary_client, config):
    # Run dictionary fetch and translation concurrently for the same word/doc
    await asyncio.gather(
        dictionary_client.get_from_dictionary(session, doc, word),
        translate(doc, word, config.translation.min_translate_level, config.translation.target_language)
    )

async def main():

    transcript_fetcher = TranscriptYtFetcher(config.video.video_id)

    cefr_analyzer = CEFRWordAnalyzer(min_level=config.cefr.min_level, max_level=config.cefr.max_level)
    
    yt_transcript = transcript_fetcher.fetch()

    transcript_processor = TranscriptProcessor(cefr_analyzer, yt_transcript, config.video.video_id)
    
    result_docs = transcript_processor.process_transcript()

    dictionary_client = DictionaryApiClient(config)

    async with aiohttp.ClientSession() as session:
        tasks = [
            enrich_word(word, doc, session, dictionary_client, config)
            for word, doc in result_docs.items()
        ]
        await asyncio.gather(*tasks)
    mongo_client = MongoClient(config.mongodb)
    await mongo_client.insert_many(list(result_docs.values()))

if __name__ == '__main__':
    asyncio.run(main())
    