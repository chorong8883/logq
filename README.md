# logqueue
Log Queue

## implement logqueue.get()
```python  
import logqueue
def log_worker():
    while True:
        log_dict = logqueue.get()
        if not log_dict:
            break
        print(log_dict)
    
thread = threading.Thread(target=log_worker)
thread.start()
# ...
# thread.join()
```

## logging
```python  
logqueue.info("start")
logqueue.info("finish")
```

```python 
log_dict = logqueue.get()
print(log_dict)
```
output:  
{'timestamp': 1700000000.100001, 'process_id': 1234, 'thread_id': 1234567890, 'log_type': 'information', 'file_name': 'test.py', 'file_lineno': 2, 'text': 'start'}  
{'timestamp': 1700000000.100002, 'process_id': 1234, 'thread_id': 1234567890, 'log_type': 'information', 'file_name': 'test.py', 'file_lineno': 2, 'text': 'start'}  

## flush logqueue.get()
```python  
def log_worker():
    while True:
        log_dict = logqueue.get()
        if not log_dict:
            break
        print(log_dict)

    while not logqueue.empty():
        log_dict = logqueue.get()
        print(log_dict)
        
    print("flush queue")
```
