from IPython.display import Audio, display
from pydub import AudioSegment
import tempfile
import yt_dlp


class AudioHandler:
    """Downloads YouTube audio and plays audio segments in notebook."""
    def __init__(self, video_id: str, ffmpeg_path: str = '/opt/homebrew/bin'):
        self.video_id = video_id
        self.ffmpeg_path = ffmpeg_path
        self.audio_filename = f'{video_id}.mp3'

    def download_audio(self) -> None:
        ydl_opts = {
            'format': 'bestaudio/best',
            'ffmpeg_location': self.ffmpeg_path,
            'outtmpl': f'{self.video_id}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        url = f'https://www.youtube.com/watch?v={self.video_id}'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def play_segment(self, start_sec: float, end_sec: float) -> None:
        audio = AudioSegment.from_file(self.audio_filename)
        start_ms = int(start_sec * 1000)
        end_ms = int(end_sec * 1000)
        clip = audio[start_ms:end_ms]

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmpfile:
            clip.export(tmpfile.name, format="mp3")
            display(Audio(filename=tmpfile.name))