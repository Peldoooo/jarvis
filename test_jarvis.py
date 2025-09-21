#!/usr/bin/env python3
"""
JARVIS Quick Test Script
Run basic functionality tests without GUI
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.jarvis_core import JarvisCore
from utils.logger import setup_logger
from config.config import config

def test_components():
    """Test JARVIS components"""
    print("🤖 JARVIS Component Testing")
    print("=" * 40)
    
    logger = setup_logger(level='INFO')
    
    try:
        # Test configuration
        print("✅ Configuration loaded")
        print(f"   Language: {config.get('languages.default')}")
        print(f"   Voice engine: {config.get('voice.engine')}")
        
        # Test core initialization
        print("🧠 Initializing JARVIS core...")
        jarvis = JarvisCore()
        print("✅ JARVIS core initialized")
        
        # Test AI client
        if jarvis.ai_client:
            print("🤖 Testing AI connection...")
            if jarvis.ai_client.test_connection():
                print("✅ AI client connected")
            else:
                print("❌ AI client connection failed")
        else:
            print("⚠️  AI client not configured (missing API key)")
        
        # Test speech engine
        print("🗣️  Testing speech engine...")
        jarvis.speech_engine.speak("JARVIS system test successful")
        print("✅ Speech engine working")
        
        # Test camera
        print("📹 Testing camera...")
        if jarvis.camera_manager.start_camera():
            print("✅ Camera started")
            jarvis.camera_manager.stop_camera()
            print("✅ Camera stopped")
        else:
            print("❌ Camera failed to start")
        
        # Test system controller
        print("🖥️  Testing system controller...")
        system_info = jarvis.system_controller.get_system_info()
        print(f"✅ System info retrieved: {system_info.get('platform', 'Unknown')}")
        
        print("\n🎉 All tests completed!")
        
        # Shutdown
        jarvis.shutdown()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False
    
    return True

def interactive_test():
    """Interactive test mode"""
    print("\n🎯 Interactive Test Mode")
    print("Type 'quit' to exit")
    
    try:
        jarvis = JarvisCore()
        
        while True:
            command = input("\nEnter command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            
            if not command:
                continue
            
            # Process command
            jarvis.command_queue.put({
                'text': command,
                'language': jarvis.current_language,
                'timestamp': None
            })
            
            # Wait a bit for processing
            import time
            time.sleep(2)
        
        jarvis.shutdown()
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main test function"""
    print("🚀 JARVIS Assistant Test Suite")
    print("==============================")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_test()
    else:
        success = test_components()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
