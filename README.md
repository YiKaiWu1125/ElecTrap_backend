# ElecTrap Backend

## Requirements

+ Python 3.8.13+
+ A webcam on host
+ PostgreSQL
+ Redis

## Build Steps

### Install and enable the database

```
sudo pacman -S postgresql redis
sudo systemctl enable postgresql --now
sudo systemctl enable redis --now
```

### Configure PostgreSQL

```
sudo -iu postgres
createdb ElecTrap_scoreboard
```

### Install environment and dependencies

```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Run it

```
python app.py
```

### View it on web browser and play fun

```
http://localhost:5000
```

