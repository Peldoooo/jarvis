#!/bin/bash

# JARVIS Assistant Installation Script
# This script installs all dependencies for JARVIS

echo "🤖 Installing JARVIS Assistant Dependencies..."
echo "================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$python_version" ]]; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv jarvis_env
source jarvis_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install system dependencies
echo "🔧 Installing system dependencies..."

# Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "Detected Ubuntu/Debian system"
    sudo apt-get update
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        portaudio19-dev \
        espeak \
        espeak-data \
        libespeak1 \
        libespeak-dev \
        ffmpeg \
        libasound2-dev \
        libgtk-3-dev \
        libcairo2-dev \
        libgirepository1.0-dev
        
# macOS
elif command -v brew &> /dev/null; then
    echo "Detected macOS system"
    brew install portaudio
    brew install espeak
    brew install ffmpeg
    
# Fedora/CentOS/RHEL
elif command -v dnf &> /dev/null; then
    echo "Detected Fedora/CentOS/RHEL system"
    sudo dnf install -y \
        python3-devel \
        portaudio-devel \
        espeak \
        espeak-devel \
        ffmpeg \
        alsa-lib-devel \
        gtk3-devel \
        cairo-devel \
        gobject-introspection-devel
        
else
    echo "⚠️  Unknown system. Please install portaudio, espeak, and ffmpeg manually."
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output/photos
mkdir -p output/videos
mkdir -p output/screenshots
mkdir -p logs
mkdir -p config
mkdir -p assets

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📄 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenRouter API key!"
fi

# Create desktop entry (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🖥️  Creating desktop entry..."
    
    desktop_entry="[Desktop Entry]
Version=1.0
Type=Application
Name=JARVIS Assistant
Comment=AI Virtual Assistant
Exec=$PWD/jarvis_env/bin/python $PWD/main.py
Icon=$PWD/assets/jarvis_icon.png
Terminal=false
Categories=Utility;AudioVideo;Development;"
    
    echo "$desktop_entry" > ~/.local/share/applications/jarvis-assistant.desktop
    chmod +x ~/.local/share/applications/jarvis-assistant.desktop
fi

echo ""
echo "🎉 Installation complete!"
echo "================================================"
echo "Next steps:"
echo "1. Edit .env file and add your OpenRouter API key"
echo "2. Activate virtual environment: source jarvis_env/bin/activate"
echo "3. Run JARVIS: python main.py"
echo ""
echo "For more information, see README.md"
