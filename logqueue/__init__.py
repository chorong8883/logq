import threading
from datetime import datetime
import os
import inspect
import multiprocessing
import ctypes
import traceback
import platform

is_psutil = False
try:
    import psutil
    uname = platform.uname()
    if uname.system == "Darwin":
        from psutil._psosx import svmem
    elif uname.system == "Linux":
        from psutil._pslinux import svmem
    elif uname.system == "Windows":
        from psutil._pswindows import svmem
    is_psutil = True
except ModuleNotFoundError:
    pass
except Exception as e:
    print(e)

import multiprocessing
import ctypes
from datetime import datetime

__trace_caller_count_key = '.^trace&caller#count%'

__log_queue = multiprocessing.Queue()

__log_thread : threading.Thread = None
__log_formatter = multiprocessing.Value(ctypes.c_wchar_p, "")
__logger_function = None 

class LogType:
    INFORMATION = 'information'
    DEBUG = 'debug'
    WARNING = 'warning'
    EXCEPTION = 'exception'
    SIGNAL = 'signal'

class LogDictKey:
    log_type = 'log_type'
    timestamp = 'timestamp'
    process_id = 'process_id'
    thread_id = 'thread_id'
    cpu_usage = 'cpu_usage'
    memory_usage = 'memory_usage'
    file_name = 'file_name'
    file_lineno = 'file_lineno'
    text = 'text'
    trace_back = 'trace_back'

__is_load_log_type = multiprocessing.Value(ctypes.c_bool, True)
__is_load_timestamp = multiprocessing.Value(ctypes.c_bool, True)
__is_load_process_id = multiprocessing.Value(ctypes.c_bool, True)
__is_load_thread_id = multiprocessing.Value(ctypes.c_bool, True)
__is_load_cpu_usage = multiprocessing.Value(ctypes.c_bool, True)
__is_load_memory_usage = multiprocessing.Value(ctypes.c_bool, True)
__is_load_file_name = multiprocessing.Value(ctypes.c_bool, True)
__is_load_file_lineno = multiprocessing.Value(ctypes.c_bool, True)
__is_load_text = multiprocessing.Value(ctypes.c_bool, True)
__is_load_trace_back = multiprocessing.Value(ctypes.c_bool, True)

def enable_load_log_type():     __is_load_log_type.value = True
def enable_load_timestamp():    __is_load_timestamp.value = True
def enable_load_process_id():   __is_load_process_id.value = True
def enable_load_thread_id():    __is_load_thread_id.value = True
def enable_load_cpu_usage():    __is_load_cpu_usage.value = True
def enable_load_memory_usage(): __is_load_memory_usage.value = True
def enable_load_file_name():    __is_load_file_name.value = True
def enable_load_file_lineno():  __is_load_file_lineno.value = True
def enable_load_text():         __is_load_text.value = True
def enable_load_trace_back():   __is_load_trace_back.value = True

def disable_load_log_type():     __is_load_log_type.value = False
def disable_load_timestamp():    __is_load_timestamp.value = False
def disable_load_process_id():   __is_load_process_id.value = False
def disable_load_thread_id():    __is_load_thread_id.value = False
def disable_load_cpu_usage():    __is_load_cpu_usage.value = False
def disable_load_memory_usage(): __is_load_memory_usage.value = False
def disable_load_file_name():    __is_load_file_name.value = False
def disable_load_file_lineno():  __is_load_file_lineno.value = False
def disable_load_text():         __is_load_text.value = False
def disable_load_trace_back():   __is_load_trace_back.value = False


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
                case _:
                    pass
        else:
            is_next = False
    return data

