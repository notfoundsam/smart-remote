# Smart Remote for your Smart Phone

## Installation

Clone this repository into your paspberry pi
```bash
$ git clone https://github.com/notfoundsam/smart-remote.git
$ cd smart-remote
```

Install python requirements
```bash
$ pip install --no-cache-dir -r requirements.txt
```

Create Data Base
```bash
$ python db_create.py
```

Run the application
```bash
$ python run.py
```

Check it
```bash
http://localhost:5000
```

## Flask create migration
```bash
$ flask db migrate --rev-id 001
```

## Flask migrate db
```bash
$ flask db upgrade
```

## Run development mode on docker

```bash
$ docker-compose up
```

## Swarm mode
```bash
$ docker stack deploy --compose-file docker-compose-swarm.yml smart-home
```
