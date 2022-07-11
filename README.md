# ElecTrap Backend

## Requirements

+ Python 3.8.13+
+ A webcam on host

## Build Steps

### Install environment and dependencies

```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Run it(Linux)

```
CAMERA=hands python app.py
CAMERA=head  python app.py
CAMERA=foot  python app.py
```

### Run it(windows cmd)

```
set CAMERA=hands
python app.py
set CAMERA=head
python app.py
set CAMERA=foot
python app.py
```

### View it on web browser and play fun

```
http://localhost:5000
```

