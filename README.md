# ValBot-Instagram
ValBot, made by Valcar ;)

# Index
* ### [Explanation](#-explanation)
* ### [Requirements](#-requirements)
* ### [Installation](#-installation)
* ### [Usage](#-usage)

# 📖 Explanation


# 💻 Requirements
To run this app you will need:
  - python3 --> (https://www.python.org/downloads/)
  - sqlite3 -->(https://www.sqlite.org/download.html)
  - A gotify server
  - Change the variables on lines 18 and 19
  - A .env file with a key to encrypt the password

# 🚀 Installation
To install ValBot follow these steps:
1. Clone the repository and set it as your working directory   
   ```
   git clone https://github.com/ImValcar/ValBot-Instagram
   cd ValBot-Instagram
   ```
2. (Optional) Create a venv  
   ```python -m venv .```
3. Install the required packages  
   ```pip install -r requirements.txt```

# ☕ Usage
```
python3 main.py --usuario USER --destinatario RECIEVER [--commonfollows] [--register]

SOME RULES:
   - The parameters --usuario and --destinatario must NEVER be empty.
   - The --usuario parameter corresponds to the user (whose name must match their Instagram account name and password, and the entrie must exist in the database) whose followers will be queried. (If it's not found in the database, use the --register option.)
   - The --destinatario parameter must correspond to the GOTIFY USERNAME that will receive the notification. It must match the name used to store their GOTIFY name and ID in the .env file. EXAMPLE: PAQUITO=Ab4JKnouyL_DwFF
   - The --commonfollows parameter will only send the list of users who don't follow you back but whom you follow. It will not update the database; it simply retrieves this information from the existing data.

options:
  -h, --help                    Show this help message and exit

  --usuario USER                The Instagram username (This parameter must never be empty).

  --destinatario RECEIVER       Who will receive the notification (This parameter must never be empty)

  --register                    Who will receive the notification (This parameter must never be empty).

  --commonfollows               To find out who you follow that doesn't follow you back.

By Valcar :D
```
