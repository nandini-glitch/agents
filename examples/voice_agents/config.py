import os
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class InterruptionConfig:
    ignored_words: List[str] = None
    confidence_threshold: float = 0.6
    debug_mode: bool = False
    
    def __post_init__(self):
        if self.ignored_words is None:
            self.ignored_words = ['uh', 'um', 'umm', 'hmm', 'haan', 'mhm', 'aha', 'uhh', 'err', 'ah']
    
    @classmethod
    def from_env(cls):
        ignored = os.getenv('IGNORED_WORDS', '').split(',')
        ignored = [w.strip().lower() for w in ignored if w.strip()]
        return cls(
            ignored_words=ignored if ignored else None,
            confidence_threshold=float(os.getenv('CONFIDENCE_THRESHOLD', '0.6')),
            debug_mode=os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        )
