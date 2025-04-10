# ⚡ AetherShell

> AI-Powered PowerShell Assistant — driven by ChatGPT and crafted for seamless system navigation, automation, and interaction.

---

## 📌 Description

AetherShell is an intelligent terminal assistant built to interact with your Windows system through PowerShell commands, guided by GPT-based AI. It dynamically analyzes user requests, refines system queries, and executes PowerShell commands while learning from context — all while prioritizing safety and flexibility.

---

## 🚀 Features

- ✅ Natural language to PowerShell conversion
- 🔁 Feedback loop: auto-corrects failed commands or asks for clarification
- 🔐 Detects and warns about dangerous system commands
- 🧠 Context memory chaining for better understanding
- 🔌 Built-in plugin/tool awareness (like finding your Desktop/Pictures path)
- 💡 Plugin-Calling Readiness for future expansion

---

## 🖥️ Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AetherShell.git
   cd AetherShell
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file or set your environment variable for OpenAI:
   ```bash
   # .env file OR directly in your shell:
   export OPENAI_API_KEY="sk-xxxx..."
   ```

4. Run the assistant:
   ```bash
   python Looping.py
   ```

---

## 🧪 Example Commands You Can Say

- "Show me files modified in the last 2 days"
- "Open my Downloads folder"
- "Find the largest 3 images on my Desktop"
- "Create an event in my calendar for April 10th at 5 PM"

---

## 🛡️ Safety

AetherShell includes checks to identify dangerous commands like:
- `rm`, `shutdown`, `format`, `kill`, etc.

You'll always be asked for confirmation before any risky command is executed.

---

## 📜 License

This project is licensed under the MIT License.  
**This project is for learning/demo purposes. Commercial use requires permission.**

---

## 🌟 Credits

Created by [Anant Khanna](https://github.com/itsanantk)  

