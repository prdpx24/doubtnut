import os
import string
import random
from urllib.request import urlopen


import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


def generate_random_string(length=8):
    return "".join([random.choice(string.ascii_letters) for _ in range(length)])


def extract_text_from_image(image_filepath):
    # generic utility to extract text from any image file_path - local and remote both
    try:
        if "http" in image_filepath:
            image_name = image_filepath.split("/")[-1]
            downloaded_image_path = (
                "/tmp/" + generate_random_string(length=10) + image_name
            )
            with open(downloaded_image_path, "wb") as dl_img:
                dl_img.write(urlopen(image_filepath).read())
        else:
            downloaded_image_path = None

        image_file = downloaded_image_path or image_filepath

        # source: https://stackoverflow.com/a/37750605
        im = Image.open(image_file)
        im = im.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(2)
        im = im.convert("1")
        random_temp_img_filepath = "/tmp/" + generate_random_string(10) + ".jpg"
        im.save(random_temp_img_filepath)
        # text = pytesseract.image_to_string(Image.open(random_temp_img_filepath))
        text = pytesseract.image_to_string(
            Image.open(random_temp_img_filepath),
            config="-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz -psm 6",
            lang="eng",
        )
        text = text.lower()
        try:
            os.remove(random_temp_img_filepath)
            if downloaded_image_path:
                os.remove(downloaded_image_path)
        except Exception as e:
            print("**exception in cleaning up /tmp/ images **")
            print(e)
        return text
    except Exception as e:
        print("** exception in extract_text_from_image")
        print(e)


def bisect_extracted_question(text):
    lines = text.splitlines()
    if len(lines) == 1:
        return text, None
    else:
        title = lines[0]
        description = "\n".join(lines[1:])
        return title, description
