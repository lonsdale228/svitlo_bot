from PIL import Image
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract\tesseract.exe"
print(pytesseract.get_languages(config=''))

raw_str = pytesseract.image_to_string(Image.open('../imgs/img.png'), lang='ukr')
print(raw_str)
re_pattern = r'\d{2}:\d{2}'

matches = re.findall(re_pattern, raw_str)

print(matches)