import subprocess
import getpass
import os
import sys
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
STATE_FILE = Path.home() / ".aether_state.json"

def clean_response(response):
    response = response.strip()
    if response.startswith("```"):
        response = response.replace("```powershell", "").replace("```", "")
    if response.startswith("`") and response.endswith("`"):
        response = response[1:-1]
    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1]
    return response.strip()

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(prompt, clarification_needed):
    with open(STATE_FILE, "w") as f:
        json.dump({
            "prompt": prompt,
            "clarification_needed": clarification_needed
        }, f)

def clear_state():
    if STATE_FILE.exists():
        STATE_FILE.unlink()

def ask_chatgpt(prompt, context="", clarification=None, model="gpt-4o"):
    user_name = getpass.getuser()

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a Windows PowerShell terminal assistant. "
                f"The user's Windows username is {user_name}. "
                "Only respond with PowerShell commands unless you need clarification. "
                "NEVER guess. If unsure, ask a concise follow-up question. "
                "If the previous command failed or returned nothing, refine it or ask. "
                "Carefully validate paths or file/folder names that fail. Use Test-Path to check them if needed."
                "Consider exploring parent directories or prompting the user to confirm alternatives."
                "Respond ONLY with:\n"
                "- a question (if clarification is needed),\n"
                "- 'DONE' if the task is complete, or\n"
                "- a valid single-line PowerShell command."
            )
        },
        {
            "role": "user",
            "content": f"Original user request: {prompt}"
        }
    ]

    if clarification:
        messages.append({
            "role": "user",
            "content": f"User clarification: {clarification}"
        })

    if context:
        messages.append({
            "role": "user",
            "content": f"The last command gave this output:\n{context}\n"
                       "If it looks correct, return DONE. Otherwise, return a better command or ask a follow-up question."
        })

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()

def is_dangerous(cmd):
    dangerous_keywords = [
        "rm", "shutdown", "reboot", "kill", "mkfs", "dd", ":(){", "yes >", "curl |",
        "wget |", "chmod +x", "mv /", "cp /", "del", "rmdir", "format", "New-Object", "Add-Type"
    ]
    return any(keyword in cmd.lower() for keyword in dangerous_keywords)

def run_powershell(cmd, timeout=15):
    print(f"\nSuggested Command:\n{cmd}\n")
    if is_dangerous(cmd):
        if sys.stdin.isatty():
            try:
                confirm = input("This command has a high level of risk! Run it anyway? [y/N] ")
                if confirm.strip().lower() != "y":
                    return "[User canceled dangerous command]"
            except EOFError:
                print("Non-interactive terminal detected. Proceeding anyway.")
        else:
            print("This command has a high level of risk! Non-interactive terminal detected. Proceeding anyway.")

    try:
        print("Running command...\n")
        result = subprocess.run(["powershell", "-Command", cmd],
                                capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0 or result.stderr:
            return f"[ERROR] {result.stderr.strip()}"
        return result.stdout.strip() or "[Command ran successfully, but produced no output]"
    except subprocess.TimeoutExpired:
        return "[ERROR] Command timed out. It may be stuck or invalid.]"

def feedback_loop(prompt, clarification=None):
    last_output = ""
    clarification_needed = False

    for round_num in range(1, 6):
        print(f"\nROUND {round_num}: Asking Aether...\n")
        ai_response = clean_response(ask_chatgpt(prompt, context=last_output, clarification=clarification))

        if "?" in ai_response and not ai_response.lower().startswith("get-"):
            print(f"Aether needs clarification:\n{ai_response}")
            try:
                clarification = input("Your clarification: ")
                save_state(prompt, True)
                continue
            except EOFError:
                print("\nClarification required but input is not available (non-interactive terminal).")
                print("You can rerun the command like this:")
                print(f'aether --clarify "your answer here"')
                save_state(prompt, True)
                break

        if ai_response.strip().lower() == "done":
            print("Aether believes the task is complete.")
            clear_state()
            break

        last_output = run_powershell(ai_response)

        if "[ERROR]" in last_output.lower() or "timed out" in last_output.lower():
            print(f"Error detected:\n{last_output}")
        else:
            print(f"\nOutput:\n{last_output[:1000]}")

    print("Loop complete.")

if __name__ == "__main__":
    args = sys.argv[1:]

    state = load_state()
    clarification_flag = None

    if state.get("clarification_needed") and args:
        clarification_flag = " ".join(args)
        prompt = state.get("prompt", "")
    else:
        prompt = " ".join(args)

    if not prompt:
        try:
            prompt = input("What would you like Aether to do?\n> ")
        except EOFError:
            print("No input provided and terminal is non-interactive. Exiting.")
            sys.exit(1)

    feedback_loop(prompt, clarification=clarification_flag)
