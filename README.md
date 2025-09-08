<u>Commands to activate virtual environment:</u>
<ul>
    <li>**First, move into your project’s root directory (where src/ and requirements.txt will live) :**

<code>cd ~/path/to/your/project</code></li>


<li> **Now create a virtual environment named .venv (you can name it anything, but .venv is common) :**
<code>python3 -m venv .venv</code></li>

<li> **activating virtual environment :**
<code>source .venv/bin/activate</code></li>

<li> **to deactivate :** 
<code>deactivate</code></li>

<li> **Install All Requirements at Once :** 
<code>pip install -r requirements.txt</code></li>

</ul>


<h2>To run the code in Windows <code>operating system</code>: </h2>
<ul>
    <li>Python 3.8+ installed. Confirm with: <code>python --version</code> </li>

    <li>
    
</ul>

<u><h2>Structure of our Project's folder :</h2></u>


```fake-url-detector/
├── 📄 README.md
├── 📄 requirements.txt       # list of dependencies (no pip commands here)
├── 📂 src/
│   ├── 📄 main.py             # entrypoint (starts the app)
│   ├── 📂 app/
│   │   ├── 📂 dialogs/
│   │   │   ├── 📄 blacklist.py   # Blacklist Manager dialog
│   │   │   ├── 📄 watchlist.py
│   │   │   ├── 📄 rule_editor.py
│   │   │   ├── 📄 settings.py
│   │   │   └── 📄 logs.py
│   │   ├── 📂 controllers/
│   │   │   └── 📄 ui_controller.py  # connects UI and logic
│   │   ├── 📂 models/
│   │       └── 📄 table_models.py   # QAbstractTableModel classes
│   │   
│   │      
├── 📂 tests/
    └── 📄 test_ui_smoke.py

    
```

