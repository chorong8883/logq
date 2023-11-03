import threading
from datetime import datetime
import os
import inspect
import multiprocessing
import ctypes
import traceback

is_psutil = False
try:
    import psutil
    is_psutil = True
except ModuleNotFoundError:
    pass

import multiprocessing
import ctypes
from datetime import datetime

__caller_count_key = '__^caller_count%'

__log_queue = multiprocessing.Queue()

__log_thread : threading.Thread = None
__logger_function = None 

def __logger_threading(logger_function):
    while True:
        log_dict = __log_queue.get()
        if log_dict is None:
            break
        logger_function(log_dict)

def initialize(logger_function, args=()):
    global __log_thread
    global __logger_function
    __logger_function = logger_function
    __log_thread = threading.Thread(target=__logger_threading, args=(logger_function,))
    __log_thread.start()
    
    append_log_formatter(__datetime_formatter.value)
    if is_psutil:
        append_log_formatter(__cpu_usage_formatter.value)
        append_log_formatter(__memory_usage_formatter.value)
    
    append_log_formatter(__process_id_formatter.value)
    append_log_formatter(__thread_id_formatter.value)
    append_log_formatter(f"{__file_name_formatter.value}:{__file_lineno_formatter.value}")
    append_log_formatter(get_log_type_formatter())
    append_log_formatter(f"{{{LogKey.text}}}")

def close():
    '''
    put None log queue 
    '''
    __log_queue.put_nowait(None)

def join():
    '''
    join log queue thread
    '''
    __log_thread.join()
    while __log_queue.empty() is False:
        log_dict = __log_queue.get_nowait()
        if log_dict is None:
            continue
        __logger_function(log_dict)
    
def empty() -> bool:
    return __log_queue.empty()

class LogType:
    INFORMATION = 'information'
    DEBUG = 'debug'
    EXCEPTION = 'exception'
    SIGNAL = 'signal'

class LogKey:
    date = 'date'
    time = 'time'
    timestamp = 'timestamp'
    process_id = 'process_id'
    process_id_max_length = 'process_id_max_length'
    thread_id = 'thread_id'
    thread_id_max_length = 'thread_id_max_length'
    cpu_usage = 'cpu_usage'
    memory_usage = 'memory_usage'
    log_type = 'log_type'
    log_type_max_length = 'log_type_max_length'
    file_info = 'file_info'
    file_name = 'file_name'
    file_name_length = 'file_name_length'
    file_lineno = 'file_lineno'
    file_lineno_length = 'file_lineno_length'
    text = 'text'
    trace_back = 'trace_back'
    
    @classmethod
    def change_key(self, src, dst):
        print(self.date, src, dst)

__enable_log_type = multiprocessing.Value(ctypes.c_bool, True)
__enable_is_timestamp = multiprocessing.Value(ctypes.c_bool, True)
__enable_process_id = multiprocessing.Value(ctypes.c_bool, True)
__enable_thread_id = multiprocessing.Value(ctypes.c_bool, True)
__enable_cpu_usage = multiprocessing.Value(ctypes.c_bool, True)
__enable_memory_usage = multiprocessing.Value(ctypes.c_bool, True)
__enable_file_name = multiprocessing.Value(ctypes.c_bool, True)
__enable_file_lineno = multiprocessing.Value(ctypes.c_bool, True)
__enable_text = multiprocessing.Value(ctypes.c_bool, True)
__enable_trace_back = multiprocessing.Value(ctypes.c_bool, True)

