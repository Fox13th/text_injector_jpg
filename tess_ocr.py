import logging
import os
from pathlib import Path

import cv2
import pytesseract
from pytesseract import Output
from tqdm import tqdm

from core import config

settings = config.get_settings()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('text_recognition.log'),
        logging.StreamHandler()
    ]
)


class TextRecognition:
    """
    Класс для распознавания текста на изображениях с использованием Tesseract-OCR.
    Поддерживает автоматическую коррекцию ориентации изображения.
    """

    def __init__(self, path_exe=None):
        """
        Инициализация класса.

        :param tesseract_path: Путь к исполняемому файлу Tesseract (если не указан, используется системный путь).
        """
        if path_exe:
            pytesseract.pytesseract.tesseract_cmd = path_exe
        logging.basicConfig(level=logging.INFO)

    def load_image(self, image_path):
        """
        Загружает изображение по указанному пути.

        :param image_path: Путь к изображению.
        :return: Загруженное изображение.
        :raises FileNotFoundError: Если изображение не найдено.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Файл {image_path} не найден или не может быть прочитан.")
        return image

    def rotate_image(self, image, angle):
        """
        Поворачивает изображение на заданный угол.

        :param image: Исходное изображение.
        :param angle: Угол поворота.
        :return: Повернутое изображение.
        """
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def correct_orientation(self, image):
        """
        Корректирует ориентацию изображения на основе анализа текста.

        :param image: Исходное изображение.
        :return: Изображение с корректной ориентацией.
        """
        osd = pytesseract.image_to_osd(image, output_type=Output.DICT)
        angle = osd["rotate"]
        if angle != 0:
            logging.info(f"Изображение повернуто на {angle} градусов. Выполняю поворот...")
            image = self.rotate_image(image, angle)
        logging.info(f'Угол наклона: {angle}\n')
        return image

    def recognize_text(self, image_path, lang_str, psm=None):
        """
        Распознает текст на изображении.

        :param image_path: Путь к изображению.
        :param lang_str: Язык для распознавания (по умолчанию 'eng').
        :param psm: Режим сегментации страницы (Page Segmentation Mode).
        :return: Распознанный текст.
        """
        try:
            image = self.load_image(image_path)
            image = self.correct_orientation(image)

            config_tess = ''
            if psm:
                config_tess += f'--psm {psm}'

            text = pytesseract.image_to_string(image, lang=lang_str, config=config_tess)
            return text
        except Exception as err:
            logging.error(f"Ошибка при распознавании текста: {err}")
            return None


def process_file(file_path, lang_dir):
    """Обрабатывает один файл: распознает текст и сохраняет результат."""
    try:
        recognizer = TextRecognition(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        recognized_text = recognizer.recognize_text(file_path, lang_dir, )

        if recognized_text is None:
            logging.warning(f"Не удалось распознать текст в файле: {file_path}")
            return

        out_sub_dir = os.path.join(settings.out_folder, lang_dir)
        Path(out_sub_dir).mkdir(parents=True, exist_ok=True)

        out_file_path = os.path.join(out_sub_dir, f'{file_path[:file_path.rfind(".")]}.txt')
        with open(out_file_path, 'w', encoding='utf-8') as f_write:
            f_write.write(recognized_text)
    except Exception as err:
        logging.error(f"Ошибка при обработке файла {file_path}: {err}")


def main():
    """Основная функция: обходит директории и обрабатывает файлы."""
    for root, dirs, files in os.walk(settings.input_dir):
        for file in tqdm(files, desc="Обработка файлов"):
            lang_dir = root[len(settings.input_dir) + 1:]
            if lang_dir == '':
                continue
            file_path = os.path.join(root, file)
            process_file(file_path, lang_dir)


if __name__ == '__main__':
    main()
