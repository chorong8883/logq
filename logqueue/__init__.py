import threading
from datetime import datetime
import os
import inspect
import multiprocessing
import ctypes
import traceback


__log_queue = multiprocessing.Queue()

class LogType:
    infomation = "information"
    debug = "debug"
    exception = "exception"

class LogKey:
    date = "date"
    time = "time"
    process_id = 'process_id'
    thread_id = "thread_id"
    log_type = "log_type"
    file_info = "file_info"
    file_name = "file_name"
    file_lineno = "file_lineno"
    text = "text"
    traceback = "traceback"

class OptionKey:
    timestamp = "timestamp"
    process_id_length = 'process_id_length'
    thread_id_length = "thread_id_length"
    log_type_length = "log_type_length"
    file_name_length = "file_name_length"
    file_lineno_length = "file_lineno_length"


__log_format = multiprocessing.Value(ctypes.c_wchar_p, '')
'''
ex) f"{{{LogKey.date}}} {{{LogKey.time}}} {{{LogKey.process_id}}} {{{LogKey.thread_id}}} {{{LogKey.log_type}}} {{{LogKey.file_info}}} {{{LogKey.text}}}"
'''

__date_format = multiprocessing.Value(ctypes.c_wchar_p, '%Y-%m-%d')
__time_format = multiprocessing.Value(ctypes.c_wchar_p, '%H:%M:%S.%f')

__process_id_length = multiprocessing.Value(ctypes.c_int, 3)
__process_id_format = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.process_id}:0{{{OptionKey.process_id_length}}}d}}:PID")

__thread_id_length = multiprocessing.Value(ctypes.c_int, 7)
__thread_id_format = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.thread_id}:0{{{OptionKey.thread_id_length}}}d}}:TID")

__log_type_length = multiprocessing.Value(ctypes.c_int, 4)
__log_type_format = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.log_type}:{{{OptionKey.log_type_length}}}}}")

__file_name_length = multiprocessing.Value(ctypes.c_int, 4)
__file_name_max_length = multiprocessing.Value(ctypes.c_int, 11)
__file_name_format = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.file_name}:>{{{OptionKey.file_name_length}}}}}")
__file_lineno_length = multiprocessing.Value(ctypes.c_int, 1)
__file_lineno_max_length = multiprocessing.Value(ctypes.c_int, 4)
__file_lineno_format = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.file_lineno}:<{{{OptionKey.file_lineno_length}}}}}")

__file_info_format = multiprocessing.Value(ctypes.c_wchar_p, f"{{{LogKey.file_name}}}:{{{LogKey.file_lineno}}}")
    
def close():
    __log_queue.put_nowait(None)

def get():
    is_next = True
    data = None
    while is_next:
        data = __log_queue.get()
        if data and ('command' in data):
            is_next = True
            match data['command']:
                case 'change_date_format':
                    __date_format.value = data['format_str']
                case 'change_time_format':
                    __time_format.value = data['format_str']
                case 'change_log_format':
                    __log_format_list = []
                    for key in data['logKey']:
                        __log_format_list.append(f'{{{key}}}')
                    __log_format.value = ' '.join(__log_format_list)
                case 'change_process_id_format':
                    __process_id_format.value = data['format_str']
                case 'change_log_format':
                    __process_id_format.value = data['format_str']
                case 'change_thread_id_format':
                    __thread_id_format.value = data['format_str']
                case 'change_log_type_format':
                    __log_type_format.value = data['format_str']
                case 'change_file_info_format':
                    __file_info_format.value = data['format_str']
                case 'change_file_name_format':
                    __file_name_format.value = data['format_str']
                case 'change_file_lineno_format':
                    __file_lineno_format.value = data['format_str']
                case 'change_process_id_length':
                    __process_id_length.value = data['length']
                case 'change_thread_id_length':
                    __thread_id_length.value = data['length']
                case 'change_log_type_length':
                    __log_type_length.value = data['length']
                case 'change_file_name_max_space_length':
                    __file_name_max_length.value = data['length']
                case 'change_file_lineno_max_length':
                    __file_lineno_max_length.value = data['length']
                case _:
                    pass
        else:
            is_next = False
    return data
            
def empty() -> bool:
    return __log_queue.empty()

def change_log_format(*logKey:str):
    '''
    default:\n
    LogKey.date, LogKey.time, LogKey.process_id, LogKey.thread_id, LogKey.log_type, LogKey.file_info, LogKey.text\n
    '''
    __log_queue.put_nowait({
        'command' : 'change_log_format',
        'logKey' : logKey
    })
change_log_format(LogKey.date, LogKey.time, LogKey.process_id, LogKey.thread_id, LogKey.log_type, LogKey.file_info, LogKey.text)

