import re
import json
import os

class PhoneticEngine:
    def __init__(self, dictionary_path=None):
        self.schemes = {
            "avro": self._load_avro_scheme(),
            "probhat": self._load_probhat_scheme()
        }
        self.dictionary = set()
        self.custom_mappings = {}
        self.ngram_model = {}
        if dictionary_path and os.path.exists(dictionary_path):
            self.load_dictionary(dictionary_path)
    
    def _load_avro_scheme(self):
        # Basic Avro phonetic patterns
        return [
            ("bhl", "ভ্ল"), ("psh", "পশ"), ("bdh", "ব্ধ"), ("bj", "ব্জ"), ("bd", "ব্দ"),
            ("bb", "ব্ব"), ("bl", "ব্ল"), ("bh", "ভ"), ("vl", "ভ্ল"), ("b", "ব"), ("v", "ভ"),
            ("kkhN", "ক্ষ্ণ"), ("kShN", "ক্ষ্ণ"), ("kkhm", "ক্ষ্ম"), ("kShm", "ক্ষ্ম"),
            ("kxN", "ক্ষ্ণ"), ("kxm", "ক্ষ্ম"), ("kkh", "ক্ষ"), ("kSh", "ক্ষ"),
            ("ksh", "কশ"), ("kx", "ক্ষ"), ("kk", "ক্ক"), ("kT", "ক্ট"), ("kt", "ক্ত"),
            ("ks", "ক্স"), ("kh", "খ"), ("k", "ক"), ("gh", "ঘ"), ("g", "গ"), ("a", "আ"), ("i", "ই"),
            ("u", "উ"), ("e", "এ"), ("o", "ও"), ("m", "ম"), ("r", "র")
        ]

    def _load_probhat_scheme(self):
        return [
            ("k", "ক"), ("kh", "খ"), ("g", "গ"), ("gh", "ঘ"), ("a", "আ"), ("i", "ই"),
            ("u", "উ"), ("e", "এ"), ("o", "ও"), ("m", "ম"), ("r", "র")
        ]

    def set_custom_mapping(self, roman, bengali):
        self.custom_mappings[roman] = bengali

    def parse(self, text, scheme="avro"):
        if not text: return ""
        # Apply custom mappings first (exact match)
        if text in self.custom_mappings:
            return self.custom_mappings[text]
        
        rules = self.schemes.get(scheme, self.schemes["avro"])
        result = ""
        i = 0
        text_lower = text
        while i < len(text_lower):
            matched = False
            for pattern, replacement in rules:
                if text_lower.startswith(pattern, i):
                    result += replacement
                    i += len(pattern)
                    matched = True
                    break
            if not matched:
                result += text[i]
                i += 1
        return result

    def load_dictionary(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    self.dictionary.add(word)

    def add_to_dictionary(self, word):
        self.dictionary.add(word)

    def spellcheck(self, word):
        if not self.dictionary:
            return True # No dictionary loaded, assume correct
        return word in self.dictionary

    def suggest_corrections(self, word):
        if not self.dictionary:
            return []
        import difflib
        return difflib.get_close_matches(word, self.dictionary, n=3, cutoff=0.6)

    def predict_next_word(self, context, current_prefix=""):
        if not current_prefix:
            return []
        predictions = [w for w in self.dictionary if w.startswith(current_prefix)]
        return predictions[:5]

class STTEngine:
    def __init__(self):
        self.is_offline_capable = True
    
    def transcribe_audio(self, audio_data):
        # Mock offline STT
        return "অফলাইন ট্রান্সক্রিপশন সফল"
