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
    
log_thread = threading.Thread(target=log_worker)
log_thread.start()
# ...
# log_thread.join()
```

## Close
```python  
import logqueue

def signal_handler(_, _):
    logqueue.close()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ... implement logqueue.get()
log_thread.start()
# ...
log_thread.join()
```

## Logging
```python  
logqueue.info("start")
logqueue.info("finish")
```  
```python 
log_dict = logqueue.get()
print(log_dict)
```
output:  
{'timestamp': 1700000000.100001, 'process_id': 1234, 'thread_id': 1234567890, 'log_type': 'information', 'file_name': 'test.py', 'file_lineno': 1, 'text': 'start'}  
{'timestamp': 1700000000.100002, 'process_id': 1234, 'thread_id': 1234567890, 'log_type': 'information', 'file_name': 'test.py', 'file_lineno': 2, 'text': 'finish'}  

```python  
log_str = logqueue.parse(log_dict)
print(log_str)
```
output:  
2023-11-15 07:13:20.100001 234:PID 4567890:TID info test.py:1 start  
2023-11-15 07:13:20.100002 234:PID 4567890:TID info test.py:2 finish  

## Flush queue
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