# Smart Remote for your Smart Phone

## Installation

Clone this repository into your paspberry pi
```bash
$ git clone https://github.com/notfoundsam/smart-remote.git
$ cd smart-remote
```

## Run services on local machine by docker or create each service by yourself (mysql, node-red, influxdb, grafana, mosquitto)
```bash
$ docker-compose -f docker-compose-server.yml up -d
```

## Install python requirements
```bash
$ pip install --no-cache-dir -r requirements.txt
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
$ flask db downgrade
```

## Run development mode on docker

```bash
$ docker-compose up
```

## Swarm mode
```bash
$ docker stack deploy --compose-file docker-compose-swarm.yml smart-home
```

<link rel="apple-touch-icon" sizes="120x120" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="mask-icon" href="/safari-pinned-tab.svg" color="#5bbad5">
<meta name="msapplication-TileColor" content="#da532c">
<meta name="theme-color" content="#ffffff">

### node red as volume in ubuntu, set chmod 777 to mounted folder

### pip update packages
`pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U`

### generate requirements
pip freeze > requirements.txt