def change_date_format(format_str:str):
    '''
    default: '%Y-%m-%d'
    '''
    __log_queue.put_nowait({
        'command' : 'change_date_format',
        'format_str' : format_str
    })
def change_time_format(format_str:str):
    '''
    default: '%H:%M:%S.%f'
    '''
    __log_queue.put_nowait({
        'command' : 'change_time_format',
        'format_str' : format_str
    })
def change_process_id_format(format_str:str):
    '''
    default:\n
    f"{{{LogKey.process_id}:0{{{OptionKey.process_id_length}}}d}}:PID"
    '''
    __log_queue.put_nowait({
        'command' : 'change_process_id_format',
        'format_str' : format_str
    })
def change_thread_id_format(format_str:str):
    '''
    default:\n
    f"{{{LogKey.thread_id}:0{{{OptionKey.thread_id_length}}}d}}:TID"
    '''
    __log_queue.put_nowait({
        'command' : 'change_thread_id_format',
        'format_str' : format_str
    })
def change_log_type_format(format_str:str):
    '''
    default:\n
    f"{{{LogKey.log_type}:{{{OptionKey.log_type_length}}}}}"
    '''
    __log_queue.put_nowait({
        'command' : 'change_log_type_format',
        'format_str' : format_str
    })
def change_file_info_format(format_str:str):
    '''
    default:\n
    f"{{{LogKey.file_name}}}:{{{LogKey.file_lineno}}}"
    '''
    __log_queue.put_nowait({
        'command' : 'change_file_info_format',
        'format_str' : format_str
    })
def change_file_name_format(format_str:str):
    '''
    default:\n
    f"{{{LogKey.file_name}:>{{{OptionKey.file_name_length}}}}}"
    '''
    __log_queue.put_nowait({
        'command' : 'change_file_name_format',
        'format_str' : format_str
    })
def change_file_lineno_format(format_str:str):
    '''
    default:\n
    f"{{{LogKey.file_lineno}:<{{{OptionKey.file_lineno_length}}}}}"
    '''
    __log_queue.put_nowait({
        'command' : 'change_file_lineno_format',
        'format_str' : format_str
    })

def change_process_id_length(length:int):
    __log_queue.put_nowait({
        'command' : 'change_process_id_length',
        'length' : length
    })
def change_thread_id_length(length:int):
    __log_queue.put_nowait({
        'command' : 'change_thread_id_length',
        'length' : length
    })
def change_log_type_length(length:int):
    __log_queue.put_nowait({
        'command' : 'change_log_type_length',
        'length' : length
    })
def change_file_name_max_space_length(length:int):
    __log_queue.put_nowait({
        'command' : 'change_file_name_max_space_length',
        'length' : length
    })
def change_file_lineno_max_length(length:int):
    '''
    set length of file lineno.\n
    auto increase if lineno length larger than current length.\n
    ex)\n
    length = 2\n
    39 log\n
    length = 4\n
    39   log\n
    f"{{{LogKey.file_lineno}:<{{{OptionKey.file_lineno_length}}}}}"
    '''
    __log_queue.put_nowait({
        'command' : 'change_file_lineno_max_length',
        'length' : length
    })
    
def parse_date(timestamp:float) -> str:
    return datetime.fromtimestamp(timestamp).strftime(__date_format.value)
def parse_time(timestamp:float) -> str:
    return datetime.fromtimestamp(timestamp).strftime(__time_format.value)
def parse_process_id(pid:int, length:int) -> str:
    return __process_id_format.value.format(**{LogKey.process_id:pid, OptionKey.process_id_length:length})
def parse_thread_id(tid:int, length:int) -> str:
    return __thread_id_format.value.format(**{LogKey.thread_id:tid, OptionKey.thread_id_length:length})
def parse_log_type(log_type:str, length:int) -> str:
    if length < len(log_type):
        log_type = log_type[:length]
    return __log_type_format.value.format(**{LogKey.log_type:log_type, OptionKey.log_type_length:length})
def parse_file_info(file_name:str, file_name_length:int, file_lineno:int, file_lineno_length:int) -> str:
    file_name = parse_file_name(file_name, file_name_length)
    file_lineno = parse_file_lineno(file_lineno, file_lineno_length)
    return __file_info_format.value.format(**{LogKey.file_name:file_name, LogKey.file_lineno:file_lineno})
def parse_file_name(file_name:str, length:int) -> str:
    return __file_name_format.value.format(**{LogKey.file_name:file_name, OptionKey.file_name_length:length})
def parse_file_lineno(file_lineno:str, length:int) -> str:
    return __file_lineno_format.value.format(**{LogKey.file_lineno:file_lineno, OptionKey.file_lineno_length:length})


