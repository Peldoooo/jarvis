"""
System Controller Module
Handles system automation and control
"""

import os
import sys
import subprocess
import psutil
import pyautogui
import webbrowser
from typing import Dict, Any, List, Optional
import platform
import time

from config.config import config
from utils.logger import get_logger

class SystemController:
    """System automation and control operations"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.system = platform.system().lower()
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        self.logger.info(f"System controller initialized for {self.system}")
    
    # Volume Control
    def increase_volume(self, step: int = 10) -> bool:
        """Increase system volume"""
        try:
            if self.system == 'windows':
                # Windows volume control
                for _ in range(step // 2):
                    pyautogui.press('volumeup')
            elif self.system == 'darwin':  # macOS
                subprocess.run(['osascript', '-e', f'set volume output volume (output volume of (get volume settings) + {step})'])
            elif self.system == 'linux':
                subprocess.run(['amixer', 'set', 'Master', f'{step}%+'])
            
            self.logger.info(f"Volume increased by {step}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error increasing volume: {e}")
            return False
    
    def decrease_volume(self, step: int = 10) -> bool:
        """Decrease system volume"""
        try:
            if self.system == 'windows':
                for _ in range(step // 2):
                    pyautogui.press('volumedown')
            elif self.system == 'darwin':
                subprocess.run(['osascript', '-e', f'set volume output volume (output volume of (get volume settings) - {step})'])
            elif self.system == 'linux':
                subprocess.run(['amixer', 'set', 'Master', f'{step}%-'])
            
            self.logger.info(f"Volume decreased by {step}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error decreasing volume: {e}")
            return False
    
    def mute_volume(self) -> bool:
        """Mute/unmute system volume"""
        try:
            if self.system == 'windows':
                pyautogui.press('volumemute')
            elif self.system == 'darwin':
                subprocess.run(['osascript', '-e', 'set volume with output muted'])
            elif self.system == 'linux':
                subprocess.run(['amixer', 'set', 'Master', 'toggle'])
            
            self.logger.info("Volume muted/unmuted")
            return True
            
        except Exception as e:
            self.logger.error(f"Error muting volume: {e}")
            return False
    
    def set_volume(self, level: int) -> bool:
        """Set volume to specific level (0-100)"""
        try:
            level = max(0, min(100, level))
            
            if self.system == 'windows':
                # Windows doesn't have direct volume setting via pyautogui
                # We'll use a more complex approach
                import pycaw.pycaw as pycaw
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                volume.SetMasterScalarVolume(level / 100, None)
                
            elif self.system == 'darwin':
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'])
            elif self.system == 'linux':
                subprocess.run(['amixer', 'set', 'Master', f'{level}%'])
            
            self.logger.info(f"Volume set to {level}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            return False
    
    # Application Control
    def open_application(self, app_name: str) -> bool:
        """Open an application"""
        try:
            if self.system == 'windows':
                subprocess.Popen(['start', app_name], shell=True)
            elif self.system == 'darwin':
                subprocess.Popen(['open', '-a', app_name])
            elif self.system == 'linux':
                subprocess.Popen([app_name])
            
            self.logger.info(f"Opened application: {app_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening application {app_name}: {e}")
            return False
    
    def close_application(self, app_name: str) -> bool:
        """Close an application"""
        try:
            # Find and terminate process
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    self.logger.info(f"Closed application: {app_name}")
                    return True
            
            self.logger.warning(f"Application not found: {app_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error closing application {app_name}: {e}")
            return False
    
    def get_running_applications(self) -> List[Dict[str, Any]]:
        """Get list of running applications"""
        try:
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    apps.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory': proc.info['memory_info'].rss if proc.info['memory_info'] else 0,
                        'cpu': proc.info['cpu_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return sorted(apps, key=lambda x: x['memory'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting running applications: {e}")
            return []
    
    # Web Browser Control
    def open_website(self, url: str) -> bool:
        """Open website in default browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            self.logger.info(f"Opened website: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening website {url}: {e}")
            return False
    
    def search_web(self, query: str, engine: str = 'google') -> bool:
        """Search the web"""
        try:
            search_urls = {
                'google': 'https://www.google.com/search?q=',
                'bing': 'https://www.bing.com/search?q=',
                'duckduckgo': 'https://duckduckgo.com/?q=',
                'youtube': 'https://www.youtube.com/results?search_query='
            }
            
            base_url = search_urls.get(engine, search_urls['google'])
            search_url = base_url + query.replace(' ', '+')
            
            return self.open_website(search_url)
            
        except Exception as e:
            self.logger.error(f"Error searching web: {e}")
            return False
    
    # System Information
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': cpu_percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_used': memory.used,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_free': disk.free,
                'disk_percent': (disk.used / disk.total) * 100,
                'boot_time': psutil.boot_time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    # Power Management
    def shutdown_system(self, delay: int = 0) -> bool:
        """Shutdown the system"""
        try:
            if self.system == 'windows':
                subprocess.run(['shutdown', '/s', f'/t', str(delay)])
            elif self.system == 'darwin':
                subprocess.run(['sudo', 'shutdown', '-h', f'+{delay//60}'])
            elif self.system == 'linux':
                subprocess.run(['sudo', 'shutdown', '-h', f'+{delay//60}'])
            
            self.logger.info(f"System shutdown initiated with {delay}s delay")
            return True
            
        except Exception as e:
            self.logger.error(f"Error shutting down system: {e}")
            return False
    
    def restart_system(self, delay: int = 0) -> bool:
        """Restart the system"""
        try:
            if self.system == 'windows':
                subprocess.run(['shutdown', '/r', f'/t', str(delay)])
            elif self.system == 'darwin':
                subprocess.run(['sudo', 'shutdown', '-r', f'+{delay//60}'])
            elif self.system == 'linux':
                subprocess.run(['sudo', 'shutdown', '-r', f'+{delay//60}'])
            
            self.logger.info(f"System restart initiated with {delay}s delay")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restarting system: {e}")
            return False
    
    def sleep_system(self) -> bool:
        """Put system to sleep"""
        try:
            if self.system == 'windows':
                subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
            elif self.system == 'darwin':
                subprocess.run(['pmset', 'sleepnow'])
            elif self.system == 'linux':
                subprocess.run(['systemctl', 'suspend'])
            
            self.logger.info("System sleep initiated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error putting system to sleep: {e}")
            return False
    
    # Mouse and Keyboard Control
    def move_mouse(self, x: int, y: int) -> bool:
        """Move mouse to coordinates"""
        try:
            pyautogui.moveTo(x, y)
            return True
        except Exception as e:
            self.logger.error(f"Error moving mouse: {e}")
            return False
    
    def click_mouse(self, x: int = None, y: int = None, button: str = 'left') -> bool:
        """Click mouse at coordinates"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
            else:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking mouse: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """Type text"""
        try:
            pyautogui.typewrite(text)
            return True
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press keyboard key"""
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key {key}: {e}")
            return False
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take screenshot"""
        try:
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output/screenshots/screenshot_{timestamp}.png"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            raise
