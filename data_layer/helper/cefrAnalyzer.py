import spacy
from cefrpy import CEFRAnalyzer
from typing import List, Dict, Any

class CEFRWordAnalyzer:
    def __init__(self, min_level: float = 4.0, max_level: float = 9.0, lang_model: str = 'en_core_web_sm'):
        self.min_level = min_level
        self.max_level = max_level
        self.nlp = spacy.load(lang_model)
        self.analyzer = CEFRAnalyzer()
        self.pos_map = {'NOUN': 'NN', 'VERB': 'VB', 'ADJ': 'JJ', 'ADV': 'RB'}

    def get_word_level(self, word: str) -> float:
        doc = self.nlp(word)
        pos = doc[0].pos_
        pos_tag = self.pos_map.get(pos)
        if not pos_tag:
            return 0.0
        return self.analyzer.get_word_pos_level_float(word.lower(), pos_tag)

    def find_cefr_level(self, text: str) -> List[Dict[str, Any]]:
        doc = self.nlp(text)
        tokens = []
        for sent in doc.sents:
            for token in sent:
                level = self.get_word_level(token.text)
                if level and self.min_level <= level <= self.max_level:
                    tokens.append({'word': token.text, 'cefr_level': level})
        return tokens