# J.A.R.V.I.S - Just A Rather Very Intelligent System

![JARVIS Logo](assets/jarvis_banner.png)

Um assistente virtual avançado inspirado no JARVIS dos filmes do Homem de Ferro, com interface futurística, controle por voz, acesso à câmera e integração com IA de última geração.

## ✨ Características

### 🎯 Funcionalidades Principais
- **🗣️ Reconhecimento de Voz**: Ativação por palavra-chave "JARVIS"
- **🤖 Síntese de Voz Robótica**: Voz artificial com efeitos futurísticos
- **📹 Controle de Câmera**: Captura de fotos e vídeos em tempo real
- **🧠 IA Avançada**: Integração com OpenRouter (Claude, GPT, etc.)
- **🌍 Multilíngue**: Suporte para PT-BR, EN-US, ES-ES, FR-FR, DE-DE
- **🎮 Automação de Sistema**: Controle de volume, aplicações e mais
- **🖥️ Interface Futurística**: GUI moderna inspirada no JARVIS
- **🔍 Detecção Facial**: Reconhecimento e rastreamento (opcional)

### 🛠️ Tecnologias Utilizadas
- **Python 3.8+** - Linguagem principal
- **OpenRouter API** - Modelos de IA (Claude, GPT, etc.)
- **CustomTkinter** - Interface gráfica moderna
- **OpenCV** - Processamento de imagem e câmera
- **SpeechRecognition** - Reconhecimento de voz
- **pyttsx3/gTTS** - Síntese de voz
- **PyAutoGUI** - Automação de sistema
- **psutil** - Monitoramento de sistema

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8 ou superior
- Chave da API OpenRouter ([obtenha aqui](https://openrouter.ai/))
- Microfone e câmera (opcionais)
- Sistema operacional: Windows, macOS ou Linux

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/jarvis-assistant.git
cd jarvis-assistant
```

### 2. Instalação Automática

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
install.bat
```

### 3. Configuração da API
1. Copie o arquivo `.env.example` para `.env`
2. Edite o arquivo `.env` e adicione sua chave da API:
```env
OPENROUTER_API_KEY=sua_chave_api_aqui
```

### 4. Executar JARVIS
```bash
# Ativar ambiente virtual
source jarvis_env/bin/activate  # Linux/macOS
# ou
jarvis_env\Scripts\activate.bat  # Windows

# Executar JARVIS
python main.py
```

## 🎮 Como Usar

### Ativação por Voz
1. Diga "**JARVIS**" para ativar
2. Aguarde o sinal sonoro
3. Fale seu comando
4. JARVIS processará e responderá

### Interface Gráfica
- **Chat**: Converse por texto ou voz
- **Câmera**: Controle da câmera e captura
- **Sistema**: Monitoramento e controle do sistema
- **Logs**: Visualização de logs em tempo real
- **Configurações**: Personalização de voz, API e idioma

### Comandos de Exemplo

**Português:**
- "JARVIS, que horas são?"
- "JARVIS, tire uma foto"
- "JARVIS, aumente o volume"
- "JARVIS, abra o navegador"
- "JARVIS, qual é o clima hoje?"

**English:**
- "JARVIS, what time is it?"
- "JARVIS, take a picture"
- "JARVIS, increase volume"
- "JARVIS, open browser"
- "JARVIS, what's the weather today?"

## ⚙️ Configuração Avançada

### Configuração de Voz
```python
# No arquivo config/config.py ou via interface
"voice": {
    "engine": "pyttsx3",  # ou "gtts"
    "rate": 150,          # Velocidade da fala
    "volume": 0.8,        # Volume (0.0-1.0)
    "voice_id": 0,        # 0=masculino, 1=feminino
    "language": "pt-br"   # Idioma
}
```

### Modelos de IA Suportados
- `anthropic/claude-3-sonnet`
- `openai/gpt-4-turbo`
- `openai/gpt-3.5-turbo`
- `google/palm-2-chat-bison`
- `meta-llama/llama-2-70b-chat`

## 🛡️ Recursos de Segurança

- **Validação de Entrada**: Sanitização de comandos
- **Limite de Rate**: Proteção contra spam
- **Logs Detalhados**: Auditoria completa
- **Parada de Emergência**: Botão de stop instantâneo
- **Configuração Segura**: Variáveis de ambiente para APIs

## 🐛 Solução de Problemas

### Problemas Comuns

**Erro: "Microphone not found"**
```bash
# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

**Erro: "OpenCV not working"**
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

**Erro: "API Connection Failed"**
1. Verifique sua chave da API OpenRouter
2. Confirme conexão com internet
3. Teste com modelo diferente

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.

## 🙏 Agradecimentos

- **OpenAI/Anthropic** - Modelos de linguagem
- **OpenRouter** - API unificada para IA
- **Marvel Studios** - Inspiração do JARVIS
- **Comunidade Open Source** - Bibliotecas incríveis

---

**"Sometimes you gotta run before you can walk." - Tony Stark**

🤖 **JARVIS** - Seu assistente virtual do futuro, hoje!
