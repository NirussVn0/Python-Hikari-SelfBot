# Hikari Self-Bot with Python (Archived)

> ⚠️ **[ARCHIVED]** This repository is no longer actively maintained as the project has been migrated from Python to [NestJS](https://nestjs.com/).  
> 🗃️ This codebase is kept publicly available for **reference and educational purposes only**.  
> 👉 Please refer to the new implementation if you’re looking for an up-to-date version.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type hints: mypy](https://img.shields.io/badge/type%20hints-mypy-blue.svg)](http://mypy-lang.org/)

### Author by NirussVn0

⚠️ **WARNING: This project is for educational purposes only!**  
Self-bots violate Discord's Terms of Service and can result in account termination. Use this code only for learning purposes and testing in private servers where you have permission.

## 🌐 **Available Languages**

- [English](README.md)
- [Tiếng Việt](README.vi.md)

## 🧪 **Features**

- **Requires Python 3.9 or higher:** Leverages the latest language features.
- **100% Type Hints:** Fully type-annotated codebase, validated with `mypy`.
- **Advanced Metrics & Analytics:** Gain insights into bot activity and performance.
- **Robust Error Handling:** Improved stability and easier debugging.
- **Rate Limiting:** Prevents abuse and respects Discord API limits.
- **Secure Logging:** No sensitive data is ever logged.
- **Token Validation:** Built-in validation against the Discord API.
- **Command Set:** See [COMMAND.md](COMMAND.md) for available commands.
- **Flexible Installation:** Use Poetry (recommended) or pip.

## 📦 **Installation**

### **Clone the Repository**

```bash
git clone https://github.com/NirussVn0/Hikari-SelfBot
cd Hikari-SelfBot
```

### **Using Poetry (Recommended)**

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry env use python3
poetry env activate
```

### **Using pip**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## ⚙️ **Configuration**

### **Environment Setup**

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Discord token:
   ```env
   DISCORD_SELFBOT_DISCORD_TOKEN=your_discord_user_token_here
   DISCORD_SELFBOT_ENVIRONMENT=development
   DISCORD_SELFBOT_DEBUG=true
   ```

### **Token Validation**

Validate your token before running:

```bash
# Using the built-in validator
python -m src.utils.validators <token> [password]

# Or using the CLI tool
discord-selfbot validate-token
```

⚠️ **Security Warning:** Be extremely careful with your token. Anyone with access to it can control your Discord account!

## 🚀 **Usage**

### **Basic Usage**

```bash
# Run the bot
poetry run python -m run_bot
# Or using pip
python -m run_bot

# Or using the CLI
Hikari-SelfBot
```
## 📄 **License**

* This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
* **Remember: This is for educational purposes only. Self-bots violate Discord's ToS. Use responsibly! 🐍⚡**

## 🤝 **Contribute & Contact**

* Author: NirussVn0
* Discord suport: [hikariisan.vn](https://discord.gg/5Naa9X9W7f)
* Email: [niruss.dev](mailto:work.niruss.dev@gmail.com)
