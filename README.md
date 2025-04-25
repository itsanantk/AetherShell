# ⚡ AetherShell

> AI-Powered PowerShell Assistant — crafted for seamless system navigation, automation, and interaction.

---

## 📌 Description

AetherShell is an intelligent terminal assistant built to interact with your Windows system through PowerShell commands and AI. It dynamically analyzes user requests, refines system queries, and executes PowerShell commands while learning from context — all while prioritizing safety and flexibility.

---

## 🚀 Features

- ✅ Natural language to PowerShell conversion
- 🔁 Feedback loop: auto-corrects failed commands or asks for clarification
- 🔐 Detects and warns about dangerous system commands
- 🧠 Context memory chaining for better understanding

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
   python main.py
   ```

---

## 🧪 Example Commands You Can Say

- "Show me files modified in the last 2 days"
- "Open my Downloads folder"
- "Find the largest 3 images on my Desktop"
- "Open Spotify"
  
- ![image](https://github.com/user-attachments/assets/2e38898c-b3ed-40f4-95f3-b3babc3deed1)
- An example use of this program which helped me setup a shortcut script for this AetherShell


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

