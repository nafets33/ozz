# ozz
learning walks chatbot

pip install requirements.txt

streamlit run ozz_app.py
python ozz_api.py

# SSH
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys


# build component
del lock file
use zsh not bash
npm run build


# gcp setup nginx
1. updates site-avial
2. sudo ln
3. sudo cert

update only sites-enabled without CERTA

sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d divergent-thinkers.com

sudo ln -s /etc/nginx/sites-available/divergent-thinkers.com /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api.divergent-thinkers.com /etc/nginx/sites-enabled/


sudo certbot --nginx -d api.divergent-thinkers.com -d www.divergent-thinkers.com
#REMOVE sites-enabled

sudo systemctl restart nginx
sudo systemctl start nginx

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