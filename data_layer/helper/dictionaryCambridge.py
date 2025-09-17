import requests
from bs4 import BeautifulSoup


class CambridgeParser:
    """Parses Cambridge Dictionary for definitions, examples, and CEFR levels."""
    ROOT_URL = 'https://dictionary.cambridge.org/dictionary/english/'

    def __init__(self, word: str):
        self.word = word
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://dictionary.cambridge.org/"
        }

    def _extract_text(self, element):
        return element.text.strip() if element else None

    def get_entries(self):
        """
        Returns a list of entries for word with details like:
        {
          'definition': str,
          'example': str,
          'level': str (CEFR),
          'extra_explanations': [str, ...]
        }
        """
        url = self.ROOT_URL + self.word
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all entry blocks for definitions (some words have multiple senses)
        entries = soup.find_all('div', class_='pr di superentry')

        if not entries:
            entries = [soup]  # fallback to whole page

        result = []
        for entry in entries:
            # CEFR Level: often within span with class 'epp-xref' or 'cefr' inside entry
            cefr_span = entry.find('span', class_='epp-xref')
            if cefr_span is None:
                cefr_span = entry.find('span', class_='cefr')
            level = self._extract_text(cefr_span)

            # Definitions: inside div with class 'def ddef_d db'
            defs = entry.find_all('div', class_='def ddef_d db')
            definitions = [self._extract_text(d) for d in defs if self._extract_text(d)]

            # Examples: inside div with class 'examp dexamp'
            examples = entry.find_all('div', class_='examp dexamp')
            example_texts = [self._extract_text(e) for e in examples if self._extract_text(e)]

            # Extra explanations: Look for div or span with explanatory notes or complex definitions
            extras = []
            expl_blocks = entry.find_all('div', class_='explanation')
            for expl in expl_blocks:
                text = self._extract_text(expl)
                if text:
                    extras.append(text)

            result.append({
                'level': level,
                'definitions': definitions,
                'examples': example_texts,
                'extra_explanations': extras,
            })
        return result