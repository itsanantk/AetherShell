import subprocess
import getpass
import os
from openai import OpenAI
import sys

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_response(response):
    response = response.strip()
    if response.startswith("```"):
        response = response.replace("```powershell", "").replace("```", "")
    if response.startswith("`") and response.endswith("`"):
        response = response[1:-1]
    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1]
    return response.strip()

def ask_chatgpt(prompt, context="", clarification=None, model="gpt-4o"):
    user_name = getpass.getuser()

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a Windows PowerShell terminal assistant. "
                f"The user's Windows username is {user_name}. "
                "Only respond with PowerShell commands unless you need clarification. "
                "NEVER guess if you're unsure — instead, ask the user a concise follow-up question. "
                "If a previous command failed or gave no output, you must suggest a better one or ask a clarifying question. "
                "Don't explain anything unless asking for clarification. "
                "If a command fails (timeout, invalid syntax), improve it or ask a clarification."
                "When asking clarifying questions, be concise and avoid repetition."
                "Once you are confident your command will work, respond only with that command and nothing else. "
                "You can always respond with: A question if clarification is needed, DONE if you're confident, A single-line PowerShell command otherwise"
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
            "content": f"The last command gave this output:\n{context[:1500]}\n"
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
    print(f"\n⚙️ Suggested Command:\n{cmd}\n")
    if is_dangerous(cmd):
        print("This command has a high level of risk!")
        confirm = input("Run it anyway? [y/N] ")
        if confirm.strip().lower() != "y":
            return "[User canceled dangerous command]"

    try:
        print("Running command...\n")
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode != 0 or result.stderr:
            return f"[ERROR] {result.stderr.strip()}"
        return result.stdout.strip() or "[Command ran successfully, but produced no output]"
    except subprocess.TimeoutExpired:
        return "[ERROR] Command timed out. It may be stuck or invalid.]"

def feedback_loop(initial_request, max_rounds=5):
    prompt = initial_request
    last_output = ""
    clarification = None
    previous_questions = set()

    for round_num in range(max_rounds):
        print(f"\n ROUND {round_num + 1}: Asking Aether...\n")
        ai_response = clean_response(ask_chatgpt(prompt, context=last_output, clarification=clarification))

        if "?" in ai_response and not ai_response.lower().startswith("get-"):
            if ai_response in previous_questions:
                print("🔁 Aether is repeating a question — stopping loop.")
                break
            previous_questions.add(ai_response)
            print(f" Aether needs clarification:\n{ai_response}")
            clarification = input("✍️ Your clarification: ")
            continue

        if ai_response.strip().lower() == "done":
            print(" Aether believes the task is complete.")
            break

        last_output = run_powershell(ai_response)

        if "[ERROR]" in last_output or "timed out" in last_output.lower():
            print(f" Error detected:\n{last_output}")
        else:
            print(f"\n Output:\n{last_output[:1000]}")

    print("💡 Loop complete.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = input(" What would you like Aether to do?\n> ")

    feedback_loop(user_request)
