from collections import defaultdict

class TranscriptProcessor:
    def __init__(self, cefr_analyzer, transcript, video_id):
        self.cefr_analyzer = cefr_analyzer
        self.transcript = transcript
        self.video_id = video_id

    def process_transcript(self):
        
        processed_docs = defaultdict(lambda: {"cefr_level": None, "context": [], "timeline": []})

        for i in range(1, len(self.transcript.snippets) - 1):
            prev_phrase = self.transcript.snippets[i - 1]
            phrase = self.transcript.snippets[i]
            next_phrase = self.transcript.snippets[i + 1]
            cefr_list = self.cefr_analyzer.find_cefr_level(phrase.text)

            for cerf_word in cefr_list:
                word = cerf_word['word']
                if processed_docs[word]['cefr_level'] is None:
                    processed_docs[word]['word'] = word
                    processed_docs[word]['cefr_level'] = cerf_word['cefr_level']
                    processed_docs[word]['video_id'] = self.video_id

                processed_docs[word]['context'].append(f"...{prev_phrase.text} {phrase.text} {next_phrase.text}...")
                processed_docs[word]['timeline'].append({
                    'start': phrase.start,
                    'end': prev_phrase.start + phrase.duration + next_phrase.duration
                })

        return processed_docs
