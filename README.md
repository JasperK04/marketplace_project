Final project for the course "Database driven Webtechnology" at the University of Groningen.

## Setup

### Create venv

> [!IMPORTANT]
> This project was developed using Python 3.10.12. We make no guarantees it will function correctly with other versions of Python.

```bash
python3 -m venv .venv
```

### Activate venv

```bash
source .venv/bin/activate
```

### Install requirements

```bash
pip install -r requirements.txt
```

### Seed the database

> [!WARNING]
> This will delete all data in the database. Do not run this if you already have a database

```bash
flask cli recreate-db
```

### (Optional) Create admin user

```bash
flask cli create-admin
```

### Run the server

```bash
flask run
```
