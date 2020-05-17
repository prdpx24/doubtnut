import os
import string
import random
import re
from urllib.request import urlopen


from fpdf import FPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


from .constants import TAG_ENGINE_KEYWORDS


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


def get_possible_tags_from_text(text):
    """
    dumb tag detector engine
    """
    tags = []

    for meta_tag in TAG_ENGINE_KEYWORDS.keys():
        possible_tags = TAG_ENGINE_KEYWORDS[meta_tag]
        for tag_key in possible_tags:
            for word in possible_tags[tag_key]:
                if word in text:
                    tags.append(tag_key)
                    break
    return list(set(tags))


def generate_pdf_document_from_catalog_questions(catalog_questions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt="Doubtnut", ln=2, align="C")
    for idx, catalog_question in enumerate(catalog_questions):
        title = catalog_question.question.title
        if title:
            pdf.cell(200, 10, txt=str(idx + 1) + "." + title, ln=idx + 1, align="L")
        description = catalog_question.question.description
        if description:
            pdf.set_text_color(0, 0, 255)
            pdf.cell(
                200,
                10,
                txt=description,
                ln=idx + 1,
                align="L",
                link=catalog_question.video_url,
            )
            pdf.set_text_color(0, 0, 0)
        # video_url = catalog_question.video_url
        # if video_url:
        #     # link = pdf.add_link(video_url)
        #     pdf.cell(
        #         200, 10, txt="Video", link=video_url, ln=idx + 1, align="L",
        #     )
        pdf.cell(200, 10, txt="\n", ln=1, align="L")

    output_filepath = (
        "/tmp/" + "generated_catalog_" + generate_random_string(length=10) + ".pdf"
    )
    pdf.output(output_filepath)
    return output_filepath
