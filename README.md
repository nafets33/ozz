# ozz
learning walks chatbot

pip install requirements.txt

streamlit run ozz_app.py
python ozz_api.py





#### OLD
brew install postgresql
initdb -D /path/to/data/directory
pg_ctl -D /path/to/data/directory start
createdb your_database_name
psql -U stefanstapinski -d ozz_db

psql -U stefanstapinski -d ozz_db

ALTER ROLE stefanstapinski PASSWORD 'ozz';



pkill -f postgres

ps aux | grep postgres
# find if port active
sudo lsof -i :8501
sudo lsof -i :8000
sudo kill -9