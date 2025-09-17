"""Automated vocabulary generator based on developmental psychology."""

import json
from typing import List, Dict, Any
from pathlib import Path

from ..models.development import VocabularyBand, DevelopmentalStage


class VocabularyGenerator:
    """Generates vocabulary constraints based on developmental psychology."""
    
    def __init__(self):
        # Realistic developmental vocabulary based on psychological research
        # Early years: fewer, broader increments (slower learning)
        # Later years: more frequent, smaller increments (accelerating learning)
        self.developmental_vocabulary = {
            # Year 1 - Only 2 periods (0-6 months, 6-12 months)
            # Very slow vocabulary development, mostly pre-linguistic
            "1.1": {  # 0-6 months: Pre-linguistic stage
                "max_tokens": 1000,
                "stage": DevelopmentalStage.SENSORIMOTOR,
                "cognitive_focus": "sensory_integration",
                "language_characteristics": ["cooing", "babbling", "sound recognition", "gesture communication"],
                "forbidden_patterns": ["words", "sentences", "complex sounds", "abstract concepts"],
                "core_vocabulary": ["mama", "dada", "uh-oh", "bye-bye", "hi", "no"]
            },
            "1.2": {  # 6-12 months: First words and intentional communication
                "max_tokens": 2000,
                "stage": DevelopmentalStage.SENSORIMOTOR,
                "cognitive_focus": "intentional_communication",
                "language_characteristics": ["first words", "gesture combinations", "object naming", "simple requests"],
                "forbidden_patterns": ["complex sentences", "future tense", "abstract concepts", "pronouns"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck"]
            },
            
            # Year 2 - Only 2 periods (12-18 months, 18-24 months)
            # Language explosion begins, but still broad increments
            "2.1": {  # 12-18 months: Vocabulary explosion begins
                "max_tokens": 3000,
                "stage": DevelopmentalStage.SENSORIMOTOR,
                "cognitive_focus": "object_schema",
                "language_characteristics": ["50-200 words", "two-word combinations", "naming objects", "action words"],
                "forbidden_patterns": ["complex sentences", "abstract reasoning", "future planning", "pronouns"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help"]
            },
            "2.2": {  # 18-24 months: Two-word phrases and early grammar
                "max_tokens": 4000,
                "stage": DevelopmentalStage.SENSORIMOTOR,
                "cognitive_focus": "symbolic_play",
                "language_characteristics": ["200-300 words", "two-word phrases", "simple questions", "early pronouns"],
                "forbidden_patterns": ["complex sentences", "abstract reasoning", "future planning"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they"]
            },
            
            # Year 3 - 3 periods (24-30, 30-36, 36-42 months)
            # Accelerating learning, more frequent increments
            "3.1": {  # 24-30 months: Simple sentences emerge
                "max_tokens": 5000,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "self_awareness",
                "language_characteristics": ["300-600 words", "simple sentences", "basic questions", "pronouns"],
                "forbidden_patterns": ["complex reasoning", "abstract concepts", "hypothetical thinking"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty"]
            },
            "3.2": {  # 30-36 months: Complex sentences and reasoning
                "max_tokens": 6000,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "basic_reasoning",
                "language_characteristics": ["600-1000 words", "complex sentences", "basic reasoning", "cause-effect"],
                "forbidden_patterns": ["abstract reasoning", "complex hypotheticals", "metacognitive reflection"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes"]
            },
            "3.3": {  # 36-42 months: Advanced reasoning and planning
                "max_tokens": 7000,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "advanced_reasoning",
                "language_characteristics": ["1000-1500 words", "complex sentences", "advanced reasoning", "planning"],
                "forbidden_patterns": ["abstract reasoning", "complex hypotheticals", "metacognitive reflection"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                    "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes",
                                  "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                                  "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate"]
            },
            
            # Year 4 - 4 periods (42-45, 45-48, 48-51, 51-54 months)
            # Even more frequent increments as learning accelerates
            "4.1": {  # 42-45 months: World understanding expands
                "max_tokens": 8000,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "world_model",
                "language_characteristics": ["1500-2000 words", "complex sentences", "basic reasoning", "social concepts"],
                "forbidden_patterns": ["abstract reasoning", "complex hypotheticals", "metacognitive reflection"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes",
                                  "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                                  "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate",
                                  "think", "feel", "remember", "imagine", "wonder", "guess",
                                  "believe", "know", "understand", "learn", "teach"]
            },
            "4.2": {  # 45-48 months: Advanced reasoning and planning
                "max_tokens": 8500,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "advanced_reasoning",
                "language_characteristics": ["2000-2500 words", "complex sentences", "advanced reasoning", "planning"],
                "forbidden_patterns": ["abstract reasoning", "complex hypotheticals", "metacognitive reflection"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes",
                                  "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                                  "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate",
                                  "think", "feel", "remember", "imagine", "wonder", "guess",
                                  "believe", "know", "understand", "learn", "teach",
                                  "curious", "bored", "interested", "nervous", "excited"]
            },
            "4.3": {  # 48-51 months: Abstract concepts emerge
                "max_tokens": 9000,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "abstract_thinking",
                "language_characteristics": ["2500-3000 words", "complex sentences", "abstract concepts", "metacognition"],
                "forbidden_patterns": ["adult-level abstraction", "complex logical reasoning", "philosophical concepts"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes",
                                  "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                                  "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate",
                                  "think", "feel", "remember", "imagine", "wonder", "guess",
                                  "believe", "know", "understand", "learn", "teach",
                                  "curious", "bored", "interested", "nervous", "excited",
                                  "metacognitive", "consciousness", "awareness", "reflection"]
            },
            "4.4": {  # 51-54 months: Advanced metacognition
                "max_tokens": 9500,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "metacognitive_awareness",
                "language_characteristics": ["3000-3500 words", "complex sentences", "metacognitive awareness", "self-reflection"],
                "forbidden_patterns": ["adult-level abstraction", "complex logical reasoning", "philosophical concepts"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes",
                                  "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                                  "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate",
                                  "think", "feel", "remember", "imagine", "wonder", "guess",
                                  "believe", "know", "understand", "learn", "teach",
                                  "curious", "bored", "interested", "nervous", "excited",
                                  "metacognitive", "consciousness", "awareness", "reflection",
                                  "mind", "thought", "feeling", "emotion", "experience", "memory"]
            },
            
            # Year 5 - 6 periods (54-56, 56-58, 58-60 months)
            # Most frequent increments as learning reaches peak acceleration
            "5.1": {  # 54-56 months: Advanced abstract thinking
                "max_tokens": 10000,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "advanced_abstract_thinking",
                "language_characteristics": ["3500-4000 words", "complex sentences", "advanced abstract concepts", "metacognition"],
                "forbidden_patterns": ["adult-level abstraction", "complex logical reasoning", "philosophical concepts"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                    "because", "if", "then", "maybe", "probably", "sometimes",
                    "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                    "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate",
                                  "think", "feel", "remember", "imagine", "wonder", "guess",
                                  "believe", "know", "understand", "learn", "teach",
                                  "curious", "bored", "interested", "nervous", "excited",
                                  "metacognitive", "consciousness", "awareness", "reflection",
                                  "mind", "thought", "feeling", "emotion", "experience", "memory",
                                  "dream", "wish", "hope", "fear", "brave", "strong", "smart"]
            },
            "5.2": {  # 56-58 months: Peak metacognitive awareness
                "max_tokens": 10500,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "peak_metacognition",
                "language_characteristics": ["4000-4500 words", "complex sentences", "peak metacognitive awareness", "self-reflection"],
                "forbidden_patterns": ["adult-level abstraction", "complex logical reasoning", "philosophical concepts"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes",
                                  "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                                  "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate",
                    "think", "feel", "remember", "imagine", "wonder", "guess",
                    "believe", "know", "understand", "learn", "teach",
                                  "curious", "bored", "interested", "nervous", "excited",
                                  "metacognitive", "consciousness", "awareness", "reflection",
                                  "mind", "thought", "feeling", "emotion", "experience", "memory",
                                  "dream", "wish", "hope", "fear", "brave", "strong", "smart",
                                  "wisdom", "knowledge", "understanding", "learning", "growth", "change"]
            },
            "5.3": {  # 58-60 months: Final developmental stage
                "max_tokens": 11000,
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "cognitive_focus": "final_development",
                "language_characteristics": ["4500+ words", "complex sentences", "advanced metacognition", "pre-school readiness"],
                "forbidden_patterns": ["adult-level abstraction", "complex logical reasoning", "philosophical concepts"],
                "core_vocabulary": ["mama", "dada", "ball", "dog", "cat", "milk", "up", "down", 
                                  "more", "all-done", "no", "yes", "bye-bye", "hi", "book", "toy",
                                  "hungry", "sleepy", "hot", "cold", "big", "small", "car", "truck",
                                  "run", "walk", "jump", "play", "eat", "drink", "sleep", "cry",
                                  "bird", "fish", "tree", "flower", "house", "door", "window",
                                  "sit", "stand", "open", "close", "give", "take", "help",
                                  "where", "what", "who", "mine", "yours", "here", "there",
                                  "I", "me", "you", "he", "she", "it", "we", "they",
                                  "want", "like", "go", "come", "see", "hear", "know", "think",
                                  "why", "how", "when", "happy", "sad", "angry", "scared",
                                  "excited", "tired", "hungry", "thirsty", "full", "empty",
                                  "fast", "slow", "good", "bad", "same", "different", "new", "old",
                                  "school", "friend", "family", "home", "work", "play", "help",
                                  "idea", "plan", "story", "game", "rule", "time", "space",
                                  "color", "number", "shape", "size", "kind", "nice", "mean",
                                  "because", "if", "then", "maybe", "probably", "sometimes",
                                  "yesterday", "today", "tomorrow", "morning", "afternoon", "night",
                    "proud", "embarrassed", "surprised", "worried", "confused",
                                  "share", "care", "love", "like", "dislike", "hate",
                                  "think", "feel", "remember", "imagine", "wonder", "guess",
                                  "believe", "know", "understand", "learn", "teach",
                                  "curious", "bored", "interested", "nervous", "excited",
                                  "metacognitive", "consciousness", "awareness", "reflection",
                                  "mind", "thought", "feeling", "emotion", "experience", "memory",
                                  "dream", "wish", "hope", "fear", "brave", "strong", "smart",
                                  "wisdom", "knowledge", "understanding", "learning", "growth", "change",
                                  "future", "past", "present", "time", "space", "universe", "world"]
            }
        }
    
    def generate_vocabulary_band(self, period: str) -> VocabularyBand:
        """Generate vocabulary constraints for a specific developmental period."""
        if period not in self.developmental_vocabulary:
            raise ValueError(f"Period {period} not supported")
        
        period_data = self.developmental_vocabulary[period]
        
        return VocabularyBand(
            year=int(period.split('.')[0]),
            max_tokens=period_data["max_tokens"],
            developmental_stage=period_data["stage"],
            cognitive_focus=period_data["cognitive_focus"],
            language_characteristics=period_data["language_characteristics"],
            forbidden_patterns=period_data["forbidden_patterns"],
            core_vocabulary=period_data["core_vocabulary"]
        )
    
    def get_core_vocabulary(self, period: str) -> List[str]:
        """Get core vocabulary for a specific developmental period."""
        if period not in self.developmental_vocabulary:
            raise ValueError(f"Period {period} not supported")
        
        return self.developmental_vocabulary[period]["core_vocabulary"]
    
    def generate_all_vocabulary_bands(self) -> Dict[str, VocabularyBand]:
        """Generate vocabulary bands for all developmental periods."""
        bands = {}
        
        for period in self.developmental_vocabulary.keys():
            bands[period] = self.generate_vocabulary_band(period)
        
        return bands
    
    def save_vocabulary_bands(self, bands: Dict[str, VocabularyBand], output_dir: Path):
        """Save vocabulary bands to JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for period, band in bands.items():
            # Create filename based on period
            if '.' in period:
                year, increment = period.split('.')
                filename = f"vocabulary_year_{year}_period_{increment}.json"
            else:
                filename = f"vocabulary_year_{period}.json"
            
            output_path = output_dir / filename
            
            with open(output_path, 'w') as f:
                json.dump(band.model_dump(mode='json'), f, indent=2)
            
            print(f"Vocabulary band for period {period} saved to {output_path}")
    
    def generate_from_scenario(self, scenario_path: Path, output_dir: Path):
        """Generate vocabulary bands from scenario file."""
        with open(scenario_path, 'r') as f:
            scenario = json.load(f)
        
        # Extract vocabulary bands from scenario
        vocabulary_bands = scenario.get("timeline", {}).get("vocabulary_bands", {})
        
        # Generate bands for all periods
        bands = self.generate_all_vocabulary_bands()
        
        # Override with scenario-specific bands if provided
        for year, max_tokens in vocabulary_bands.items():
            if int(year) in bands:
                bands[int(year)].max_tokens = max_tokens
        
        self.save_vocabulary_bands(bands, output_dir) 