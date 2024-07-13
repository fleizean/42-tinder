cd tinder42
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from app.database import create_database; create_database()"
python3 run.py