def enable_log_type(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_log_type', 'is_enable' : is_enable})
def enable_is_timestamp(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_is_timestamp', 'is_enable' : is_enable})
def enable_process_id(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_process_id', 'is_enable' : is_enable})
def enable_thread_id(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_thread_id', 'is_enable' : is_enable})
def enable_cpu_usage(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_cpu_usage', 'is_enable' : is_enable})
def enable_memory_usage(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_memory_usage', 'is_enable' : is_enable})
def enable_file_name(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_file_name', 'is_enable' : is_enable})
def enable_file_lineno(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_file_lineno', 'is_enable' : is_enable})
def enable_text(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_text', 'is_enable' : is_enable})
def enable_trace_back(is_enable:bool): __log_queue.put_nowait({'command' : 'enable_trace_back', 'is_enable' : is_enable})

def get(timeout:float = None):
    '''
    Return
    -
    (dict) \n
    'log_type'\n
    'timestamp'\n
    'process_id'\n
    'thread_id'\n
    'file_name'\n
    'file_lineno'\n
    'text'\n
    exception\n
    'traceback'\n
    **kwargs\n
    '''
    is_next = True
    data = None
    while is_next:
        data = __log_queue.get(timeout = timeout)
        if data and ('command' in data):
            is_next = True
            match data['command']:
                case 'enable_log_type':
                    __enable_log_type.value = data['is_enable']
                case 'enable_is_timestamp':
                    __enable_is_timestamp.value = data['is_enable']
                case 'enable_process_id':
                    __enable_process_id.value = data['is_enable']
                case 'enable_thread_id':
                    __enable_thread_id.value = data['is_enable']
                case 'enable_cpu_usage':
                    __enable_cpu_usage.value = data['is_enable']
                case 'enable_memory_usage':
                    __enable_memory_usage.value = data['is_enable']
                case 'enable_file_name':
                    __enable_file_name.value = data['is_enable']
                case 'enable_file_lineno':
                    __enable_file_lineno.value = data['is_enable']
                case 'enable_text':
                    __enable_text.value = data['is_enable']
                case 'enable_trace_back':
                    __enable_trace_back.value = data['is_enable']
                case _:
                    pass
        else:
            is_next = False
    return data

def __get_log_dict(log_type:str, *objs:object, **kwargs) -> dict:
    log_dict = {}
    if __enable_log_type.value:
        log_dict[LogKey.log_type] = log_type
    
    if __enable_is_timestamp.value:
        log_dict[LogKey.timestamp] = datetime.now().timestamp()
    
    if __enable_process_id.value:
        log_dict[LogKey.process_id] = os.getpid()
    
    if __enable_thread_id.value:
        log_dict[LogKey.thread_id] = threading.current_thread().ident
    
    if is_psutil:
        if __enable_cpu_usage.value:
            log_dict[LogKey.cpu_usage] = psutil.cpu_percent()
        
    if is_psutil:
        if __enable_memory_usage.value:
            log_dict[LogKey.memory_usage] = dict(psutil.virtual_memory()._asdict())['percent']
        
    if __enable_file_name.value or __enable_file_lineno.value:
        caller_count = kwargs[__caller_count_key]
        frame_stack = inspect.stack()
        caller_frame = frame_stack[caller_count]
        caller_file_lineno = caller_frame.lineno
        splitted_caller_file_name = caller_frame.filename.split('/')
        caller_file_name = splitted_caller_file_name[-1]
        if caller_file_name == '__init__.py':
            caller_file_name = '/'.join(splitted_caller_file_name[-2:])
        if __enable_file_name.value:
            log_dict[LogKey.file_name] = caller_file_name
        if __enable_file_lineno.value:
            log_dict[LogKey.file_lineno] = caller_file_lineno
            
    if __enable_text.value:
        temp_text_list = []
        for obj in objs:
            temp_text_list.append(str(obj))
        log_dict[LogKey.text] = ' '.join(temp_text_list)
    
    if __enable_trace_back.value and log_type == LogType.EXCEPTION:
        log_dict[LogKey.trace_back] = traceback.format_exc()
    
    if kwargs:
        del kwargs[__caller_count_key]
        log_dict.update(**kwargs)
    return log_dict

def put(log_type:str, *objs:object, **kwargs):
    '''
    Parameter
    -
    log_type (str) : input custom type 
    '''
    if __caller_count_key in kwargs:
        kwargs[__caller_count_key] += 1
    else:
        kwargs[__caller_count_key] = 2
    log_dict = __get_log_dict(log_type, *objs, **kwargs)
    __log_queue.put_nowait(log_dict)
    
def info(*objs:object, **kwargs):      kwargs[__caller_count_key] = 2; put(LogType.INFORMATION, *objs, **kwargs)
def put_info(*objs:object, **kwargs):      kwargs[__caller_count_key] = 2; put(LogType.INFORMATION, *objs, **kwargs)
def debug(*objs:object, **kwargs):     kwargs[__caller_count_key] = 2; put(LogType.DEBUG,       *objs, **kwargs)
def put_debug(*objs:object, **kwargs):     kwargs[__caller_count_key] = 2; put(LogType.DEBUG,       *objs, **kwargs)
def exception(*objs:object, **kwargs): kwargs[__caller_count_key] = 2; put(LogType.EXCEPTION,   *objs, **kwargs)
def put_exception(*objs:object, **kwargs): kwargs[__caller_count_key] = 2; put(LogType.EXCEPTION,   *objs, **kwargs)
def signal(*objs:object, **kwargs):    kwargs[__caller_count_key] = 2; put(LogType.SIGNAL,      *objs, **kwargs)
def put_signal(*objs:object, **kwargs):    kwargs[__caller_count_key] = 2; put(LogType.SIGNAL,      *objs, **kwargs)
    
    
 ####################################################################################################################   
 ####################################################################################################################   
 ####################################################################################################################   
 ####################################################################################################################   
 ####################################################################################################################   
 # Parser


def cut_tail_str(src:str, length:int, is_ellipsis = False):
    if length < len(src):
        if is_ellipsis:
            return src[:length-2] + '..'
        else:
            return src[:length]
    return src

def cut_front_int(src:int, length:int):
    if length < len(str(src)):
        return src%(10**length)
    return src

__process_id_max_length = multiprocessing.Value(ctypes.c_int8, 3)
__thread_id_max_length = multiprocessing.Value(ctypes.c_int8, 6)
__log_type_max_length = multiprocessing.Value(ctypes.c_int8, 4)
def get_log_type_max_length():
    return __log_type_max_length.value
def set_log_type_max_length(length:int):
    __log_type_max_length.value = length
__file_name_length = multiprocessing.Value(ctypes.c_int8, 0)
__file_name_max_length = multiprocessing.Value(ctypes.c_int8, 15)
__file_lineno_length = multiprocessing.Value(ctypes.c_int8, 0)
__file_lineno_max_length = multiprocessing.Value(ctypes.c_int8, 4)

__datetime_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.date}}} {{{LogKey.time}}}")
__date_formatter = multiprocessing.Value(ctypes.c_wchar_p, "%y-%m-%d")
def get_date_formatter():
    return __date_formatter.value
def set_date_formatter(formatter:str):
    __date_formatter.value = formatter
__time_formatter = multiprocessing.Value(ctypes.c_wchar_p, "%H:%M:%S.%f")
__process_id_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.process_id}:0{{{LogKey.process_id_max_length}}}d}}:PID")
def get_process_id_formatter():
    return __process_id_formatter.value
def set_process_id_formatter(formatter:str):
    __process_id_formatter.value = formatter

__thread_id_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.thread_id}:0{{{LogKey.thread_id_max_length}}}d}}:TID")
__cpu_usage_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.cpu_usage}:>2}}%:CPU")
__memory_usage_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.memory_usage}:>2}}%:Mem")
__log_type_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.log_type}:{{{LogKey.log_type_max_length}}}}}")
def get_log_type_formatter():
    return __log_type_formatter.value
