from __future__ import print_function
from PIL import Image, ImageDraw, ImageFont, ImageColor
from io import BytesIO
import sys
import praw
import markov
import get_data
import requests


def check_length(image_width, text_string, font_size):
    if len(text_string) * font_size > image_width:
        return True
    return False


def split_text(image_width, text_string, font_size):
    final_strings = []
    str_len_in_pixels = 0
    substring = ""
    for char in text_string:
        str_len_in_pixels += font_size * 0.6
        substring += char
        if str_len_in_pixels > image_width:
            final_strings.append(substring)
            substring = ""
            str_len_in_pixels = 0
    if substring != "":
        final_strings.append(substring)
    return final_strings


def wrap_words(lines):
    pos = 0
    fixed_lines = lines
    for line in lines:
        if pos < len(lines) - 1 and line[-1] != " " and lines[pos + 1][
                0] != " ":
            words_line1 = lines[pos].split(" ")
            words_line2 = lines[pos + 1].split(" ")

            whole_word = words_line1[-1] + words_line2[0]
            words_line2[0] = whole_word

            del words_line1[-1]
            words_line1 = " ".join(words_line1)
            words_line2 = " ".join(words_line2)

            fixed_lines[pos] = words_line1
            fixed_lines[pos + 1] = words_line2
        pos += 1

    # print fixed_lines

    return fixed_lines


# -Create base image for meme text
# -Returns a 2-tuple whose first element is the image
#  and second element is the starting coordinate
#  of the meme picture


def get_base(meme_pic, text, font_size, padding):
    width = meme_pic.width
    split = split_text(width, text, font_size)
    height = (len(split) * font_size) + meme_pic.height
    return (Image.new('RGBA', (width + (2 * padding), height + (4 * padding)),
                      (255, 255, 255)),
            (padding, height - meme_pic.height + 15))


# make a transparent overlay for the meme text and draw the text on it
def draw_text(base, text_string, pos_x, pos_y, font_size):
    txt = Image.new('RGBA', base.size, (0, 0, 0, 0))
    fnt = ImageFont.truetype('Pillow/Tests/fonts/Arial.ttf', font_size)
    # get a drawing context
    d = ImageDraw.Draw(txt)

    if check_length(base.width, text_string, font_size):
        split = split_text(base.width, text_string, font_size)
        split = wrap_words(split)
        height_offset = 0
        for substring in split:
            d.text(
                (pos_x, pos_y + height_offset),
                substring,
                font=fnt,
                fill=(0, 0, 0, 255))
            height_offset += font_size

    else:
        d.text((pos_x, pos_y), text_string, font=fnt, fill=(0, 0, 0, 255))

    return Image.alpha_composite(base, txt)


def draw_meme_custom(pic, text):
    meme_pic = Image.open(pic).convert('RGBA')
    base = get_base(meme_pic, text, 20, 5)
    base_pic = base[0]
    coords = base[1]
    out = draw_text(base_pic, text, 10, 10, 20)
    # get a drawing context
    background = out
    foreground = meme_pic
    background.paste(foreground, coords, foreground)
    background.show()

    return background


def resize_image(image, baseheight):
    # wpercent = (basewidth / float(image.size[0]))
    # hsize = int((float(image.size[1]) * float(wpercent)))
    hpercent = (baseheight / float(image.size[1]))
    wsize = int((float(image.size[0]) * float(hpercent)))
    return image.resize((wsize, baseheight), Image.ANTIALIAS)


def draw_meme_random(titles_subreddit, images_subreddit):
    pic_url = get_data.choose_image("pics/%s_pics.txt" % (images_subreddit))
    if pic_url == 'error':
        print(
            "No data found\nUse python mem.py generate <subreddit-to-get-titles-from> <subreddit-to-get-images-from> to update\n"
        )
        return None
    response = requests.get(pic_url)
    meme_pic = Image.open(BytesIO(response.content)).convert('RGBA')
    meme_pic = resize_image(meme_pic, 500)

    markov_table = markov.generate_table(
        ["text/%s_titles.txt" % (titles_subreddit)])
    text = markov.generate_markov_text(15, 1, markov_table)[0].decode('utf-8')

    base = get_base(meme_pic, text, 20, 5)
    base_pic = base[0]
    coords = base[1]
    out = draw_text(base_pic, text, 10, 10, 20)
    # get a drawing context
    background = out
    foreground = meme_pic
    background.paste(foreground, coords, foreground)
    background.show()

    return background


def update_memes(titles_subreddit, images_subreddit):
    get_data.get_titles(titles_subreddit, 1000)
    get_data.get_images(images_subreddit, 1000)


args = sys.argv
if len(args) == 4:
    if args[1] == "generate":
        out = draw_meme_random(args[2], args[3])
        if out == None:
            exit(-1)
        ans = raw_input("Save this meme? [Y/N] ").lower()
        while (ans != 'y' and ans != 'n'):
            ans = raw_input("Save this meme? [Y/N] ")
        if ans == 'y':
            filename = raw_input("Filename: ")
            filename = 'out_pics/' + filename
            out.save(filename, "PNG")
            print("Saved %s.png" % (filename))
    elif args[1] == "update":
        update_memes(args[2], args[3])
    else:
        print(
            "Usage: \npython mem.py generate <subreddit-to-get-titles-from> <subreddit-to-get-images-from> \nOr\npython mem.py update subreddit"
        )
else:
    print(
        "Usage: \npython mem.py generate <subreddit-to-get-titles-from> <subreddit-to-get-images-from> \nOr\npython mem.py update subreddit"
    )