def __get_log_dict(log_type:str, *objs:object, **kwargs) -> dict:
    log_dict = {}
    if __is_load_log_type.value:
        log_dict[LogDictKey.log_type] = log_type
    
    if __is_load_timestamp.value:
        log_dict[LogDictKey.timestamp] = datetime.now().timestamp()
    
    if __is_load_process_id.value:
        log_dict[LogDictKey.process_id] = os.getpid()
    
    if __is_load_thread_id.value:
        log_dict[LogDictKey.thread_id] = threading.current_thread().ident
    
    if is_psutil and __is_load_cpu_usage.value:
        log_dict[LogDictKey.cpu_usage] = psutil.cpu_percent()
        
    if is_psutil and __is_load_memory_usage.value:
        vm:svmem = psutil.virtual_memory()
        log_dict[LogDictKey.memory_usage] = vm.percent
        
    if __is_load_file_name.value or __is_load_file_lineno.value:
        caller_count = kwargs[__trace_caller_count_key]
        frame_stack = inspect.stack()
        caller_frame = frame_stack[caller_count]
        caller_file_lineno = caller_frame.lineno
        splitted_caller_file_name = caller_frame.filename.split('/')
        caller_file_name = splitted_caller_file_name[-1]
        if caller_file_name == '__init__.py':
            caller_file_name = '/'.join(splitted_caller_file_name[-2:])
        if __is_load_file_name.value:
            log_dict[LogDictKey.file_name] = caller_file_name
        if __is_load_file_lineno.value:
            log_dict[LogDictKey.file_lineno] = caller_file_lineno
            
    if __is_load_text.value:
        temp_text_list = []
        for obj in objs:
            temp_text_list.append(str(obj))
        log_dict[LogDictKey.text] = ' '.join(temp_text_list)
    
    if __is_load_trace_back.value and log_type == LogType.EXCEPTION:
        log_dict[LogDictKey.trace_back] = traceback.format_exc()
    
    if kwargs:
        del kwargs[__trace_caller_count_key]
        log_dict.update(**kwargs)
    return log_dict

def put(log_type:str, *objs:object, **kwargs):
    '''
    Parameter
    -
    log_type (str) : input custom type 
    '''
    if __trace_caller_count_key in kwargs:
        kwargs[__trace_caller_count_key] += 1
    else:
        kwargs[__trace_caller_count_key] = 2
    log_dict = __get_log_dict(log_type, *objs, **kwargs)
    __log_queue.put(log_dict)
    
def info(*objs:object, **kwargs):      kwargs[__trace_caller_count_key] = 2; put(LogType.INFORMATION, *objs, **kwargs)
def debug(*objs:object, **kwargs):     kwargs[__trace_caller_count_key] = 2; put(LogType.DEBUG,       *objs, **kwargs)
def warning(*objs:object, **kwargs):   kwargs[__trace_caller_count_key] = 2; put(LogType.WARNING,     *objs, **kwargs)
def exception(*objs:object, **kwargs): kwargs[__trace_caller_count_key] = 2; put(LogType.EXCEPTION,   *objs, **kwargs)
def signal(*objs:object, **kwargs):    kwargs[__trace_caller_count_key] = 2; put(LogType.SIGNAL,      *objs, **kwargs)

def put_info(*objs:object, **kwargs):      kwargs[__trace_caller_count_key] = 2; put(LogType.INFORMATION, *objs, **kwargs)
def put_debug(*objs:object, **kwargs):     kwargs[__trace_caller_count_key] = 2; put(LogType.DEBUG,       *objs, **kwargs)
def put_warning(*objs:object, **kwargs):   kwargs[__trace_caller_count_key] = 2; put(LogType.WARNING,     *objs, **kwargs)
def put_exception(*objs:object, **kwargs): kwargs[__trace_caller_count_key] = 2; put(LogType.EXCEPTION,   *objs, **kwargs)
def put_signal(*objs:object, **kwargs):    kwargs[__trace_caller_count_key] = 2; put(LogType.SIGNAL,      *objs, **kwargs)
    
    
####################################################################################################################
####################################################################################################################   
####################################################################################################################   
####################################################################################################################   
####################################################################################################################   
# Parser

class LogFormatterKey:
    date = 'f_date'
    time = 'f_time'
    timestamp = 'f_timestamp'
    process_id = 'f_process_id'
    process_id_max_length = 'f_process_id_max_length'
    thread_id = 'f_thread_id'
    thread_id_max_length = 'f_thread_id_max_length'
    cpu_usage = 'f_cpu_usage'
    cpu_usage_max_length = 'f_cpu_usage_max_length'
    memory_usage = 'f_memory_usage'
    memory_usage_max_length = 'f_memory_usage_max_length'
    log_type = 'f_log_type'
    log_type_max_length = 'f_log_type_max_length'
    file_info = 'f_file_info'
    file_name = 'f_file_name'
    file_name_length = 'f_file_name_length'
    file_lineno = 'f_file_lineno'
    file_lineno_length = 'f_file_lineno_length'
    text = 'f_text'
    trace_back = 'f_trace_back'
    
