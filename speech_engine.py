"""
Speech Engine Module
Handles text-to-speech synthesis with robotic voice effects
"""

import pyttsx3
import threading
import time
from typing import Optional
import numpy as np
import io
from config.config import config
from utils.logger import get_logger

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class SpeechEngine:
    """Speech synthesis engine with robotic voice effects"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.engine_type = config.get('voice.engine', 'pyttsx3')
        self.is_speaking = False
        self.speech_lock = threading.Lock()
        
        # Initialize speech engine
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the speech engine"""
        try:
            if self.engine_type == 'pyttsx3':
                self._init_pyttsx3()
            elif self.engine_type == 'gtts' and GTTS_AVAILABLE:
                self._init_gtts()
            else:
                self.logger.warning("Falling back to pyttsx3")
                self._init_pyttsx3()
                
        except Exception as e:
            self.logger.error(f"Error initializing speech engine: {e}")
            raise
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        self.engine = pyttsx3.init()
        
        # Configure voice settings for robotic effect
        rate = config.get('voice.rate', 150)
        volume = config.get('voice.volume', 0.8)
        voice_id = config.get('voice.voice_id', 0)
        
        # Set properties
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        if voices and len(voices) > voice_id:
            self.engine.setProperty('voice', voices[voice_id].id)
        
        self.logger.info("pyttsx3 engine initialized")
    
    def _init_gtts(self):
        """Initialize gTTS engine"""
        if GTTS_AVAILABLE:
            pygame.mixer.init()
            self.logger.info("gTTS engine initialized")
        else:
            raise ImportError("gTTS not available")
    
    def speak(self, text: str, language: str = None):
        """Speak text with robotic voice effects"""
        if not text:
            return
        
        with self.speech_lock:
            if self.is_speaking:
                return
            
            self.is_speaking = True
        
        try:
            # Apply robotic text preprocessing
            processed_text = self._apply_robotic_effects(text)
            
            if self.engine_type == 'pyttsx3':
                self._speak_pyttsx3(processed_text)
            elif self.engine_type == 'gtts' and GTTS_AVAILABLE:
                self._speak_gtts(processed_text, language)
            
        except Exception as e:
            self.logger.error(f"Error speaking: {e}")
        
        finally:
            self.is_speaking = False
    
    def _apply_robotic_effects(self, text: str) -> str:
        """Apply robotic speech effects to text"""
        # Add pauses for robotic effect
        robotic_text = text.replace('.', '... ')
        robotic_text = robotic_text.replace(',', ',. ')
        robotic_text = robotic_text.replace('!', '... ')
        robotic_text = robotic_text.replace('?', '... ')
        
        # Add emphasis on certain words
        emphasis_words = ['jarvis', 'sistema', 'ativado', 'processando', 'comando']
        for word in emphasis_words:
            if word in robotic_text.lower():
                robotic_text = robotic_text.replace(
                    word, f"<emphasis level='strong'>{word}</emphasis>"
                )
        
        return robotic_text
    
    def _speak_pyttsx3(self, text: str):
        """Speak using pyttsx3"""
        try:
            # Apply robotic voice settings
            original_rate = self.engine.getProperty('rate')
            
            # Slightly slower for robotic effect
            self.engine.setProperty('rate', original_rate * 0.8)
            
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Restore original rate
            self.engine.setProperty('rate', original_rate)
            
        except Exception as e:
            self.logger.error(f"Error with pyttsx3 speech: {e}")
    
    def _speak_gtts(self, text: str, language: str = None):
        """Speak using gTTS"""
        if not GTTS_AVAILABLE:
            return
        
        try:
            # Convert language code
            lang_map = {
                'pt-BR': 'pt',
                'en-US': 'en',
                'es-ES': 'es',
                'fr-FR': 'fr',
                'de-DE': 'de'
            }
            
            lang = lang_map.get(language, 'pt')
            
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=True)  # slow=True for robotic effect
            
            # Save to memory buffer
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            # Play audio
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error with gTTS speech: {e}")
    
    def stop(self):
        """Stop current speech"""
        try:
            if self.engine_type == 'pyttsx3' and hasattr(self, 'engine'):
                self.engine.stop()
            elif self.engine_type == 'gtts' and GTTS_AVAILABLE:
                pygame.mixer.music.stop()
                
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}")
        
        finally:
            self.is_speaking = False
    
    def is_busy(self) -> bool:
        """Check if engine is currently speaking"""
        return self.is_speaking
    
    def set_rate(self, rate: int):
        """Set speech rate"""
        try:
            if self.engine_type == 'pyttsx3' and hasattr(self, 'engine'):
                self.engine.setProperty('rate', rate)
            config.set('voice.rate', rate)
            
        except Exception as e:
            self.logger.error(f"Error setting rate: {e}")
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        try:
            if self.engine_type == 'pyttsx3' and hasattr(self, 'engine'):
                self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            config.set('voice.volume', volume)
            
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
    
    def get_voices(self) -> list:
        """Get available voices"""
        try:
            if self.engine_type == 'pyttsx3' and hasattr(self, 'engine'):
                voices = self.engine.getProperty('voices')
                return [{
                    'id': voice.id,
                    'name': voice.name,
                    'age': getattr(voice, 'age', None),
                    'gender': getattr(voice, 'gender', None)
                } for voice in voices] if voices else []
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
