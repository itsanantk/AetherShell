import getpass
import multiprocessing as mp
from itertools import chain
import subprocess

import ollama
import requests
import json
import os
from multiprocessing import Pool
import time

from pyexpat.errors import messages

# Set up the base URL for the local Ollama API
url = "http://localhost:11434/api/chat"

"""
def list_dirs(path, max_files = 50):
    dirs = []

    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            dirs.append(f)

    return dirs


def list_files(path, max_files = 50):
    files = []

    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            files.append(f)

    return files
"""


def list_dirs(path):
    dirs = []

    for entry in os.scandir(path):
        if entry.is_dir():
            dirs.append(entry.path)

    return dirs


def list_files(path):
    files = []

    for entry in os.scandir(path):
        if entry.is_file():
            files.append(entry)

    return files


def scan_folder(folder):
    try:
        path = os.path.join(base, folder)
        files = list_files(path)
        return files
    except Exception as e:
        return (folder, [f"Error: {str(e)}"])


def create_context(file_list):
    return "Here are the files on the system:\n" + "\n".join(file_list)


def build_prompt(user_input):
    return f"""
    You are a" + os + "terminal assistant.
    Respond ONLY with the most appropriate" + os + "command.
    You can assume the system is" + os + "and you have permission to list,
    find, and read files. Do not explain anything. Just return the command.

    Request: {user_input}
    """


def is_dangerous(cmd):
    dangerous_keywords = [
        "rm", "shutdown", "reboot", "kill", "mkfs", "dd", ":(){", "yes >", "curl |", "wget |", "chmod +x", "mv /",
        "cp /"
    ]
    for keyword in dangerous_keywords:
        if keyword in cmd:
            return True
    return False


def run_command(cmd):
    print(f"About to run: {cmd}")
    if is_dangerous(cmd):
        print("This command has a high level of risk!")

    confirm = input("Run this? [y/N] ")
    if confirm.lower() == 'y':
        try:
            output = subprocess.check_output(['cmd.exe', '/c', cmd], stderr=subprocess.STDOUT)
            return output.decode()
        except subprocess.CalledProcessError as e:
            return e.output.decode()


base = "C:/"
os.chdir(base)

user_input = input()
# prompt = build_prompt(user_input)
prompt = user_input
os = "Windows"
user = str(getpass.getuser())

# Sample prompt
# prompt = "Show me my desktop folders"

print("Asking Ollama:", prompt)
stream = ollama.chat(
    model='mistral',
    messages=[{"role": "system",
               "content": "You are a" + os + "terminal assistant. Respond ONLY with the most appropriate" + os + "command.  You can assume the system is" + os + "and you have permission to list, find, and read files. The user's username is" + user + " in their device. Do not explain anything. Just return the command. If there is any information you dont know and need to run a command, then run whatever initial commands are needed to retrieve enough information to complete the users request."},
              {'role': 'user', 'content': prompt}],
    stream=True,
)

print("Streaming response from Ollama:", flush=True)

response_text = ""
for chunk in stream:
    content = chunk['message']['content']
    print(content, end='', flush=True)
    response_text += content  # accumulate into final string
print('\n')

print("over")
# If it’s quoted like a Python string: 'explorer "C:\..."'
if response_text.startswith("`") and response_text.endswith("`"):
    cmd = response_text[1:-1]  # remove outer single quotes
else:
    cmd = response_text
# Then run:
output = run_command(cmd)
print(output)
