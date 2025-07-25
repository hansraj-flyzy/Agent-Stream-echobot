# 🤖 Voice Bot Echo Server for Exotel

A **simple, reliable WebSocket echo server** specifically designed for testing Exotel's voice streaming functionality. Perfect for validating bidirectional audio streams and understanding the Exotel voice streaming protocol.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![WebSockets](https://img.shields.io/badge/websockets-v12.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

## ✨ What This Does

🎯 **Echo Audio Packets**: Receives audio from Exotel and echoes it back, perfect for testing bidirectional voice streaming

🔍 **Protocol Testing**: Handles all Exotel WebSocket events (`connected`, `start`, `media`, `dtmf`, `stop`, `mark`, `clear`)

📊 **Comprehensive Logging**: Detailed logs with timestamps for debugging and monitoring

⚡ **Production Ready**: Robust error handling, connection management, and graceful shutdowns

🚀 **Easy Setup**: One-command installation and startup

## 🏃‍♂️ Quick Start (2 Minutes)

### **Prerequisites**
- Python 3.8+ 
- Port 5000 available
- Internet connection

### **Installation**

```bash
# Clone the repository
git clone https://github.com/Saurabhsharma209/voice-bot-echo-exotel.git
cd voice-bot-echo-exotel

# One-command setup
chmod +x setup.sh && ./setup.sh
```

### **Start the Server**

```bash
# Start the echo server
./start.sh
```

**That's it!** Your server is now running at `ws://localhost:5000` ✅

## 🌐 Public Access with ngrok

To test with Exotel, you need a public URL:

```bash
# Install ngrok (if not already installed)
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Make your server public
ngrok http 5000
```

Use the `wss://` URL from ngrok in your Exotel configuration.

## 🧪 Testing

Test your server with the included test client:

```bash
# Test local server
python3 test_connection.py

# Test public ngrok URL
python3 test_connection.py wss://your-ngrok-url.ngrok.io
```

## 📋 Exotel Configuration

### **For Bidirectional Streaming (Voicebot Applet)**

1. **URL**: `wss://your-ngrok-url.ngrok.io`
2. **Custom Parameters**: Optional (will be logged)
3. **Record**: Enable if you want call recordings
4. **Next Applet**: Configure your next flow step

### **For Unidirectional Streaming (Stream Applet)**

1. **Action**: Start
2. **URL**: `wss://your-ngrok-url.ngrok.io`
3. **Next Applet**: Configure your next flow step

## 🎯 What Happens During a Call

1. **Connection**: Exotel establishes WebSocket connection
2. **Connected Event**: Server logs call initiation
3. **Start Event**: Stream begins, call details logged
4. **Media Events**: Audio packets received and echoed back
5. **DTMF Events**: Key presses logged (if any)
6. **Stop Event**: Stream ends, call summary logged

## 📊 Monitoring & Logs

The server creates detailed logs in the `logs/` directory:

- **`voice_bot_echo.log`**: Main server activity
- **`calls.log`**: Individual call details in JSON format

### **Real-time Monitoring**

```bash
# Watch server logs
tail -f logs/voice_bot_echo.log

# Watch call logs
tail -f logs/calls.log

# Monitor specific events
grep "Media packet" logs/voice_bot_echo.log
```

## 📁 File Structure

```
voice-bot-echo-exotel/
├── simple_server.py       # Main echo server
├── test_connection.py     # Test client
├── requirements.txt       # Python dependencies
├── setup.sh              # Automated setup script
├── start.sh               # Server start script
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── venv/                  # Virtual environment (created by setup)
└── logs/                  # Log files (created at runtime)
    ├── voice_bot_echo.log
    └── calls.log
```

## 🔧 Advanced Usage

### **Manual Installation**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python3 simple_server.py
```

### **Custom Port**

Edit `simple_server.py` and change the port:

```python
port = 8080  # Change from 5000 to your preferred port
```

### **Environment Variables**

```bash
# Set custom log level
export LOG_LEVEL=DEBUG

# Set custom port
export PORT=8080
```

## 🛠️ Troubleshooting

### **Port Already in Use**

```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use the built-in port cleanup
./start.sh  # Automatically handles port conflicts
```

### **Connection Refused from Exotel**

1. **Check server is running**: `curl http://localhost:5000`
2. **Verify ngrok tunnel**: Visit `http://localhost:4040`
3. **Use HTTPS URL**: Exotel requires `wss://` not `ws://`
4. **Check firewall**: Ensure port 5000 is open

### **No Audio Echo**

1. **Verify bidirectional mode**: Check Exotel Voicebot applet settings
2. **Check media events**: Look for `Media packet received` in logs
3. **Audio format**: Ensure Exotel sends 16-bit PCM, 8kHz, mono

### **Dependencies Issues**

```bash
# Clean reinstall
rm -rf venv
./setup.sh
```

## 🎨 Customization

### **Add Custom Logic**

Modify `simple_server.py` to add your own audio processing:

```python
elif event_type == 'media':
    # Your custom audio processing here
    processed_audio = process_audio(data['media']['payload'])
    
    # Echo back processed audio
    echo_response = {
        'event': 'media',
        'stream_sid': data.get('stream_sid'),
        'media': {
            'chunk': data['media']['chunk'],
            'timestamp': data['media']['timestamp'],
            'payload': processed_audio
        }
    }
    await websocket.send(json.dumps(echo_response))
```

### **Add Response Templates**

Create different responses for different scenarios:

```python
# Welcome message (synthetic audio)
welcome_audio = base64.b64encode(generate_welcome_audio()).decode()

# Error message
error_audio = base64.b64encode(generate_error_audio()).decode()
```

## 🚀 Production Deployment

### **Cloud Deployment**

For production use, deploy to a cloud server:

```bash
# On your cloud server (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Clone and setup
git clone https://github.com/Saurabhsharma209/voice-bot-echo-exotel.git
cd voice-bot-echo-exotel
./setup.sh

# Run with systemd (optional)
sudo systemctl enable voice-bot-echo
sudo systemctl start voice-bot-echo
```

### **Docker Deployment**

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python3", "simple_server.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/Saurabhsharma209/voice-bot-echo-exotel/issues)
- **Exotel Documentation**: [Voice Streaming Guide](https://support.exotel.com/support/solutions/articles/3000108630)
- **WebSockets Documentation**: [Python websockets library](https://websockets.readthedocs.io/)

## 🎯 Use Cases

- **🧪 Testing**: Validate Exotel voice streaming setup
- **🔍 Debugging**: Understand audio flow and protocol
- **🎓 Learning**: Study WebSocket-based telephony integration
- **🚀 Foundation**: Starting point for building voice bots
- **🔧 Development**: Local testing before production deployment

---

**🚀 Ready to test your Exotel voice streaming? This echo server makes it simple!**

Made with ❤️ for the Exotel developer community 