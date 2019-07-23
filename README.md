# Smart Remote for your Smart Phone

## Installation

Clone this repository into your paspberry pi
```bash
$ git clone https://github.com/notfoundsam/smart-remote.git
$ cd smart-remote
```

## Production

### Run services on a local machine by docker or create each service by yourself (mysql, node-red, influxdb, grafana, mosquitto)
`$ make up-server` or `$ docker-compose -f docker-compose-server.yml up -d`

### Install python requirements
`$ pip install --no-cache-dir -r requirements.txt`

### Run the application
`$ python3 run.py`

### Or run it in background
`$ nohup python3 run.py > output.log &`

## Development

### Run the development mode on docker
`$ make up-dev` or `$ docker-compose up`

### Flask create migration
`$ flask db migrate --rev-id 001`

### Flask db migrate dev/prod
`$ make migrate` or `$ flask db upgrade`

### Flask db rollback dev/prod
`$ make rollback` or `$ flask db downgrade`

### Swarm mode
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
`$ pip freeze > requirements.txt`

### find running process
`$ ps ax | grep run.py`
