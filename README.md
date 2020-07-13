# Realtime-BigData-Dashboard

---
## Introduction
A demo for realtime dashboard, based on bigdata technology and popular realtime comunication web technology.

---
## Architect

### flow
- scrawler.py ---> kafka
- kafka ---> wordCounter.py
- wordCounter.py ---> kafka
- kafka ---> app.py
- app.py ---> browser

### diagram

Note: powered by asciiflow website [asciiflow](http://asciiflow.com/)

```
+--------------+                    +------------------+                     +----------------+
|              |         1          |                  |         4           |                |
|    Scrawler  +------------------> |     Kafka        +-------------------> |       Flask    |
|              |                    |                  |                     |                |
|              |                    |                  |                     |                |
+--------------+                    +----+---------+---+                     +--------+-------+
                                         |         ^                                  |
                                         |         |                                  |
                                       2 |         |3                                 |5
                                         |         |                                  |
                                         |         |                                  |
                                         |         |                                  v
                                     +---v---------+----+                    +--------+---------+
                                     |                  |                    |                  |
                                     |      Spark Stream|                    |       Browser    |
                                     |                  |                    |                  |
                                     |                  |                    |                  |
                                     +------------------+                    +------------------+

```

### Demo

![demo](wordCloud.png)

---
## Technology
### bigdata techs:
* kafka -- tranfer all data between components
* spark streaming -- data statistics
* scrawler -- get raw data from url.


### web techs:
* flask -- python web framework
* socket.io -- frontend/backend data exchange tunnel
* vue -- popular frontend JS framework

---
## Install
### Kafka

reference: http://dblab.xmu.edu.cn/blog/1096-2/

### Spark

reference: http://dblab.xmu.edu.cn/blog/1307-2/

### Dependency

enter project root directory
run such commands:

```
./bin/install.sh
```

---
## Run APP
### run zookeeper
open a new terminal, 
run such commands:

```
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

### run kafka
open a new terminal, 
run such commands:

```
rm -rf /tmp/kafka-logs/*
cd /usr/local/kafka
bin/kafka-server-start.sh config/server.properties
```

### run wordCounter
open a new terminal, 
enter project root directory,
run such commands:

```
./bin/startWordCounter.sh
```

### run wordStats Observor to watch word statistics
open a new terminal, 
enter project root directory,
run such commands:

```
python3 backend/wordStatsObserver.py
```

### run scrawler to get new page content and insert to wordCounter
open a new terminal, 
enter project root directory,
run such commands:

```
python3 backend/scrawler.py
```

Then go to wordStats observer to see new wordstats.

### build front code

open a new terminal, 
enter project root directory,
run such commands:

```
cd frontend/vueproj
npm install
npm run build
```


### run flask server

open a new terminal, 
enter project root directory,
run such commands:

```
python3 frontend/app.py
```

Then go to browser and access url 
http://127.0.0.1:5000/#/


---
## Note:
### inspiration
This project is inspired by chinese bigdata course:
http://dblab.xmu.edu.cn/post/8274/

### Markdown cheatsheet
ReadMe is written by Markdown, here is syntax cheatsheet [Markdown Syntax](https://www.markdown.xyz/cheat-sheet/)
