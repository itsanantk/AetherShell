import getpass
import subprocess
import ollama

def clean_response(response):
    response = response.strip()
    # Remove backticks and optional 'powershell' label
    response = response.strip()
    if response.startswith("```"):
        response = response.replace("```powershell", "").replace("```", "")
    if response.startswith("`") and response.endswith("`"):
        response = response[1:-1]
    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1]
    return response.strip()

def ask_ollama(prompt, context="", model="mistral"):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a " + os + " PowerShell terminal assistant. Respond only with PowerShell commands. "
                "Assume the user is running Windows. Do not explain anything. "
                "Your task is to help the user complete the original goal"
                "If the output from the previous command indicates it didn't work or returned nothing, "
                "you must modify the command and try again — but stay on topic. "
                "Only generate new commands if necessary. Do not hallucinate tasks unrelated to file system exploration."
                "Do not format your response as Markdown."
                "The user's username on their current device is " + str(user_name)
            )
        },

        {
            "role": "user",
            "content": "The users original prompt is " + prompt
        }
    ]

    if context:
        messages.append({
            "role": "user",
            "content": f"The last command was run and produced this output:\n\n{context}\n\n"
                       "If it looks correct, return 'DONE'. If it failed or returned nothing, return a new improved PowerShell command."
        })

    response = ollama.chat(model=model, messages=messages)
    return response['message']['content'].strip()

def is_dangerous(cmd):
    dangerous_keywords = [
        "rm", "shutdown", "reboot", "kill", "mkfs", "dd", ":(){", "yes >", "curl |", "wget |", "chmod +x", "mv /", "cp /"
    ]
    for keyword in dangerous_keywords:
        if keyword in cmd:
            return True
    return False

def run_powershell(cmd):
    print(f"About to run: {cmd}")
    """if is_dangerous(cmd):
        print("This command has a high level of risk!")
        confirm = input("Run this? [Y/N] ")

        if confirm.lower() == 'n':
            return "This command posses a high level of risk"""

    try:
        print("Running...")
        output = subprocess.check_output(["powershell", "-Command", cmd], stderr=subprocess.STDOUT)
        return output.decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8', errors='ignore')

def feedback_loop(initial_request, max_rounds=5):
    prompt = initial_request
    last_output = ""
    for round_num in range(max_rounds):
        print(f"\n🧠 ROUND {round_num + 1}: Asking AI...\n")
        ai_response = clean_response(ask_ollama(prompt, context=last_output))

        if ai_response.strip().lower() == "done":
            print("✅ AI believes the task is complete.")
            break

        print(f"⚙️ Suggested command:\n{ai_response}\n")
        print(f"🖥️ Running:\n{ai_response}\n")

        last_output = run_powershell(ai_response)
        if not last_output.strip():
            print("⚠️ The command returned no output.")
        else:
            print(f"\n📄 Output (truncated):\n{last_output[:1000]}")

    print("💡 Loop complete.")

# Example usage
if __name__ == "__main__":
    user_name = str(getpass.getuser())
    os = "Windows"
    user_request = input("What would you like the AI to do?\n> ")
    feedback_loop(user_request)
