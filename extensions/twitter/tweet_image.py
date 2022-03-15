"""
This module just extends from github package.
repo: https://github.com/fedejordan/tweet-image-generator
"""
import os
from io import BytesIO, IOBase
import textwrap
import requests

import arabic_reshaper
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
from django.conf import settings
from logging import getLogger


logger = getLogger(__name__)


# Numbers
margin_x = 32
margin_y = 28
final_size = (1200, 2400)
twitter_name_x = 150
twitter_name_y = margin_y + 8

# Fonts
font_file = str(settings.TWEET_IMAGE_TEXT_FONT_PATH)
# font_file = "./fonts/Vazir-Medium-UI.ttf"
font_bold = str(settings.TWEET_IMAGE_TEXT_BOLD_FONT_PATH)
# font_bold = "./fonts/Vazir-Bold.ttf"
header_font_size = 32

# Colors
first_text_color = "white"
secondary_text_color = (136, 153, 166)
background_color = (21, 32, 43)
links_color = (27, 149, 224)


def get_width_for_text(text: str):
    text_font = ImageFont.truetype(font_file, 46)
    part_canvas = Image.new('RGB', (500, 100))
    part_draw = ImageDraw.Draw(part_canvas)
    part_draw.text((0, 0), text, font=text_font, fill='white')
    part_box = part_canvas.getbbox()
    return part_box[2]


def get_space_width():
    return get_width_for_text('a b') - get_width_for_text('ab')


def generate_white_image(source, destination):
    im = Image.open(source)
    im = im.convert('RGBA')

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    black_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 255)
    data[..., :-1][black_areas.T] = (255, 255, 255)  # Transpose back needed

    im2 = Image.fromarray(data)
    im2.save(destination)


def get_drawer_with_background():
    final_image = Image.new('RGB', final_size, color=background_color)
    return ImageDraw.Draw(final_image), final_image


def generate_twitter_name_and_get_width(drawer, twitter_name):
    text_font = ImageFont.truetype(font_bold, header_font_size)
    if settings.TWEET_IMAGE_TEXT_RESHAPE:
        twitter_name = get_display(arabic_reshaper.reshape(twitter_name))
    drawer.text((twitter_name_x, twitter_name_y), twitter_name, font=text_font, fill=first_text_color)
    return text_font.getsize(twitter_name)[0]


def generate_verified_image(final_image, is_verified, twitter_name_width):
    if is_verified:
        verified_image_x = twitter_name_x + twitter_name_width + 5
        verified_image_y = twitter_name_y
        verified_image_white_file = 'verified-white.png'
        generate_white_image('images/verified.png', verified_image_white_file)
        verified_image = Image.open(verified_image_white_file, 'r')
        verified_image_width = 40
        verified_image = verified_image.resize([verified_image_width, verified_image_width], Image.ANTIALIAS)
        final_image.paste(verified_image, (verified_image_x, verified_image_y), verified_image)
        os.remove('verified-white.png')


def generate_twitter_account(drawer, twitter_account):
    twitter_account_y = twitter_name_y + 38
    text_font = ImageFont.truetype(font_file, header_font_size)
    drawer.text((twitter_name_x, twitter_account_y), twitter_account, font=text_font, fill=secondary_text_color)


def is_valid_url(url):
    import re
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


def contains_url(text):
    for part in text.split(' '):
        if is_valid_url(part):
            return True
    return False


def generate_main_text_and_get_final_y(drawer, text, space_width):
    y_text_position = 151
    x_text_margin = margin_x
    text_lines_spacing = 10
    text_font = ImageFont.truetype(font_file, 46)
    text = text.replace('\n', ' ').replace('\r', ' ')
    if settings.TWEET_IMAGE_TEXT_RESHAPE:
        text = get_display(arabic_reshaper.reshape(text))
        lines_wrapper = textwrap.wrap(text, width=54)[::-1]
    else:
        lines_wrapper = textwrap.wrap(text, width=54)

    for line in lines_wrapper:
        if '@' in line or '#' in line or contains_url(line):
            string_parts = line.split(' ')
            if not settings.TWEET_IMAGE_TEXT_RESHAPE:
                string_parts = string_parts[::-1]
            next_x = 0
            for index, part in enumerate(string_parts):
                if len(part) == 0:
                    continue
                if not settings.TWEET_IMAGE_TEXT_RESHAPE and (part[0] in ('@', '#') or is_valid_url(part)):
                    color = links_color
                elif part[0] in ('@', '#') or part[-1] in ('@', '#') or is_valid_url(part):
                    color = links_color
                else:
                    color = 'white'
                part_width = get_width_for_text(text=part)
                drawer.text((x_text_margin + next_x, y_text_position), part, font=text_font, fill=color)
                next_x += part_width + space_width
        else:
            drawer.text((x_text_margin, y_text_position), line, font=text_font, fill="white")
        y_text_position += text_font.getsize(line)[1] + text_lines_spacing
    return y_text_position


