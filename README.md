# logq
Log Queue

## implement logq.get()
```python  
import logq
def log_worker():
    while True:
        log_dict = logq.get()
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
logq.info("start")
logq.info("finish")
```

```python 
log_dict = logq.get()
print(log_dict)
```
output:  
{'timestamp': 1700000000.100001, 'process_id': 1234, 'thread_id': 1234567890, 'log_type': 'information', 'file_name': 'test.py', 'file_lineno': 2, 'text': 'start'}  
{'timestamp': 1700000000.100002, 'process_id': 1234, 'thread_id': 1234567890, 'log_type': 'information', 'file_name': 'test.py', 'file_lineno': 2, 'text': 'start'}  

## flush logq.get()
```python  
def log_worker():
    while True:
        log_dict = logq.get()
        if not log_dict:
            break
        print(log_dict)

    while not logq.empty():
        log_dict = logq.get()
        print(log_dict)
        
    print("flush queue")
```