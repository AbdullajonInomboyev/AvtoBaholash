# AvtoBaholash — Deploy qilish

## Tezkor ishga tushirish (Development)

```bash
git clone https://github.com/your/edulens.git && cd edulens
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # va .env ni to'ldiring
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Production (Ubuntu 22.04)

### 1. Server tayyorlash
```bash
apt update && apt install -y python3-venv python3-pip nginx postgresql
```

### 2. PostgreSQL
```bash
sudo -u postgres psql -c "CREATE USER edulens WITH PASSWORD 'strong-pass';"
sudo -u postgres psql -c "CREATE DATABASE edulens OWNER edulens;"
```

### 3. Loyihani yuklash
```bash
cd /var/www && git clone ... edulens && cd edulens
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # DEBUG=False, to'g'ri ma'lumotlar
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_data  # Demo ma'lumotlar kerak bo'lsa
mkdir logs
```

### 4. Systemd service
```bash
cp edulens.service.example /etc/systemd/system/edulens.service
systemctl daemon-reload
systemctl enable edulens
systemctl start edulens
```

### 5. Nginx
```bash
cp nginx.conf.example /etc/nginx/sites-available/edulens
ln -s /etc/nginx/sites-available/edulens /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 6. SSL (Let's Encrypt)
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d edulens.uz -d www.edulens.uz
```

### 7. Cron
```bash
crontab -e
# Crontab.example ni qo'shing
```

### 8. Telegram bot webhook
```
https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://edulens.uz/assessment/webhook/telegram/
```

## Tekshiruv
```bash
python manage.py check --deploy
python manage.py test assessment
```
