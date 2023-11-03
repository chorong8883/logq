# logqueue
Log Queue

## Initialize
Declare thread function.  
```python  
def logger_function(log_dict):
    print(log_dict)
    # ...
```
output:  
{'log_type': 'exception',  
'timestamp': 1700000000.100001,  
'process_id': 1234,  
'thread_id': 1234567890,  
'cpu_usage': 12, # if exist psutil  
'memory_usage': 12, # if exist psutil  
'file_name': 'test.py',  
'file_lineno': 1,  
'text': 'start',  
'trace_back': 'error'} # if exception  
 
```python  
import logqueue
logqueue.initialize(logger_function)
# ...
```

## Close and Join
```python  
logqueue.close()
logqueue.join()
```
Signal
```python  
import signal
import logqueue

def signal_handler(_, frame):
    logqueue.close()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ... 
logqueue.join()
```

## Logging
```python  
logqueue.put_info("start")
# or
logqueue.info("start")
```  

#### **kwargs
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
'text': 'hi',  
'alarm_meesage': "alarm",  
'input_database': True}  

#### Log function types
```python  
logqueue.put(log_type:str, *objs:object, **kwargs)
logqueue.info(*objs:object, **kwargs) # or put_info()
logqueue.debug(*objs:object, **kwargs) # or put_debug()
logqueue.exception(*objs:object, **kwargs) # or put_exception()
logqueue.signal(*objs:object, **kwargs) # or put_signal()
```

## Parse
```python  
log_str = logqueue.parse(log_dict)
print(log_str)
```
output:  
2023-11-15 07:13:20.100001 12%:CPU 12%:Mem 234:PID 4567890:TID info test.py:1 start  

```python
get_log_formatters() # default log formatters
# {date} {time} {process_id:0{process_id_max_length}d}:PID {thread_id:0{thread_id_max_length}d}:TID {file_name:>{file_name_length}}:{file_lineno:<{file_lineno_length}} {log_type:{log_type_max_length}} {text}
clear_log_formatter()

append_log_formatter(f"{{{LogKey.date}}}")
append_log_formatter(f"{{{LogKey.time}}}")
get_log_formatters()
# {date} {time}
```
```python
set_date_formatter("%y-%m-%d")
get_date_formatter()
# %y-%m-%d
```
```python
set_process_id_formatter(f"{{{LogKey.process_id}:0{{{LogKey.process_id_max_length}}}d}}:PID")
get_process_id_formatter()
# {process_id:0{process_id_max_length}d}:PID
```

### LogKeys
```python
LogKey.date  
LogKey.time  
LogKey.timestamp  
LogKey.process_id  
LogKey.process_id_max_length  
LogKey.thread_id  
LogKey.thread_id_max_length  
LogKey.cpu_usage  
LogKey.memory_usage  
LogKey.log_type  
LogKey.log_type_max_length  
LogKey.file_info  
LogKey.file_name  
LogKey.file_name_length  
LogKey.file_lineno  
LogKey.file_lineno_length  
LogKey.text  
LogKey.trace_back  
```