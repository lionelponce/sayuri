#!/usr/bin/env python3

from sayuri.core import Sayuri_Core
import json
from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.patch_stdout import patch_stdout

import subprocess
import platform

def chat():
    global last_interaction, alert_pending

    if platform.system().lower() == "windows":
        subprocess.run('cls', shell=True)
    else:
        subprocess.run('clear', shell=True)
        
    print("\033[1;45m Sayuri 2.3 - CLI \033[0m\n")

    session = PromptSession(
        ANSI("\033[1;36mTu: \033[0m\n")
    )

    with patch_stdout():
        while True:
            sayuri = Sayuri_Core()

            user_text = session.prompt().strip()

            if not user_text:
                continue

            if user_text.lower() in ("salir", "quit", "exit"):
                print_formatted_text("")
                print_formatted_text(
                    ANSI("\033[1;45m EXIT \033[0m")
                )
                break
            
            if user_text.lower() in ("factory_reset"):
                sayuri.factory_reset()
                print_formatted_text("")
                print_formatted_text(
                    ANSI("\033[1;45m FACTORY RESET \033[0m")
                )            
                continue

            response = json.loads(sayuri.answer(user_text))

            print_formatted_text("")
            print_formatted_text(
                ANSI(f"\033[1;35mSayuri:\033[0m\n{response.get('message')}")
            )
            
            status = ""

            if response.get('memory_saved'):
                status += f"\033[1;45m Memory \033[0m "
                                
            if response.get('note_saved'):
                status += f"\033[1;45m Note \033[0m"

            if status:
                print_formatted_text(ANSI(status))

            print_formatted_text("")

if __name__ == "__main__":
    chat()
