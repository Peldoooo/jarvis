"""
Speech Recognition Engine
Handles voice input and speech-to-text conversion
"""

import speech_recognition as sr
import threading
import time
from typing import Optional, Dict, Any
import queue
from langdetect import detect, LangDetectError

from config.config import config
from utils.logger import get_logger

class RecognitionEngine:
    """Speech recognition engine for voice input"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Configuration
        self.language = config.get('speech.language', 'pt-BR')
        self.timeout = config.get('speech.timeout', 5)
        self.phrase_timeout = config.get('speech.phrase_timeout', 1)
        self.energy_threshold = config.get('speech.energy_threshold', 300)
        
        # State
        self.is_listening = False
        self.calibrated = False
        
        self._initialize_microphone()
    
    def _initialize_microphone(self):
        """Initialize microphone"""
        try:
            # Get default microphone
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            self._calibrate_microphone()
            
            self.logger.info("Microphone initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing microphone: {e}")
            raise
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        if self.calibrated:
            return
        
        try:
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
                # Set energy threshold
                self.recognizer.energy_threshold = self.energy_threshold
                self.recognizer.dynamic_energy_threshold = True
                
                # Set timeout values
                self.recognizer.phrase_threshold = 0.3
                self.recognizer.non_speaking_duration = 0.5
                
                self.calibrated = True
                self.logger.info(f"Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}")
                
        except Exception as e:
            self.logger.error(f"Error calibrating microphone: {e}")
            raise
    
    def listen_for_wake_word(self, timeout: float = 1.0) -> Optional[str]:
        """Listen for wake word with short timeout"""
        if not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                # Quick listen for wake word
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=3
                )
            
            # Recognize speech
            return self._recognize_speech(audio, quick=True)
            
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            self.logger.debug(f"Wake word detection error: {e}")
            return None
    
    def listen_for_command(self, timeout: float = None) -> Optional[str]:
        """Listen for voice command"""
        if not self.microphone:
            return None
        
        timeout = timeout or self.timeout
        
        try:
            self.is_listening = True
            
            with self.microphone as source:
                self.logger.info("Listening for command...")
                
                # Listen for command
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10
                )
            
            # Recognize speech
            command = self._recognize_speech(audio)
            
            if command:
                self.logger.info(f"Command recognized: {command}")
                return command
            
            return None
            
        except sr.WaitTimeoutError:
            self.logger.info("Listening timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
            return None
        finally:
            self.is_listening = False
    
    def _recognize_speech(self, audio, quick: bool = False) -> Optional[str]:
        """Recognize speech from audio"""
        try:
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.language
                )
                
                if text:
                    # Detect language if not quick mode
                    if not quick:
                        detected_lang = self._detect_language(text)
                        if detected_lang:
                            self.logger.debug(f"Detected language: {detected_lang}")
                    
                    return text.lower().strip()
                    
            except sr.UnknownValueError:
                self.logger.debug("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                self.logger.warning(f"Google Speech Recognition error: {e}")
                
                # Fallback to offline recognition
                return self._offline_recognition(audio)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error recognizing speech: {e}")
            return None
    
    def _offline_recognition(self, audio) -> Optional[str]:
        """Fallback offline speech recognition"""
        try:
            # Try Sphinx (PocketSphinx) for offline recognition
            text = self.recognizer.recognize_sphinx(audio, language=self.language)
            
            if text:
                return text.lower().strip()
                
        except sr.UnknownValueError:
            self.logger.debug("Sphinx could not understand audio")
        except sr.RequestError as e:
            self.logger.warning(f"Sphinx error: {e}")
        except Exception as e:
            self.logger.debug(f"Offline recognition error: {e}")
        
        return None
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect language of recognized text"""
        try:
            detected = detect(text)
            
            # Map detected language to our language codes
            lang_map = {
                'pt': 'pt-BR',
                'en': 'en-US',
                'es': 'es-ES',
                'fr': 'fr-FR',
                'de': 'de-DE'
            }
            
            return lang_map.get(detected, detected)
            
        except LangDetectError:
            return None
        except Exception as e:
            self.logger.debug(f"Language detection error: {e}")
            return None
    
    def set_language(self, language: str):
        """Set recognition language"""
        self.language = language
        config.set('speech.language', language)
        self.logger.info(f"Recognition language set to: {language}")
    
    def set_energy_threshold(self, threshold: int):
        """Set energy threshold for voice detection"""
        self.energy_threshold = threshold
        self.recognizer.energy_threshold = threshold
        config.set('speech.energy_threshold', threshold)
        self.logger.info(f"Energy threshold set to: {threshold}")
    
    def get_microphone_list(self) -> list:
        """Get list of available microphones"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return list(enumerate(mic_list))
        except Exception as e:
            self.logger.error(f"Error getting microphone list: {e}")
            return []
    
    def set_microphone(self, device_index: int):
        """Set microphone device"""
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            self.calibrated = False
            self._calibrate_microphone()
            self.logger.info(f"Microphone set to device index: {device_index}")
            
        except Exception as e:
            self.logger.error(f"Error setting microphone: {e}")
            raise
    
    def test_microphone(self) -> bool:
        """Test microphone functionality"""
        try:
            test_text = self.listen_for_command(timeout=3)
            return test_text is not None
            
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
    
    def stop(self):
        """Stop recognition engine"""
        self.is_listening = False
        self.logger.info("Recognition engine stopped")
