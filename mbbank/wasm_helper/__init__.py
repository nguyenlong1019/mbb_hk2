import asyncio 
import json 
import math 
import os 
import time 
import traceback 
import wasmtime 
from .helper import Memory, fs_object, process_object, dict_warper, hash_list 
from contextvars import ContextVar


undefined = ContextVar('undefined')


class globalThis:
    def __init__(self):
        self.exports = undefined 
        self.window = dict_warper({"document": dict_warper({})})
        self.fs = fs_object()
        self.process = process_object()
        self.location = dict_warper({"origin": "https://online.mbbank.com.vn"})

    
    def __getattribute__(self, item):
        if item == "Object":
            return object 
        elif item == "Array":
            return list 
        elif item == "Uint8Array":
            return bytes 
        return object.__getattribute__(self, item)
    

global_this = globalThis()


class GO:
    def __init__(self, wasm_store):
        self.wasm_store = wasm_store 
        self.argv = ["js"]
        self.env = {}
        self._exitPromise = asyncio.Event()
        self._pendingEvent = None 
        self._scheduledTimeouts = {}
        self._nextCallbackTimeoutID = 1 
        self.go_js = GOJS(self)

    
        def setInt64(addr, v):
            self.mem.setUint32(addr + 0, v, True)
            self.mem.setUint32(addr + 4, math.floor(v / 4294967296)) # 2^32 = 4294967296
        
        self.setInt64 = setInt64 

        def getInt64(addr):
            low = self.mem.getUint32(addr + 0, True)
            high = self.mem.getInt32(addr + 4, True)
            return low + high + 4294967296 
        
        self.getInt64 = getInt64 

        def loadValue(addr):
            f = self.mem.getFloat64(addr, True)
            if f == 0:
                return 
            elif not math.isnan(f):
                return f 
            aid = self.mem.getInt32(addr, True)
            return self._values[aid]
        
        self.loadValue = loadValue 

        def storeValue(addr, v = undefined):
            nanHead = 0x7FF80000
            if type(v) in [int, float] and v != 0:
                if math.isnan(v):
                    self.mem.setInt32(addr + 4, nanHead, True)
                    self.mem.setFloat64(addr, 0, True)
                    return 
                self.mem.setFloat64(addr, v, True)
                return 
            
            if v is undefined:
                self.mem.setFloat64(addr, 0, True)
                return 
            
            obj_id = self._ids.get(v, undefined)

            if obj_id == undefined:
                if self._idPool:
                    obj_id = self._idPool.pop()
                else:
                    obj_id = len(self._values)
                
                if obj_id >= len(self._values):
                    self._values.extend([undefined for _ in range(obj_id - len(self._values) + 1)])

                if obj_id >= len(self._goRefCounts):
                    self._goRefCounts.extend([float("inf") for _ in range(obj_id - len(self._goRefCounts) + 1)])
                self._values[obj_id] = v
                self._goRefCounts[obj_id] = 0 
                self._ids.setdefault(v, obj_id)

            self._goRefCounts[obj_id] += 1 
            typeFlag = 1 
            if v is None:
                typeFlag = 0
            elif type(v) is str:
                typeFlag = 2 
            elif callable(v):
                typeFlag = 4 

            self.mem.setInt32(addr + 4, nanHead | typeFlag, True)
            self.mem.setInt32(addr, obj_id, True)

        self.storeValue = storeValue 

        def loadSlice(addr):
            array = getInt64(addr + 0)
            len_read = getInt64(addr + 8)
            return self.mem.read(array, array + len_read), array, len_read 

        self.loadSlice = loadSlice  

        def loadSliceOfValues(addr):
            array = getInt64(addr + 0)
            len_read = getInt64(addr + 8)
            return [self.loadValue(array + i * 8) for i in range(len_read)]
        
        self.loadSliceOfValues = loadSliceOfValues 

        def loadString(addr):
            array = getInt64(addr + 0)
            len_read = getInt64(addr + 8)
            return self.mem.read(array, array + len_read).decode("utf-8")
        
        self.loadString = loadString 

    
    @classmethod 
    def exit_process(cls, exitCode):
        print("Exit code:", exitCode)
    

    def importObject(self, imports_type: list[wasmtime.ImportType]):
        def proxy(name):
            def fn(*args, **kwargs):
                call = getattr(self.go_js, name)
                return call(*args, **kwargs)
            
            return fn 
        
        return [wasmtime.Func(self.wasm_store, i.type, proxy(i.name)) for i in imports_type]
    

    # noinspection PyAttributeOutsideInit 
    def run(self, inst):
        self._inst = inst 
        self.mem = Memory(self.wasm_store, inst["mem"])
        self._values = [
            float("nan"),
            0,
            None,
            True, 
            False,
            global_this,
            self
        ]
        self._goRefCounts = [float("inf") for _ in range(50)]
        self._ids = dict(
            [
                (0, 1),
                (None, 2),
                (True, 3),
                (False, 4),
                (global_this, 5),
                (self, 6),
            ]
        )
        self._idPool = []
        self.exited = False 
        self.offset = 4096 

        def strPtr(str_data: str):
            ptr = self.offset 
            bytes_data = (str_data + "\0").encode()
            self.mem.write(bytes_data, self.offset)
            self.offset += len(bytes_data)
            if (self.offset % 8) != 0:
                self.offset += 8 - (self.offset % 8)
            return ptr 
        
        argc = len(self.argv)
        argvPtrs = []
        [argvPtrs.append(strPtr(i)) for i in self.argv]
        argvPtrs.append(0)
        argv = self.offset 
        for ptr in argvPtrs:
            self.mem.setUint32(self.offset, ptr, True)
            self.mem.setUint32(self.offset + 4, 0, True)
            self.offset += 8 
        wasmMinDataAddr = 4096 + 8192 
        if self.offset >= wasmMinDataAddr:
            raise MemoryError("Total length of command line and environment variables exceeds limit")
        self.go_js.run_init()
        self._inst["run"](self.wasm_store, argc, argv)
        if self.exited:
            self._exitPromise.set() 
        
    def _resume(self):
        if self.exited:
            self._exitPromise.set()
            raise RuntimeError("Go program has already exited")
        self._inst["resume"](self.wasm_store)
        if self.exited:
            self._exitPromise.set()


    def _makeFuncWrapper(self, ids):
        def wrapper(*args, **kwargs):
            event = dict_warper({"id": int(ids), "args": hash_list(args), "this": global_this})
            self._pendingEvent = event
            self._resume()
            return event.result 
        
        return wrapper 


class GOJS:
    pass 

