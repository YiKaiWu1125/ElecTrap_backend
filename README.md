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
### Build Postgresql server 
```
#Step 1:
https://postgresql-note.readthedocs.io/en/latest/section01/Install/01_install-PostgreSQL.html

#Step 2:
Open PgAdmin 4.exe 
Enter your password
Rename Server "ElecTrap_scoreboard"

#Step 3:Create Database
Database name = "ElecTrap_scoreboard"
Owner = postgre

#Step 4:Create Table "userinfo"
CREATE TABLE IF NOT EXISTS public.userinfo
(
    user_id integer NOT NULL DEFAULT nextval('userinfo_user_id_seq'::regclass),
    user_name character varying(20) COLLATE pg_catalog."default",
    game_mode character varying(20) COLLATE pg_catalog."default",
    game_body character varying(10) COLLATE pg_catalog."default",
    game_level integer,
    score integer,
    CONSTRAINT userinfo_pkey PRIMARY KEY (user_id)
)

#Step 5:Update app.py
+14 app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:yourpassword@localhost/ElecTrap_scoreboard'

+20 con = psycopg2.connect(database="ElecTrap_scoreboard", user="postgres", password="yourpassword", host="127.0.0.1", port="5432")
```

### Install Redis on Windows
```
Tutorial <https://marcus116.blogspot.com/2019/02/how-to-install-redis-in-windows-os.html>
```

### Run it

```
python app.py
```

### View it on web browser and play fun

```
http://localhost:5000
```

