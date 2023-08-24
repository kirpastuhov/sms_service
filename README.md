* Install requirements:  
```
pip3 install -r requirements.txt
```

## How to launch
* Start Redis instance in Docker using this command: 
```
docker run -p 6379:6379 -it redis/redis-stack:latest
```
* Run `python3 src/server.py`.  
* Go to `http://127.0.0.1:5000/` in your browser