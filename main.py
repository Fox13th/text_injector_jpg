import os.path
from pathlib import Path

from paddleocr import PaddleOCR
from core import config


settings = config.get_settings()


class OCRWork:
    def __init__(self, image_path: str, main_lang_symbols: str, addition_lang_symbols: str = None):
        self.image_path = image_path

        self.main_lang_symbols = main_lang_symbols
        self.addition_lang_symbols = addition_lang_symbols

        self.ocr_main = PaddleOCR(use_angle_cls=True, lang=main_lang_symbols)
        if addition_lang_symbols:
            self.ocr_addion = PaddleOCR(use_angle_cls=True, lang=addition_lang_symbols)

    def get_text_from_image(self) -> str:
        result_main = self.ocr_main.ocr(self.image_path, cls=True)
        if self.addition_lang_symbols:
            result_addition = self.ocr_addion.ocr(self.image_path, cls=True)

        combined_result = []

        for line in result_main[0]:
            combined_result.append({
                'text': line[1][0],
                'position': line[0],
                'language': self.main_lang_symbols,
                'confidence': line[1][1]
            })

        if self.addition_lang_symbols:
            for line in result_addition[0]:
                combined_result.append({
                    'text': line[1][0],
                    'position': line[0],
                    'language': self.addition_lang_symbols,
                    'confidence': line[1][1]
                })

        combined_result.sort(key=lambda x: x['position'][0][1])

        out_text = ''
        for i, line in enumerate(combined_result):
            print(f"Язык: {line['language']}, Текст: {line['text']}, Уверенность: {line['confidence']}, Позиция {line['position']}")
            out_text += line['text']  # word_info#[1][0]
            if not i == len(combined_result) - 1:
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

            res = OCRWork(os.path.join(root, file), 'ru', ).get_text_from_image()

            print(res)

            out_sub_dir = os.path.join(settings.out_folder, lang_dir)
            Path(out_sub_dir).mkdir(parents=True, exist_ok=True)

            out_file_path = os.path.join(out_sub_dir, f'{file[:file.rfind(".")]}.txt')
            with open(out_file_path, 'w', encoding='utf-8') as f_write:
                f_write.write(res)


if __name__ == '__main__':
    main()
