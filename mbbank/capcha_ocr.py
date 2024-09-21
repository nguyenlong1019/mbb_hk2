import io 
import re 
import pytesseract 
from PIL import Image 


class CapchaProcessing:
    """
    
    """
    
    def __init__(self):
        return 
    

    def process_image(self, img: bytes) -> str:
        """
        Process image and return text 

        Args:
            img (bytes): image input as bytes 

        Returns:
            success (str): text from image 
        """
        raise NotImplementedError("process_image is not implemented")


class TesseractOCR(CapchaProcessing):
    """
    
    """

    def __init__(self, tesseract_path: str = None):
        if tesseract_path is not None:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path 

    
    def process_image(self, img: bytes) -> str:
        """
        
        """
        img_byte = io.BytesIO(img) 
        img = Image.open(img_byte) # read image from byte
        img = img.convert('RGBA') # convert to RGBA 
        pix = img.load() # get pixel data 
        