def generate_images_and_get_final_y(final_image, images, y_position):
    if images:
        y_position += 5
        image_url = images[0]
        width = final_size[0] - margin_x * 2
        height = int(float(width) * 0.67)
        tweet_image = get_image_from_url(image_url)
        aspect = tweet_image.size[0] / tweet_image.size[1]
        height = width / aspect
        tweet_image_size = (int(width), int(height))
        tweet_image = tweet_image.resize(tweet_image_size, Image.ANTIALIAS)
        mask_im = Image.new("L", tweet_image.size, 0)
        mask_draw = ImageDraw.Draw(mask_im)
        radius = 50
        mask_draw.ellipse((0, 0, radius, radius), fill=255)
        mask_draw.rectangle((radius / 2, 0, width - radius / 2, radius), fill=255)
        mask_draw.ellipse((width - radius, 0, width, radius), fill=255)
        mask_draw.rectangle((width - radius, radius / 2, width, height - radius / 2), fill=255)
        mask_draw.ellipse((width - radius, height - radius, width, height), fill=255)
        mask_draw.rectangle((width - radius / 2, height - radius, radius / 2, height), fill=255)
        mask_draw.ellipse((0, height - radius, radius, height), fill=255)
        mask_draw.rectangle((0, height - radius / 2, radius, radius / 2), fill=255)
        mask_draw.rectangle((radius, radius, width - radius, height - radius), fill=255)
        final_image.paste(tweet_image, (margin_x, y_position), mask_im)
        return y_position + height
    else:
        return y_position


def generate_date_and_get_final_y(drawer, date_text, y_text_position):
    date_y = y_text_position + 22
    text_font = ImageFont.truetype(font_file, 32)
    drawer.text((30, date_y), date_text, font=text_font, fill=secondary_text_color)
    return date_y


def get_image_from_url(image_url):
    content = requests.get(image_url).content
    bytes_io = BytesIO(content)
    bytes_io.seek(0)
    return Image.open(bytes_io, 'r')


def get_image_from_url_with_size(image_url, size):
    tweet_image = get_image_from_url(image_url)
    tweet_image_size = size
    tweet_image = tweet_image.resize(tweet_image_size, Image.ANTIALIAS)
    return tweet_image


def download_and_insert_image(final_image, image_url):
    tweet_image = get_image_from_url_with_size(image_url, (96, 96))
    h, w = tweet_image.size
    mask_im = Image.new("L", tweet_image.size, 0)
    mask_draw = ImageDraw.Draw(mask_im)
    mask_draw.ellipse((0, 0, w, h), fill=255)
    final_image.paste(tweet_image, (margin_x, margin_y), mask_im)


def crop_final_image(final_image, date_y):
    final_height = date_y + 50
    w, h = final_image.size
    return final_image.crop((0, 0, w, final_height))


def save_image(final_image, destination=None, image_format=None):
    if not destination:
        image = BytesIO()
        final_image.save(image, format=image_format or 'JPEG')
        return image.getvalue()
    elif isinstance(destination, BytesIO):
        final_image.save(destination, format=image_format or 'JPEG')
        return destination.getvalue()
    else:
        if image_format:
            final_image.save(destination, format=image_format)
        else:
            final_image.save(destination)
        with open(destination, 'rb') as f:
            return f.read()


def generate_tweet_image(name, username, text, time, date, device, image_url, is_verified, images, destination=None):
    space_width = get_space_width()
    drawer, final_image = get_drawer_with_background()
    twitter_name_width = generate_twitter_name_and_get_width(drawer, name)
    generate_verified_image(final_image, is_verified, twitter_name_width)
    generate_twitter_account(drawer, username)
    y_text_position = generate_main_text_and_get_final_y(drawer, text, space_width)
    images_y = generate_images_and_get_final_y(final_image, images, y_text_position)
    date_y = generate_date_and_get_final_y(drawer, f'{time} · {date} · {device}', images_y)
    download_and_insert_image(final_image, image_url)
    final_image = crop_final_image(final_image, date_y)
    return save_image(final_image, destination)