__log_type_max_length = multiprocessing.Value(ctypes.c_int8, 4)
__log_type_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.log_type}:{{{LogFormatterKey.log_type_max_length}}}}}")
__datetime_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.date}}} {{{LogFormatterKey.time}}}")
__date_formatter = multiprocessing.Value(ctypes.c_wchar_p, "%y-%m-%d")
__time_formatter = multiprocessing.Value(ctypes.c_wchar_p, "%H:%M:%S.%f")
__process_id_max_length = multiprocessing.Value(ctypes.c_int8, 3)
__process_id_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.process_id}:0{{{LogFormatterKey.process_id_max_length}}}d}}:PID")
__file_name_length = multiprocessing.Value(ctypes.c_int8, 0)
__file_name_max_length = multiprocessing.Value(ctypes.c_int8, 15)
__file_name_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.file_name}:>{{{LogFormatterKey.file_name_length}}}}}")
__file_lineno_length = multiprocessing.Value(ctypes.c_int8, 0)
__file_lineno_max_length = multiprocessing.Value(ctypes.c_int8, 4)
__file_lineno_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.file_lineno}:<{{{LogFormatterKey.file_lineno_length}}}}}")
__thread_id_max_length = multiprocessing.Value(ctypes.c_int8, 6)
__thread_id_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.thread_id}:0{{{LogFormatterKey.thread_id_max_length}}}d}}:TID")
__cpu_usage_max_length = multiprocessing.Value(ctypes.c_int8, 4)
__cpu_usage_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.cpu_usage}:>{{{LogFormatterKey.cpu_usage_max_length}}}}}%:CPU")
__memory_usage_max_length = multiprocessing.Value(ctypes.c_int8, 4)
__memory_usage_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.memory_usage}:>{{{LogFormatterKey.memory_usage_max_length}}}}}%:Mem")
__text_formatter = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogFormatterKey.text}}}")

####################################################################################################################   

def get_log_type_max_length():
    return __log_type_max_length.value
def set_log_type_max_length(length:int):
    __log_type_max_length.value = length
def get_log_type_formatter():
    return __log_type_formatter.value
def set_log_type_formatter(formatter:str):
    __log_type_formatter.value = formatter
    
####################################################################################################################
def get_date_formatter():
    return __date_formatter.value
def set_date_formatter(formatter:str):
    __date_formatter.value = formatter
def get_time_formatter():
    return __time_formatter.value
def set_time_formatter(formatter:str):
    __time_formatter.value = formatter

####################################################################################################################
def get_process_id_max_length():
    return __process_id_max_length.value
def set_process_id_max_length(length:int):
    __process_id_max_length.value = length
def get_process_id_formatter():
    return __process_id_formatter.value
def set_process_id_formatter(formatter:str):
    __process_id_formatter.value = formatter

####################################################################################################################
def get_file_name_max_length():
    return __file_name_max_length.value
def set_file_name_max_length(length:int):
    __file_name_max_length.value = length
def get_file_name_formatter():
    return __file_name_formatter.value
def set_file_name_formatter(formatter:str):
    __file_name_formatter.value = formatter
    
####################################################################################################################
def get_file_lineno_max_length():
    return __file_lineno_max_length.value
def set_file_lineno_max_length(length:int):
    __file_lineno_max_length.value = length
def get_file_lineno_formatter():
    return __file_lineno_formatter.value
def set_file_lineno_formatter(formatter:str):
    __file_lineno_formatter.value = formatter

####################################################################################################################
def get_thread_id_max_length():
    return __thread_id_max_length.value
def set_thread_id_max_length(length:int):
    __thread_id_max_length.value = length
def get_thread_id_formatter():
    return __thread_id_formatter.value
def set_thread_id_formatter(formatter:str):
    __thread_id_formatter.value = formatter

####################################################################################################################
def get_cpu_usage_max_length():
    return __cpu_usage_max_length.value
def set_cpu_usage_max_length(length:int):
    __cpu_usage_max_length.value = length
def get_cpu_usage_formatter():
    return __cpu_usage_formatter.value
def set_cpu_usage_formatter(formatter:str):
    __cpu_usage_formatter.value = formatter

####################################################################################################################
def get_memory_usage_max_length():
    return __memory_usage_max_length.value
