# NPCL Asterisk ARI Voice Assistant - Startup Guide

## 🚀 One-Click Startup Scripts

This project includes automated startup scripts that will set up and run the complete NPCL Voice Assistant in one go.

### 📋 Quick Start

#### For Linux/macOS:
```bash
./run_project.sh
```

#### For Windows:
```cmd
run_project.bat
```

### 📦 What the Scripts Do

The startup scripts automatically handle:

1. **System Requirements Check**
   - Verify Python 3.8+ installation
   - Check for required system tools

2. **Environment Setup**
   - Create Python virtual environment
   - Activate virtual environment
   - Upgrade pip to latest version

3. **Dependencies Installation**
   - Install all required Python packages from `requirements.txt`
   - Verify successful installation

4. **Configuration Setup**
   - Create `.env` file from `.env.example` template
   - Set up required directories (`logs`, `sounds`, `recordings`, etc.)
   - Validate configuration

5. **Service Health Checks**
   - Check OpenAI API key configuration
   - Test Asterisk ARI connection (optional)
   - Validate system readiness

6. **Application Startup**
   - Set proper Python paths
   - Start the voice assistant service
   - Display service URLs and endpoints

### 🔧 Prerequisites

Before running the startup scripts, ensure you have:

#### Required:
- **Python 3.8 or higher** - [Download from python.org](https://python.org)
- **Internet connection** - For downloading dependencies
- **OpenAI API Key** - [Get from OpenAI Platform](https://platform.openai.com/api-keys)

#### Optional (for full telephony features):
- **Asterisk PBX** - For telephony integration
- **curl** - For health checks (fallback available)

### ⚙️ Configuration

#### 1. OpenAI API Key Setup
After running the script for the first time:

1. Edit the `.env` file:
   ```bash
   nano .env  # Linux/macOS
   notepad .env  # Windows
   ```

2. Replace the placeholder with your actual API key:
   ```env
   OPENAI_API_KEY=sk-proj-your_actual_api_key_here
   ```

3. Save the file and restart the application

#### 2. Asterisk Configuration (Optional)
If you want full telephony features:

1. Install and configure Asterisk PBX
2. Copy configuration files:
   ```bash
   sudo cp asterisk-config/* /etc/asterisk/
   sudo systemctl restart asterisk
   ```

3. Verify ARI is accessible:
   ```bash
   curl -u "asterisk:1234" "http://localhost:8088/ari/asterisk/info"
   ```

### 🌐 Service Endpoints

Once started, the voice assistant provides these endpoints:

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8000` | Main service information |
| `http://localhost:8000/docs` | Interactive API documentation |
| `http://localhost:8000/health` | Health check endpoint |
| `http://localhost:8000/ari/status` | ARI system status |
| `http://localhost:8000/ari/calls` | Active calls information |

### 📞 Testing the Voice Assistant

#### 1. Web Interface Test
- Open `http://localhost:8000` in your browser
- Check the service status and configuration

#### 2. API Test
- Visit `http://localhost:8000/docs` for interactive API testing
- Use the health check endpoint to verify system status

#### 3. Telephony Test (with Asterisk)
- Configure a SIP client (like Zoiper) with:
  - Username: `1000`
  - Password: `1234`
  - Server: `localhost`
- Call extension `1000` to test voice interaction

### 🛠️ Troubleshooting

#### Common Issues:

**1. Python Not Found**
```bash
# Install Python 3.8+
sudo apt-get install python3 python3-pip  # Ubuntu/Debian
brew install python3  # macOS
# Download from python.org for Windows
```

**2. Permission Denied (Linux/macOS)**
```bash
chmod +x run_project.sh
```

**3. OpenAI API Key Error**
- Verify your API key is correct in `.env`
- Check your OpenAI account has sufficient credits
- Ensure the key format starts with `sk-proj-`

**4. Asterisk Connection Failed**
```bash
# Check Asterisk status
sudo systemctl status asterisk

# Restart Asterisk
sudo systemctl restart asterisk

# Check ARI configuration
sudo asterisk -rx "ari show status"
```

**5. Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in configuration
```

### 🔄 Manual Startup (Alternative)

If you prefer manual control:

```bash
# 1. Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate.bat  # Windows

# 2. Set Python path
export PYTHONPATH="$PWD/src:$PYTHONPATH"  # Linux/macOS
set PYTHONPATH=%CD%\src;%PYTHONPATH%  # Windows

# 3. Start the application
python ari_bot.py
# OR
python start_voice_assistant.py
# OR
python src/run_realtime_server.py
```

### 📊 Monitoring and Logs

#### Log Files:
- `logs/startup.log` - Startup process logs
- `logs/application.log` - Application runtime logs
- `logs/asterisk.log` - Asterisk integration logs

#### Real-time Monitoring:
```bash
# Watch startup logs
tail -f logs/startup.log

# Watch application logs
tail -f logs/application.log

# Monitor system status
curl http://localhost:8000/health
```

### 🔒 Security Considerations

1. **API Key Protection**
   - Never commit `.env` file to version control
   - Use environment variables in production
   - Rotate API keys regularly

2. **Network Security**
   - Configure firewall rules for production
   - Use HTTPS in production environments
   - Restrict ARI access to trusted networks

3. **Access Control**
   - Configure proper authentication for production
   - Use strong passwords for Asterisk users
   - Monitor access logs regularly

### 🆘 Getting Help

If you encounter issues:

1. **Check the logs** in the `logs/` directory
2. **Verify configuration** in `.env` file
3. **Test individual components** using the health endpoints
4. **Review the documentation** in `docs/` directory
5. **Check system requirements** and dependencies

### 📝 Script Options

#### Linux/macOS Script Options:
```bash
./run_project.sh --help     # Show help message
```

#### Windows Script:
The Windows batch file runs automatically without additional options.

### 🔄 Updates and Maintenance

To update the project:

1. **Pull latest changes** (if using git):
   ```bash
   git pull origin main
   ```

2. **Update dependencies**:
   ```bash
   source .venv/bin/activate  # Activate venv
   pip install -r requirements.txt --upgrade
   ```

3. **Restart the service**:
   ```bash
   ./run_project.sh  # Linux/macOS
   run_project.bat   # Windows
   ```

---

## 🎉 Success!

If everything is working correctly, you should see:

- ✅ All system checks passing
- ✅ Dependencies installed successfully
- ✅ Configuration validated
- ✅ Service running on http://localhost:8000
- ✅ API documentation available
- ✅ Health checks responding

**Enjoy your NPCL Asterisk ARI Voice Assistant!** 🎤📞🤖