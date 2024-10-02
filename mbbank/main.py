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
    'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm', 
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
    deviceIdCommon = f't2ztvkhd-mbib-0000-0000-{get_now_time()}'  
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
            headers.update(headers_default)
            headers["X-Request-Id"] = rid 
            headers["RefNo"] = rid 
            headers["DeviceId"] = self.deviceIdCommon 
            
            with requests.Session() as s:
                with s.post(url, headers=headers, json=json_data, proxies=self.proxy) as r:
                    data_out = r.json()

                if data_out["result"] is None:
                    self.getBalance()
                elif data_out["result"]["ok"]:
                    data_out.pop("result", None)
                    break 
                elif data_out["result"]["responseCode"] == "GW200":
                    self._authenticate()
                else:
                    err_out = data_out["result"]
                    raise MBBankError(err_out)
        return data_out 

    
    def _get_wasm_file(self):
        if self.__wasm_cache is not None:
            return self.__wasm_cache 
        file_data = requests.get("https://online.mbbank.com.vn/assets/wasm/main.wasm", headers=headers_default, proxies=self.proxy).content 
        self.__wasm_cache = file_data 
        return file_data 


    def _authenticate(self):
        while True:
            self._userinfo = None 
            self.sessionId = None 
            self._temp = {}
            rid = f"{self.__userid}-{get_now_time()}"
            json_data = {
                'sessionId': "",
                'refNo': rid,
                'deviceIdCommon': self.deviceIdCommon,
            }
            headers = headers_default.copy()
            headers["X-Request-Id"] = rid 
            with requests.Session() as s:
                with s.post("https://online.mbbank.com.vn/retail-web-internetbankingms/getCaptchaImage", headers=headers, json=json_data, proxies=self.proxy) as r:
                    data_out = r.json()
            img_bytes = base64.b64decode(data_out["imageString"])
            text = self.ocr_class.process_image(img_bytes)
            payload = {
                "userId": self.__userid,
                "password": hashlib.md5(self.__password.encode()).hexdigest(),
                "captcha": text,
                "sessionId": "",
                "refNo": f"{self.__userid}-{get_now_time()}",
                "deviceIdCommon": self.deviceIdCommon,
                "ibAuthen2faString": self.FPR,
            }
            wasm_bytes = self._get_wasm_file()
            dateEnc = None 


    def getTransactionAccountHistory(self):
        pass 


    def getBalance(self):
        pass 


    def getBalanceLoyalty(self):
        pass 


    def getInterestRate(self, currency: str = "VND"):
        pass 


    
