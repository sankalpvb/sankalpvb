# reconmaster/app/services/executor.py

import asyncio
import subprocess

# A mapping of tool names to their base command arguments
# This is a security measure to prevent arbitrary command execution.
# We will fetch the 'base_command' from the DB later, but this demonstrates the principle.
# For now, we hardcode them.
COMMAND_MAP = {
    "Nmap": ["nmap"],
    "Gobuster": ["gobuster", "dir"],
    "Sublist3r": ["sublist3r"],
    "WhatWeb": ["whatweb"]
}

# --- IMPORTANT SECURITY NOTE ---
# This is a simplified executor. A production system would need more robust
# input sanitization, user permission checks, and potentially run commands
# in isolated containers (e.g., Docker) to prevent escape vulnerabilities.

async def run_command_stream(tool_name: str, target: str, websocket):
    """
    Executes a command and streams its stdout and stderr to a WebSocket in real-time.
    """
    # 1. Validate the tool_name against our allowed commands
    if tool_name not in COMMAND_MAP:
        await websocket.send_text(f"ERROR: Tool '{tool_name}' is not a valid or allowed tool.")
        return

    # 2. Construct the command safely as a list
    #    This prevents shell injection vulnerabilities.
    #    NEVER use `shell=True` with user-provided input.
    base_cmd = COMMAND_MAP[tool_name]
    
    # Simple argument mapping for demonstration
    if tool_name == "Gobuster":
        # Gobuster needs -u for URL and -w for wordlist
        # NOTE: This assumes a wordlist path. A real app would make this configurable.
        command = base_cmd + ["-u", f"http://{target}", "-w", "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt", "-t", "20"]
    elif tool_name == "Sublist3r":
        # Sublist3r needs -d for domain
        command = base_cmd + ["-d", target]
    else:
        # For Nmap and WhatWeb, the target is the last argument
        command = base_cmd + [target]

    await websocket.send_text(f"INFO: Running command: {' '.join(command)}\n\n")

    # 3. Create the subprocess
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # 4. Stream stdout and stderr in real-time
    while True:
        # Check stdout
        stdout_line = await process.stdout.readline()
        if stdout_line:
            await websocket.send_text(stdout_line.decode().strip())
        
        # Check stderr
        stderr_line = await process.stderr.readline()
        if stderr_line:
            await websocket.send_text(f"ERROR: {stderr_line.decode().strip()}")

        # Break the loop if the process has finished and there's no more output
        if process.returncode is not None and not stdout_line and not stderr_line:
            break
        
        await asyncio.sleep(0.1) # Small sleep to prevent a busy-wait loop

    await websocket.send_text(f"\n\nINFO: Process finished with exit code {process.returncode}.")
