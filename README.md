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


## Open Command Prompt or Powershell
<ol>
<li>Navigate to your project folder:</li>

```powershell
cd "C:\path\to\fake-url-detector" ```

<li>Create a Virtual Environment :</li>
```cmd
python -m venv .venv ```

<li>Activate the Virtual Environment :</li>
```cmd
.venv\Scripts\activate ```

<li>Install Dependencies</li>
```cmd
pip install -r requirements.txt ```

<li>Run the Application :</li>
```cmd
cd src
python main.py ```

</ol>


  
    
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

