import asyncio

class AsyncCache:
    def __init__(self):
        self.cache = {}
        self.lock = asyncio.Lock()

    async def update_context(self, word, word_context, doc):
        async with self.lock:
            if word in self.cache:
                self.cache[word]['context'].append(word_context['context'])
                self.cache[word]['start'].append(word_context['start'])
                self.cache[word]['end'].append(word_context['end'])
            else:
                doc['context'] = [word_context['context']]
                doc['start'] = [word_context['start']]
                doc['end'] = [word_context['end']]
                self.cache[word] = doc

    async def items(self):
        async with self.lock:
            return list(self.cache.items())