def set_memory_usage_max_length(length:int):
    __memory_usage_max_length.value = length
def get_memory_usage_formatter():
    return __memory_usage_formatter.value
def set_memory_usage_formatter(formatter:str):
    __memory_usage_formatter.value = formatter

####################################################################################################################
def get_text_formatter():
    return __text_formatter.value
def set_text_formatter(formatter:str):
    __text_formatter.value = formatter

####################################################################################################################
def get_log_formatter() -> str:
    return __log_formatter.value
def clear_log_formatter():
    __log_formatter.value = ""
def append_log_formatter(formatter:str):
    if __log_formatter.value != "" and (0<len(formatter) and formatter[0] != '\n'):
        formatter = f" {formatter}"
    __log_formatter.value += f"{formatter}"
def append_log_formatters(*formatters:str):
    fstr = ' '.join(formatters)
    if __log_formatter.value != "":
        fstr = f" {fstr}"
    __log_formatter.value += f"{fstr}"
    
def replace_formatter(src:str, old_formatter:str, new_formatter:str=None) -> str:
    if new_formatter is None or new_formatter == '':
        new_formatter_str = ''
    else:
        new_formatter_str = f"{{{new_formatter}}}"
    find_index = src.find(old_formatter)
    if find_index == 0:
        src = src.replace(old_formatter, new_formatter_str)
    elif 0<find_index:
        src = src.replace(f" {old_formatter}", new_formatter_str)
    return src

def replace_log_formatter(old_formatter:str, new_formatter:str=None):
    __log_formatter.value = replace_formatter(__log_formatter.value, old_formatter, new_formatter)
        
####################################################################################################################
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

def enable_parse_log_type(): __is_parse_log_type.value = True
def enable_parse_date(): __is_parse_date.value = True
def enable_parse_time(): __is_parse_time.value = True
def enable_parse_process_id(): __is_parse_process_id.value = True
def enable_parse_thread_id(): __is_parse_thread_id.value = True
def enable_parse_cpu_usage(): __is_parse_cpu_usage.value = True
def enable_parse_memory_usage(): __is_parse_memory_usage.value = True
def enable_parse_file_name(): __is_parse_file_name.value = True
def enable_parse_file_lineno(): __is_parse_file_lineno.value = True
def enable_parse_text(): __is_parse_text.value = True
def enable_parse_trace_back(): __is_parse_trace_back.value = True
def enable_parse_signal_break_line(): __is_parse_signal_break_line.value = True

def disable_parse_log_type(): __is_parse_log_type.value = False
def disable_parse_date(): __is_parse_date.value = False
def disable_parse_time(): __is_parse_time.value = False
def disable_parse_process_id(): __is_parse_process_id.value = False
def disable_parse_thread_id(): __is_parse_thread_id.value = False
def disable_parse_cpu_usage(): __is_parse_cpu_usage.value = False
def disable_parse_memory_usage(): __is_parse_memory_usage.value = False
def disable_parse_file_name(): __is_parse_file_name.value = False
def disable_parse_file_lineno(): __is_parse_file_lineno.value = False
def disable_parse_text(): __is_parse_text.value = False
def disable_parse_trace_back(): __is_parse_trace_back.value = False
def disable_parse_signal_break_line(): __is_parse_signal_break_line.value = False

####################################################################################################################
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