def __get_blank_log_dict():
    return {
        OptionKey.timestamp : 0.0,
        LogKey.process_id : 0,
        LogKey.thread_id : 0,
        LogKey.log_type : "",
        LogKey.file_name : "",
        LogKey.file_lineno : "",
        LogKey.text : ""
    }   

def __get_log_dict(log_type:str, *objs:object, **kwargs) -> dict:
    frame_stack = inspect.stack()
    caller_frame = frame_stack[2]
    caller_file_lineno = caller_frame.lineno
    splitted_caller_file_name = caller_frame.filename.split('/')
    caller_file_name = splitted_caller_file_name[-1]
    if caller_file_name == '__init__.py':
        caller_file_name = '/'.join(splitted_caller_file_name[-2:])
    
    result = __get_blank_log_dict()
    result[OptionKey.timestamp] = datetime.now().timestamp()
    result[LogKey.process_id] = os.getpid()
    result[LogKey.thread_id] = threading.current_thread().ident
    result[LogKey.log_type] = log_type
    result[LogKey.file_name] = caller_file_name
    result[LogKey.file_lineno] = caller_file_lineno
    temp_text_list = []
    for obj in objs:
        temp_text_list.append(str(obj))
    result[LogKey.text] = ' '.join(temp_text_list)
    if log_type == LogType.exception:
        result[LogKey.traceback] = traceback.format_exc()
    if kwargs:
        result.update(**kwargs)
    return result

def etc(log_type:str, *objs:object, **kwargs):
    log_dict = __get_log_dict(log_type, *objs, **kwargs)
    __log_queue.put_nowait(log_dict)
def info(*objs:object, **kwargs):
    log_dict = __get_log_dict(LogType.infomation, *objs, **kwargs)
    __log_queue.put_nowait(log_dict)
def debug(*objs:object, **kwargs):
    log_dict = __get_log_dict(LogType.debug, *objs, **kwargs)
    __log_queue.put_nowait(log_dict)
def exception(*objs:object, **kwargs):
    log_dict = __get_log_dict(LogType.exception, *objs, **kwargs)
    __log_queue.put_nowait(log_dict)


def parse(log_dict:dict) -> str:
    log_format = __log_format.value
    if OptionKey.timestamp in log_dict:
        log_dict[LogKey.date] = parse_date(log_dict[OptionKey.timestamp])
        log_dict[LogKey.time] = parse_time(log_dict[OptionKey.timestamp])
    
    if LogKey.process_id in log_dict:
        process_id = log_dict[LogKey.process_id]
        if __process_id_length.value < len(str(process_id)):
            pid = process_id%(10**__process_id_length.value)
            log_dict[LogKey.process_id] = parse_process_id(pid, __process_id_length.value)
        else:
            __process_id_length.value = len(str(process_id))
            log_dict[LogKey.process_id] = parse_process_id(process_id, __process_id_length.value)
        
    if LogKey.thread_id in log_dict:
        thread_id = log_dict[LogKey.thread_id]
        if __thread_id_length.value < len(str(thread_id)):
            tid = thread_id%(10**__thread_id_length.value)
            log_dict[LogKey.thread_id] = parse_thread_id(tid, __thread_id_length.value)
        else:
            __thread_id_length.value = len(str(thread_id))
            log_dict[LogKey.thread_id] = parse_thread_id(thread_id, __thread_id_length.value)
        
    if LogKey.log_type in log_dict:
        log_dict[LogKey.log_type] = parse_log_type(log_dict[LogKey.log_type], __log_type_length.value)
        
    if LogKey.file_name in log_dict and LogKey.file_lineno in log_dict:
        if __file_name_length.value < len(log_dict[LogKey.file_name]):
            if __file_name_max_length.value < len(log_dict[LogKey.file_name]):
                __file_name_length.value = __file_name_max_length.value
            else:
                __file_name_length.value = len(log_dict[LogKey.file_name])
                
        if __file_lineno_length.value < len(str(log_dict[LogKey.file_lineno])):
            if __file_lineno_max_length.value < len(str(log_dict[LogKey.file_lineno])):
                __file_lineno_length.value = __file_lineno_max_length.value
            else:
                __file_lineno_length.value = len(str(log_dict[LogKey.file_lineno]))
        
        log_dict[LogKey.file_info] = parse_file_info(log_dict[LogKey.file_name], __file_name_length.value, log_dict[LogKey.file_lineno], __file_lineno_length.value)
    
    if LogKey.traceback in log_dict:
        log_dict[LogKey.text] += '\n' + log_dict[LogKey.traceback]
    
    return log_format.format(**log_dict)

def test():
    info("aa", "a")