import os
import re


def get_image_count(folder_path):
    """Belirtilen klasördeki görsel sayısını döndürür"""
    images_path = os.path.join(folder_path, "images")
    if os.path.exists(images_path):
        return len(os.listdir(images_path))
    return 0


def get_folder_name_from_text(text):
    """Metin içindeki klasör adını ayıklar (parantez içindeki sayıyı çıkarır)"""
    match = re.match(r"(.+?)\s+\(\d+\)", text)
    if match:
        return match.group(1)
    return text


def get_number_from_text(text):
    """Metin içindeki parantez içindeki sayıyı döndürür"""
    match = re.search(r"\((\d+)\)", text)
    if match:
        return int(match.group(1))
    return 0 