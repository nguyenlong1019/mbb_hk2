import dataclasses 
import json 
import struct 
import wasmtime 


class Memory:
    def __init__(self, store_wasm, mem: wasmtime.Memory):
        self.store_wasm = store_wasm 
        self.mem = mem 
        self.wasm_page_size = 65536 

    
    def read(self, start_address, end_address):
        return self.mem.read(self.store_wasm, start_address, end_address)
    

    def write(self, value, start_address):
        need = start_address + len(value)
        if self.mem.size(self.store_wasm) * self.wasm_page_size < need:
            print("need", need, "size", self.mem.size(self.store_wasm) * self.wasm_page_size)
            if self.wasm_page_size > need:
                grow_page = 1
            else:
                grow_page = int(need / self.wasm_page_size)
                if grow_page > int(grow_page):
                    grow_page += 1 
            self.mem.grow(self.store_wasm, int(grow_page))
        return self.mem.write(self.store_wasm, value, start_address) 
    

    def getBigInt64(self, address, littleEndian = False):
        data = self.read(address, address + 8)
        if littleEndian:
            value, = struct.unpack('<q', data)
        else:
            value, = struct.unpack('>q', data)
        return value 
    

    def getBigUint64(self, address, littleEndian = False):
        data = self.read(address, address + 8)
        if littleEndian:
            value, = struct.unpack('<Q', data)
        else:
            value, = struct.unpack('>Q', data)
        return value 
    

    def getFloat16(self, address, littleEndian = False):
        data = self.read(address, address + 2)
        value, = struct.unpack('<e', data)
        return value 
    

    def getFloat32(self, address, littleEndian = False):
        data = self.read(address, address + 4)
        if littleEndian:
            value, = struct.unpack('<f', data)
        else:
            value, = struct.unpack('>f', data)
        return value 
    

    def getFloat64(self, address, littleEndian = False):
        data = self.read(address, address + 8)
        if littleEndian:
            value, = struct.unpack('<d', data)
        else:
            value, = struct.unpack('>d', data)
        return value 
    

    def getInt16(self, address, littleEndian = False):
        data = self.read(address, address + 2)
        if littleEndian:
            value, = struct.unpack('<h', data)
        else:
            value, = struct.unpack('>h', data)
        return value 
    

    def getInt32(self, address, littleEndian = False):
        data = self.read(address, address + 4)
        if littleEndian:
            value, = struct.unpack('<i', data)
        else:
            value, = struct.unpack('>i', data)
        return value 
    

    def getInt8(self, address, littleEndian = False):
        data = self.read(address, address + 1)
        value, = struct.unpack('b', data)
        return value 
    

    def getUint16(self, address, littleEndian = False):
        data = self.read(address, address + 2)
        if littleEndian:
            value, = struct.unpack('<H', data)
        else:
            value, = struct.unpack('>H', data)
        return value 
    

    def getUint32(self, address, littleEndian = False):
        data = self.read(address, address + 4)
        if littleEndian:
            value, = struct.unpack('<I', data)
        else:
            value, = struct.unpack('>I', data)
        return value 
    

    def getUint8(self, address, littleEndian = False):
        data = self.read(address, address + 1)
        value, = struct.unpack('B', data)
        return value 
    

    def setBigInt64(self, address, value, littleEndian = False):
        pass 


    def setBigUint64(self, address, value, littleEndian = False):
        pass 


    def setFloat16(self, address, value, littleEndian = False):
        pass 


    def setFloat32(self, address, value, littleEndian = False):
        pass 


    def setFloat64(self, address, value, littleEndian = False):
        pass 


    def setInt16(self, address, value, littleEndian = False):
        pass 


    def setInt32(self, address, value, littleEndian = False):
        pass


    def setInt8(self, address, value, littleEndian = False):
        pass 


    def setUint16(self, address, value, littleEndian = False):
        pass 


    def setUint32(self, address, value, littleEndian = False):
        pass 


    def setUint8(self, address, value, littleEndian = False):
        pass
