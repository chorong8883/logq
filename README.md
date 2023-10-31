# logqueue
Log Queue

## threading logqueue.get()
```python  
import logqueue
def log_thread_function():
    while True:
        log_dict = logqueue.get()
        if not log_dict:
            break
        print(log_dict)
```
```python  
import threading
log_thread = threading.Thread(target=log_thread_function)
log_thread.start()
# ...
log_thread.join()
```
or
```python  
import threading
threading.Thread(target=log_thread_function, daemon=True).start()
# ...
```

## Close
Implement 'close()' when 'daemon=False' in thread.  
No need 'close()' when 'daemon=True' in thread.  
```python  
import signal
import logqueue

def signal_handler(_, frame):
    logqueue.close()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ... implement logqueue.get()
log_thread.start()
# ...
log_thread.join()
```

### Flush queue
in log thread.  
```python  
def log_worker():
    while True:
        log_dict = logqueue.get()
        if not log_dict:
            print("Got None : Close")
            break
        print(log_dict)

    print("Flush queue")
    while not logqueue.empty():
        log_dict = logqueue.get()
        print(log_dict)
        
```

## Logging
```python  
logqueue.info("start")
```  
```python 
log_dict = logqueue.get()
print(log_dict)
```
output:  
{'timestamp': 1700000000.100001,  
'process_id': 1234,  
'thread_id': 1234567890,  
'log_type': 'information',  
'file_name': 'test.py',  
'file_lineno': 1,  
'text': 'start'}  

```python  
log_str = logqueue.parse(log_dict)
print(log_str)
```
output:  
2023-11-15 07:13:20.100001 234:PID 4567890:TID info test.py:1 start  
2023-11-15 07:13:20.100002 234:PID 4567890:TID info test.py:2 finish  

##### **kwargs
```python  
logqueue.info("hi", alarm_meesage="alarm", input_database=True)
```  
```python 
log_dict = logqueue.get()
print(log_dict)
```
output:  
{'timestamp': 1700000000.100001,  
'process_id': 1234,  
'thread_id': 1234567890,  
'log_type': 'information',  
'file_name': 'test.py',  
'file_lineno': 1,  
'text': 'start',  
'alarm_meesage': "alarm",  
'input_database': True}  

##### Log Types
```python  
logqueue.etc(log_type:str, *objs:object, **kwargs)
logqueue.info(*objs:object, **kwargs)
logqueue.debug(*objs:object, **kwargs)
logqueue.exception(*objs:object, **kwargs)
logqueue.signal(*objs:object, **kwargs)
```

## Parse
Default format:  
```python  
change_log_format(LogKey.date, LogKey.time, LogKey.process_id, LogKey.thread_id, LogKey.log_type, LogKey.file_info, LogKey.text)
```
== "{date} {time} {process_id} {thread_id} {log_type} {file_info} {text}"  

#### Change string format
```python  
change_log_format(LogKey.date, LogKey.time, LogKey.log_type, LogKey.file_name, LogKey.text)
```
== "{date} {time} {log_type} {file_name} {text}"  
output:  
2023-11-15 07:13:20.100001 info test.py start  

#### LogKey
```python
LogKey.date
LogKey.time
LogKey.process_id
LogKey.thread_id
LogKey.log_type
LogKey.file_info
LogKey.file_name
LogKey.file_lineno
LogKey.text
LogKey.traceback
```
Each string format can change.  
```python  
change_date_format(format_str:str)
change_time_format(format_str:str)
change_process_id_format(format_str:str)
change_thread_id_format(format_str:str)
# ...
```

