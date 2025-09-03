#Commands to activate virtual environment:

**First, move into your project’s root directory (where src/ and requirements.txt will live):**

cd ~/path/to/your/project


**Now create a virtual environment named .venv (you can name it anything, but .venv is common):**
python3 -m venv .venv

**activating virtual environment**
source .venv/bin/activate

**to deactivate**
deactivate

**Install All Requirements at Once**
pip install -r requirements.txt