def parse(log_dict:dict):
    log_formatter = get_log_formatter()
    
    result_dict = {}
    if LogDictKey.log_type in log_dict and __is_parse_log_type.value:
        result_dict[LogFormatterKey.log_type] = cut_tail_str(log_dict[LogDictKey.log_type], __log_type_max_length.value)
        result_dict[LogFormatterKey.log_type_max_length] = __log_type_max_length.value
    else:
        log_formatter = replace_formatter(log_formatter, get_log_type_formatter())
    
    if LogDictKey.timestamp in log_dict and __is_parse_date.value:
        result_dict[LogFormatterKey.date] = datetime.fromtimestamp(log_dict[LogDictKey.timestamp]).strftime(__date_formatter.value)
    else:
        log_formatter = replace_formatter(log_formatter, f"{{{LogFormatterKey.date}}}")
            
    if LogDictKey.timestamp in log_dict and __is_parse_time.value:
        result_dict[LogFormatterKey.time] = datetime.fromtimestamp(log_dict[LogDictKey.timestamp]).strftime(__time_formatter.value)
    else:
        log_formatter = replace_formatter(log_formatter, f"{{{LogFormatterKey.time}}}")
    
    if LogDictKey.process_id in log_dict and __is_parse_process_id.value:
        result_dict[LogFormatterKey.process_id] = cut_front_int(log_dict[LogDictKey.process_id], __process_id_max_length.value)
        result_dict[LogFormatterKey.process_id_max_length] = __process_id_max_length.value
    else:
        log_formatter = replace_formatter(log_formatter, get_process_id_formatter())
    
    if LogDictKey.thread_id in log_dict and __is_parse_thread_id.value:
        result_dict[LogFormatterKey.thread_id] = cut_front_int(log_dict[LogDictKey.thread_id], __thread_id_max_length.value)
        result_dict[LogFormatterKey.thread_id_max_length] = __thread_id_max_length.value
    else:
        log_formatter = replace_formatter(log_formatter, get_thread_id_formatter())
    
    if is_psutil and LogDictKey.cpu_usage in log_dict and __is_parse_cpu_usage.value:
        result_dict[LogFormatterKey.cpu_usage] = log_dict[LogDictKey.cpu_usage]
        result_dict[LogFormatterKey.cpu_usage_max_length] = __cpu_usage_max_length.value
    else:
        log_formatter = replace_formatter(log_formatter, get_cpu_usage_formatter())
    
    if is_psutil and LogDictKey.memory_usage in log_dict and __is_parse_memory_usage.value:
        result_dict[LogFormatterKey.memory_usage] = log_dict[LogDictKey.memory_usage]
        result_dict[LogFormatterKey.memory_usage_max_length] = __memory_usage_max_length.value
    else:
        log_formatter = replace_formatter(log_formatter, get_memory_usage_formatter())
    
    if LogDictKey.file_name in log_dict and __is_parse_file_name.value:
        file_name_len = len(log_dict[LogDictKey.file_name])
        if __file_name_length.value < file_name_len:
            if file_name_len < __file_name_max_length.value:
                __file_name_length.value = file_name_len
            else:
                __file_name_length.value = __file_name_max_length.value
        result_dict[LogFormatterKey.file_name] = log_dict[LogDictKey.file_name]
        result_dict[LogFormatterKey.file_name_length] = __file_name_length.value
    else:
        log_formatter = replace_formatter(log_formatter, get_file_name_formatter())
    
    
    if LogDictKey.file_lineno in log_dict and __is_parse_file_lineno.value:
        file_lineno_str_len = len(str(log_dict[LogDictKey.file_lineno]))
        if __file_lineno_length.value < file_lineno_str_len:
            if file_lineno_str_len < __file_lineno_max_length.value:
                __file_lineno_length.value = file_lineno_str_len
            else:
                __file_lineno_length.value = __file_lineno_max_length.value
        result_dict[LogFormatterKey.file_lineno] = log_dict[LogDictKey.file_lineno]
        result_dict[LogFormatterKey.file_lineno_length] = __file_lineno_length.value
    else:
        log_formatter = replace_formatter(log_formatter, get_file_lineno_formatter())
    
    
    if LogDictKey.text in log_dict and __is_parse_text.value:
        result_dict[LogFormatterKey.text] = log_dict[LogDictKey.text]
    else:
        log_formatter = replace_formatter(log_formatter, get_text_formatter())
    
    if LogDictKey.log_type in log_dict and LogDictKey.trace_back in log_dict and\
        log_dict[LogDictKey.log_type] == LogType.EXCEPTION and __is_parse_trace_back.value:
        log_formatter += f"\n{{{LogFormatterKey.trace_back}}}"
        result_dict[LogFormatterKey.trace_back] = log_dict[LogDictKey.trace_back]
    
    log_str = log_formatter.format(**result_dict)
    
    if LogDictKey.log_type in log_dict and log_dict[LogDictKey.log_type] == LogType.SIGNAL and __is_parse_signal_break_line.value:
        log_str = f"\n{log_str}" 
    
    return log_str

####################################################################################################################
####################################################################################################################
####################################################################################################################
####################################################################################################################
####################################################################################################################
# Main
def __logger_threading(logger_function):
    while True:
        log_dict = get()
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
    append_log_formatter(__text_formatter.value)

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
