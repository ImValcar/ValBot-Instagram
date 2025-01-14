# ValBot-Instagram
<div align="center">
  ValBot, made by Valcar ;)
</div>

# Index
* ### [Explanation](#-explanation)
* ### [Requirements](#-requirements)
* ### [Installation](#-installation)
* ### [Usage](#-usage)
* ### [License](#-license)

# 📖 Explanation
ValBot is a tool built with Python and Selenium. It aims to store all the follower and following information from an Instagram profile in an SQLITE database.

It is designed to be used on a server (which must have the Gotify service running), where execution would be automated, and it would send a notification to your mobile via the Gotify app.

However, it can also be used as a tool to run occasionally and check if there have been any changes to your Instagram account. You can see which profiles you follow but don't follow you back using a command option.

Additionally, you can monitor the steps the program takes at any given moment if you have a graphical interface, by commenting on line 21 of the script.

I’ve included the empty SQLITE database file in the repository to make it easier to use. However, if you prefer to do it yourself, here are the instructions you should run in the database:
```
  CREATE TABLE CUENTAS (USERNAME TEXT PRIMARY KEY CHECK (length(USERNAME) <= 30), PASSWORD TEXT);

  CREATE TABLE IF NOT EXISTS FOLLOWS (SEGUIDOR TEXT NOT NULL,SEGUIDO TEXT NOT NULL,PRIMARY KEY (SEGUIDOR, SEGUIDO),FOREIGN KEY (SEGUIDOR) REFERENCES CUENTAS(USERNAME) ON DELETE CASCADE,FOREIGN KEY (SEGUIDO) REFERENCES CUENTAS (USERNAME)
 
  CREATE TABLE UNFOLLOWS (SEGUIDOR TEXT, SEGUIDO TEXT, FECHA TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (SEGUIDOR) REFERENCES CUENTAS(USERNAME),FOREIGN KEY (SEGUIDO) REFERENCES CUENTAS(USERNAME));
```

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
# 📜 License
```
        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
                    Version 2, December 2004 

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 

 Everyone is permitted to copy and distribute verbatim or modified 
 copies of this license document, and changing it is allowed as long 
 as the name is changed. 

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 

  0. You just DO WHAT THE FUCK YOU WANT TO.
```
<a href="http://www.wtfpl.net/"><img
       src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png"
       width="80" height="15" alt="WTFPL" /></a>
