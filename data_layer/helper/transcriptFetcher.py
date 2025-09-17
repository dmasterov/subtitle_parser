from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Optional

class TranscriptYtFetcher:
    def __init__(self, video_id: str, languages: Optional[List[str]] = None):
        self.video_id = video_id
        self.languages = ['en']
        self.api = YouTubeTranscriptApi()

    def fetch(self):
        transcript_list = self.api.list(self.video_id)
        transcript = transcript_list.find_transcript(self.languages)
        return transcript.fetch(preserve_formatting=True)