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

### **kwargs
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

### Log types
```python  
logqueue.put(log_type:str, *objs:object, **kwargs)
logqueue.info(*objs:object, **kwargs) # or put_info() and == put(LogType.INFORMATION,)
logqueue.debug(*objs:object, **kwargs) # or put_debug() and == put(LogType.DEBUG,)
logqueue.warning(*objs:object, **kwargs) # or put_warning() and == put(LogType.WARNING,)
logqueue.exception(*objs:object, **kwargs) # or put_exception() and == put(LogType.EXCEPTION,)
logqueue.signal(*objs:object, **kwargs) # or put_signal() and == put(LogType.SIGNAL,)
```

## Parse
```python  
log_str = logqueue.parse(log_dict)
print(log_str)
```
output:  
2023-11-15 07:13:20.100001 12%:CPU 12%:Mem 234:PID 4567890:TID info test.py:1 start  

### Parse Formatter
```python
log_formatter = logqueue.get_log_formatter() # default log formatters
# {date} {time} {process_id:0{process_id_max_length}d}:PID {thread_id:0{thread_id_max_length}d}:TID {file_name:>{file_name_length}}:{file_lineno:<{file_lineno_length}} {log_type:{log_type_max_length}} {text}
logqueue.clear_log_formatter()

date_formatter = f"{{{logqueue.LogFormatterKey.date}}}"
time_formatter = f"{{{logqueue.LogFormatterKey.time}}}"
append_log_formatter(date_formatter)
append_log_formatter(time_formatter)
log_formatter = logqueue.get_log_formatter()
# {date} {time}

pid_formatter = logqueue.get_process_id_formatter()
# == f"{{{logqueue.LogFormatterKey.process_id}:0{{{logqueue.LogFormatterKey.process_id_max_length}}}d}}:PID"
file_name_formatter = f"{{{logqueue.LogFormatterKey.file_name}:>{{{logqueue.LogFormatterKey.file_name_length}}}}}"
text = logqueue.get_text_formatter()
logqueue.append_log_formatters(pid_formatter, file_name_formatter, text)
log_formatter = logqueue.get_log_formatter()
# {date} {time} {process_id:0{process_id_max_length}d}:PID {file_name:>{file_name_length}} {text}

logqueue.replace_log_formatter(pid_formatter)
log_formatter = logqueue.get_log_formatter()
# {date} {time} {file_name:>{file_name_length}}

logqueue.replace_log_formatter(time_formatter, pid_formatter)
log_formatter = logqueue.get_log_formatter()
# {date} {process_id:0{process_id_max_length}d}:PID {file_name:>{file_name_length}}
```

```python
logqueue.set_date_formatter("%y-%m-%d")
date_formatter = logqueue.get_date_formatter()
# %y-%m-%d
```
```python
logqueue.set_process_id_formatter(f"{{{logqueue.LogFormatterKey.process_id}:0{{{logqueue.LogFormatterKey.process_id_max_length}}}d}}:PID")
process_id_formatter = logqueue.get_process_id_formatter()
# {process_id:0{process_id_max_length}d}:PID
```

## Keys
```python
class LogDictKey:
    log_type
    timestamp
    process_id
    thread_id
    cpu_usage
    memory_usage
    file_name
    file_lineno
    text
    trace_back
```
```python
class LogFormatterKey:
    date
    time
    timestamp
    process_id
    process_id_max_length
    thread_id
    thread_id_max_length
    cpu_usage
    cpu_usage_max_length
    memory_usage
    memory_usage_max_length
    log_type
    log_type_max_length
    file_info
    file_name
    file_name_length
    file_lineno
    file_lineno_length
    text
    trace_back
```