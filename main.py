from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='latin')

image_path = './test/3.jpg'

result = ocr.ocr(image_path, cls=True)

for line in result:
    for word_info in line:
        print(word_info[1][0])
