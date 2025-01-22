import os.path
from pathlib import Path

from paddleocr import PaddleOCR
from core import config


settings = config.get_settings()


class OCRWork:
    def __init__(self, image_path: str, type_lang_symbols: str):
        self.image_path = image_path
        self.ocr = PaddleOCR(use_angle_cls=True, lang=type_lang_symbols)

    def get_text_from_image(self) -> str:
        result = self.ocr.ocr(self.image_path, cls=True)

        out_text = ''
        for line in result:
            for i, word_info in enumerate(line):
                out_text += word_info[1][0]
                if not i == len(line) - 1:
                    out_text += '\n'
        return out_text


def main():
    if not os.path.exists(settings.input_dir):
        print('Входной директории не существует!')
        return

    for root, dirs, files in os.walk(settings.input_dir):
        for file in files:
            lang_dir = root[len(settings.input_dir) + 1:]
            if lang_dir == '':
                continue

            res = OCRWork(os.path.join(root, file), lang_dir).get_text_from_image()

            out_sub_dir = os.path.join(settings.out_folder, lang_dir)
            Path(out_sub_dir).mkdir(parents=True, exist_ok=True)

            out_file_path = os.path.join(out_sub_dir, f'{file[:file.rfind(".")]}.txt')
            with open(out_file_path, 'w', encoding='utf-8') as f_write:
                f_write.write(res)


if __name__ == '__main__':
    main()