def set_log_type_formatter(formatter:str):
    __log_type_formatter.value = formatter
__file_name_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.file_name}:>{{{LogKey.file_name_length}}}}}")
__file_lineno_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.file_lineno}:<{{{LogKey.file_lineno_length}}}}}")

__log_formatter = multiprocessing.Value(ctypes.c_wchar_p, "")

def get_log_formatters() -> str:
    return __log_formatter.value
    
def clear_log_formatter():
    __log_formatter.value = ""

def append_log_formatter(formatter:str):
    if __log_formatter.value != "":
        formatter = f" {formatter}"
    __log_formatter.value += f"{formatter}"
    
def append_log_formatters(*formatters:str):
    fstr = ' '.join(formatters)
    if __log_formatter.value != "":
        fstr = f" {fstr}"
    __log_formatter.value += f"{fstr}"
        

__is_parse_log_type = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_date = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_time = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_process_id = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_thread_id = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_cpu_usage = multiprocessing.Value(ctypes.c_bool, is_psutil)
__is_parse_memory_usage = multiprocessing.Value(ctypes.c_bool, is_psutil)
__is_parse_file_name = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_file_lineno = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_text = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_trace_back = multiprocessing.Value(ctypes.c_bool, True)
__is_parse_signal_break_line = multiprocessing.Value(ctypes.c_bool, True)

