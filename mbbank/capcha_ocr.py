import io 
import re 
import pytesseract 
from PIL import Image 


class CapchaProcessing:
    """
    Base class for capcha processing for self implemented 
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
    Tesseract Capcha processing 

    Args:
        tesseract_path (str, optional): Path to Tesseract executable default is "tesseract"
    """

    def __init__(self, tesseract_path: str = None):
        if tesseract_path is not None:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path 

    
    def process_image(self, img: bytes) -> str:
        """
        Process image and return text 

        Args:
            img (bytes): image input as bytes 
        
        Returns:
            success (str): text from image
        """
        img_byte = io.BytesIO(img) 
        img = Image.open(img_byte) # read image from byte
        img = img.convert('RGBA') # convert to RGBA 
        pix = img.load() # get pixel data 
        for y in range(img.size[1]):
            for x in range(img.size[0]): # nếu bất kỳ giá tri RGB của pixel nào thấp hơn 102 (màu pixel khá tối) -> sẽ đổi thành màu đen, ngược lại là màu trắng
                if pix[x, y][0] < 102 or pix[x, y][1] < 102 or pix[x, y][2] < 102:
                    pix[x, y] = (0, 0, 0, 255)
                else:
                    pix[x, y] = (255, 255, 255, 255)
        text = pytesseract.image_to_string(img)
        text = re.sub(r"\s+", "", text, flags=re.MULTILINE)
        return text  
        

