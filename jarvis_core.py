"""
JARVIS Core Module
Main system coordination and AI processing
"""

import threading
import time
from typing import Dict, Any, Callable, Optional
import queue
from datetime import datetime

from config.config import config
from ai.openrouter_client import OpenRouterClient
from voice.speech_engine import SpeechEngine
from voice.recognition_engine import RecognitionEngine
from camera.camera_manager import CameraManager
from automation.system_control import SystemController
from utils.logger import get_logger

class JarvisCore:
    """Core JARVIS system that coordinates all components"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Component initialization
        self.ai_client = None
        self.speech_engine = None
        self.recognition_engine = None
        self.camera_manager = None
        self.system_controller = None
        
        # System state
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False
        self.wake_word_detected = False
        
        # Communication queues
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Event callbacks
        self.callbacks = {
            'on_wake_word': [],
            'on_command': [],
            'on_response': [],
            'on_error': [],
            'on_status_change': []
        }
        
        # Current conversation context
        self.conversation_history = []
        self.current_language = config.get('languages.default', 'pt-BR')
        
        self.initialize_components()
        self.start_background_threads()
    
    def initialize_components(self):
        """Initialize all JARVIS components"""
        try:
            # Initialize AI client
            if config.get('openrouter.api_key'):
                self.ai_client = OpenRouterClient()
                self.logger.info("OpenRouter AI client initialized")
            else:
                self.logger.warning("OpenRouter API key not found")
            
            # Initialize speech engine
            self.speech_engine = SpeechEngine()
            self.logger.info("Speech engine initialized")
            
            # Initialize recognition engine
            self.recognition_engine = RecognitionEngine()
            self.logger.info("Speech recognition initialized")
            
            # Initialize camera
            self.camera_manager = CameraManager()
            self.logger.info("Camera manager initialized")
            
            # Initialize system controller
            self.system_controller = SystemController()
            self.logger.info("System controller initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise
    
    def start_background_threads(self):
        """Start background processing threads"""
        # Command processing thread
        self.command_thread = threading.Thread(
            target=self._command_processor,
            daemon=True
        )
        self.command_thread.start()
        
        # Voice activation thread
        if config.get('features.voice_activation'):
            self.voice_activation_thread = threading.Thread(
                target=self._voice_activation_listener,
                daemon=True
            )
            self.voice_activation_thread.start()
    
    def _voice_activation_listener(self):
        """Background thread for wake word detection"""
        wake_word = config.get('features.wake_word', 'jarvis').lower()
        
        while True:
            try:
                if not self.is_speaking and not self.is_processing:
                    audio_text = self.recognition_engine.listen_for_wake_word()
                    
                    if audio_text and wake_word in audio_text.lower():
                        self.wake_word_detected = True
                        self._trigger_callback('on_wake_word', audio_text)
                        self.start_listening()
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in voice activation: {e}")
                time.sleep(1)
    
    def _command_processor(self):
        """Background thread for processing commands"""
        while True:
            try:
                command_data = self.command_queue.get(timeout=1)
                self._process_command(command_data)
                self.command_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
    
    def _process_command(self, command_data: Dict[str, Any]):
        """Process a voice command"""
        try:
            self.is_processing = True
            self._trigger_callback('on_status_change', 'processing')
            
            command_text = command_data.get('text', '')
            language = command_data.get('language', self.current_language)
            
            self.logger.info(f"Processing command: {command_text}")
            
            # Add to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': command_text,
                'timestamp': datetime.now(),
                'language': language
            })
            
            # Check for system commands first
            system_response = self._handle_system_commands(command_text)
            
            if system_response:
                response = system_response
            else:
                # Process with AI
                response = self._process_with_ai(command_text, language)
            
            # Add response to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now(),
                'language': language
            })
            
            # Speak the response
            self.speak(response, language)
            
            # Trigger callbacks
            self._trigger_callback('on_command', command_data)
            self._trigger_callback('on_response', {
                'text': response,
                'language': language
            })
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            error_msg = "Desculpe, ocorreu um erro ao processar seu comando."
            self.speak(error_msg)
            self._trigger_callback('on_error', str(e))
        
        finally:
            self.is_processing = False
            self._trigger_callback('on_status_change', 'idle')
    
    def _handle_system_commands(self, command: str) -> Optional[str]:
        """Handle system-level commands"""
        command_lower = command.lower()
        
        # Camera commands
        if any(word in command_lower for word in ['câmera', 'camera', 'foto', 'picture']):
            if 'ligar' in command_lower or 'ativar' in command_lower or 'turn on' in command_lower:
                self.camera_manager.start_camera()
                return "Câmera ativada com sucesso."
            elif 'desligar' in command_lower or 'desativar' in command_lower or 'turn off' in command_lower:
                self.camera_manager.stop_camera()
                return "Câmera desativada."
            elif 'foto' in command_lower or 'picture' in command_lower or 'capturar' in command_lower:
                filename = self.camera_manager.take_photo()
                return f"Foto capturada e salva como {filename}."
        
        # Volume commands
        if any(word in command_lower for word in ['volume', 'som']):
            if 'aumentar' in command_lower or 'increase' in command_lower or 'up' in command_lower:
                self.system_controller.increase_volume()
                return "Volume aumentado."
            elif 'diminuir' in command_lower or 'decrease' in command_lower or 'down' in command_lower:
                self.system_controller.decrease_volume()
                return "Volume diminuído."
            elif 'mudo' in command_lower or 'mute' in command_lower:
                self.system_controller.mute_volume()
                return "Som silenciado."
        
        # Language change
        if 'idioma' in command_lower or 'language' in command_lower:
            if 'inglês' in command_lower or 'english' in command_lower:
                self.current_language = 'en-US'
                return "Language changed to English."
            elif 'português' in command_lower or 'portuguese' in command_lower:
                self.current_language = 'pt-BR'
                return "Idioma alterado para português."
            elif 'espanhol' in command_lower or 'spanish' in command_lower:
                self.current_language = 'es-ES'
                return "Idioma cambiado a español."
        
        return None
    
    def _process_with_ai(self, text: str, language: str) -> str:
        """Process command with AI"""
        if not self.ai_client:
            return "Sistema de IA não configurado. Verifique sua chave de API."
        
        try:
            # Prepare context
            context = self._build_context(language)
            messages = context + [{'role': 'user', 'content': text}]
            
            # Get AI response
            response = self.ai_client.chat_completion(messages, language)
            return response
            
        except Exception as e:
            self.logger.error(f"AI processing error: {e}")
            return "Desculpe, não consegui processar sua solicitação no momento."
    
    def _build_context(self, language: str) -> list:
        """Build conversation context for AI"""
        # System prompt based on language
        system_prompts = {
            'pt-BR': {
                'role': 'system',
                'content': 'Você é JARVIS, um assistente virtual inteligente. Seja útil, conciso e amigável. Responda sempre em português brasileiro.'
            },
            'en-US': {
                'role': 'system',
                'content': 'You are JARVIS, an intelligent virtual assistant. Be helpful, concise and friendly. Always respond in English.'
            },
            'es-ES': {
                'role': 'system',
                'content': 'Eres JARVIS, un asistente virtual inteligente. Sé útil, conciso y amigable. Responde siempre en español.'
            }
        }
        
        context = [system_prompts.get(language, system_prompts['pt-BR'])]
        
        # Add recent conversation history
        recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
        
        for msg in recent_history:
            context.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        return context
    
    def start_listening(self):
        """Start listening for voice commands"""
        if self.is_listening or self.is_speaking:
            return
        
        self.is_listening = True
        self._trigger_callback('on_status_change', 'listening')
        
        # Start listening in a separate thread
        listening_thread = threading.Thread(
            target=self._listen_for_command,
            daemon=True
        )
        listening_thread.start()
    
    def _listen_for_command(self):
        """Listen for voice command"""
        try:
            command_text = self.recognition_engine.listen_for_command()
            
            if command_text:
                self.command_queue.put({
                    'text': command_text,
                    'language': self.current_language,
                    'timestamp': datetime.now()
                })
        
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
        
        finally:
            self.is_listening = False
            self._trigger_callback('on_status_change', 'idle')
    
    def speak(self, text: str, language: str = None):
        """Speak text using voice synthesis"""
        if not text:
            return
        
        language = language or self.current_language
        
        self.is_speaking = True
        self._trigger_callback('on_status_change', 'speaking')
        
        try:
            self.speech_engine.speak(text, language)
        except Exception as e:
            self.logger.error(f"Error speaking: {e}")
        finally:
            self.is_speaking = False
            self._trigger_callback('on_status_change', 'idle')
    
    def add_callback(self, event: str, callback: Callable):
        """Add event callback"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, data: Any = None):
        """Trigger event callbacks"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Callback error for {event}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'is_processing': self.is_processing,
            'current_language': self.current_language,
            'ai_available': self.ai_client is not None,
            'camera_active': self.camera_manager.is_active() if self.camera_manager else False,
            'conversation_length': len(self.conversation_history)
        }
    
    def shutdown(self):
        """Shutdown JARVIS system"""
        self.logger.info("Shutting down JARVIS...")
        
        try:
            if self.camera_manager:
                self.camera_manager.stop_camera()
            
            if self.speech_engine:
                self.speech_engine.stop()
            
            if self.recognition_engine:
                self.recognition_engine.stop()
                
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
