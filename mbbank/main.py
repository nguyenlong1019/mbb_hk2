import datetime 
import base64 
import hashlib 
import typing 
import platform 
import requests 
from .capcha_ocr import TesseractOCR, CapchaProcessing 


headers_default = {
    'Cache-Control': 'no-cache',
    'Accept': 'application/json, text/plain, */*',
    'App': 'MB_WEB',
    'Authorization': 'Basic ', ######################################################
    'User-Agent': f'Mozilla/5.0 (X11; {platform.system()} {platform.processor()})',
    'Origin': 'https://online.mbbank.com.vn',
    'Referer': 'https://online.mbbank.com.vn/',
}


def get_now_time():
    now = datetime.datetime.now() 
    microsecond = int(now.strftime("%f")[:2]) 
    return now.strftime(f"%Y%m%d%H%M{microsecond}")


class MBBankError(Exception):
    def __init__(self, err_out):
        self.code = err_out['responseCode']
        self.message = err_out['message'] 
        super().__init__(f"{err_out['responseCode']} | {err_out['message']}") 


class MBBank:
    """ Core Class

    Attributes:
        deviceIdCommon (str): Device id common 
        sessionId (str or None): Current session id 

    Args:
        username (str): MBBank Account Username 
        password (str): MBBank Account Password 
        proxy (str, optional): Proxy url. Example: "http://127.0.0.1:8000". Default to None. 
        ocr_class (CapchaProcessing, optional): CapchaProcessing class. Default to TesseractOCR().

    """
    deviceIdCommon = f'' ############################################# 
    FPR = 'dd368a67ac24179dc33bdb3271ee08c0'  # FingerPrint using MD5


    def __init__(self, *, username, password, proxy=None, ocr_class=None):
        self.__userid = username 
        self.__password = password 
        self.__wasm_cache = None 
        
        if proxy is not None:
            proxy_protocol = proxy.split("://")[0]
            self.proxy = {proxy_protocol: proxy}
        else:
            self.proxy = {}

        self.ocr_class = TesseractOCR()  
        if ocr_class is not None:
            if not isinstance(ocr_class, CapchaProcessing):
                raise ValueError("ocr_class must be instance of CapchaProcessing") 
            self.ocr_class = ocr_class 
        
        self.sessionId = None 
        self._userinfo = None 
        self._temp = {}


    def _req(self, url, *, json=None, headers=None):
        if headers is None:
            headers = {}

        if json is None:
            json = {}

        while True: 
            if self.sessionId is None:
                self._authenticate()
            rid = f"{self.__userid}-{get_now_time()}" 
            json_data = {
                'sessionId': self.sessionId if self.sessionId is not None else "",
                'refNo': rid, 
                'deviceIdCommon': self.deviceIdCommon,
            }
            json_data.update(json) 

            # line 82 

    
    def _get_wasm_file(self):
        pass 


    def _authenticate(self):
        pass 


    def getTransactionAccountHistory(self):
        pass 


    def getBalance(self):
        pass 


    def getBalanceLoyalty(self):
        pass 


    def getInterestRate(self, currency: str = "VND"):
        pass 


    