def enable_parse_log_type(is_parse:bool): __is_parse_log_type.value = is_parse
def enable_parse_date(is_parse:bool): __is_parse_date.value = is_parse
def enable_parse_time(is_parse:bool): __is_parse_time.value = is_parse
def enable_parse_process_id(is_parse:bool): __is_parse_process_id.value = is_parse
def enable_parse_thread_id(is_parse:bool): __is_parse_thread_id.value = is_parse
def enable_parse_cpu_usage(is_parse:bool): __is_parse_cpu_usage.value = is_parse
def enable_parse_memory_usage(is_parse:bool): __is_parse_memory_usage.value = is_parse
def enable_parse_file_name(is_parse:bool): __is_parse_file_name.value = is_parse
def enable_parse_file_lineno(is_parse:bool): __is_parse_file_lineno.value = is_parse
def enable_parse_text(is_parse:bool): __is_parse_text.value = is_parse
def enable_parse_trace_back(is_parse:bool): __is_parse_trace_back.value = is_parse
def enable_parse_signal_break_line(is_parse:bool): __is_parse_signal_break_line.value = is_parse

def parse(log_dict:dict):
    log_formatter = get_log_formatters()
    result_dict = {}
    if __is_parse_log_type.value:
        result_dict[LogKey.log_type] = cut_tail_str(log_dict[LogKey.log_type], __log_type_max_length.value)
        result_dict[LogKey.log_type_max_length] = __log_type_max_length.value
    if __is_parse_date.value:
        result_dict[LogKey.date] = datetime.fromtimestamp(log_dict[LogKey.timestamp]).strftime(__date_formatter.value)
    if __is_parse_time.value:
        result_dict[LogKey.time] = datetime.fromtimestamp(log_dict[LogKey.timestamp]).strftime(__time_formatter.value)
    if __is_parse_process_id.value:
        result_dict[LogKey.process_id] = cut_front_int(log_dict[LogKey.process_id], __process_id_max_length.value)
        result_dict[LogKey.process_id_max_length] = __process_id_max_length.value
    if __is_parse_thread_id.value:
        result_dict[LogKey.thread_id] = cut_front_int(log_dict[LogKey.thread_id], __thread_id_max_length.value)
        result_dict[LogKey.thread_id_max_length] = __thread_id_max_length.value
    if is_psutil:
        if __is_parse_cpu_usage.value:
            result_dict[LogKey.cpu_usage] = log_dict[LogKey.cpu_usage]
    if is_psutil:
        if __is_parse_memory_usage.value:
            result_dict[LogKey.memory_usage] = log_dict[LogKey.memory_usage]
    if __is_parse_file_name.value:
        if __file_name_length.value < len(log_dict[LogKey.file_name]):
            __file_name_length.value = len(log_dict[LogKey.file_name])
        if __file_name_max_length.value < __file_name_length.value:
            __file_name_length.value = __file_name_max_length.value
        result_dict[LogKey.file_name] = cut_tail_str(log_dict[LogKey.file_name], __file_name_max_length.value, is_ellipsis = True)
        result_dict[LogKey.file_name_length] = __file_name_length.value
    if __is_parse_file_lineno.value:
        if __file_lineno_length.value < len(str(log_dict[LogKey.file_lineno])):
            __file_lineno_length.value = len(str(log_dict[LogKey.file_lineno]))
        result_dict[LogKey.file_lineno] = log_dict[LogKey.file_lineno]
        result_dict[LogKey.file_lineno_length] = __file_lineno_length.value
    if __is_parse_text.value:
        result_dict[LogKey.text] = log_dict[LogKey.text]
    if __is_parse_trace_back.value and log_dict[LogKey.log_type] == LogType.EXCEPTION:
        log_formatter += f"\n{{{LogKey.trace_back}}}" 
        result_dict[LogKey.trace_back] = log_dict[LogKey.trace_back]

    log_str = log_formatter.format(**result_dict)
    
    if __is_parse_signal_break_line.value and log_dict[LogKey.log_type] == LogType.SIGNAL:
        log_str = f"\n{log_str}" 
    
    return log_str
