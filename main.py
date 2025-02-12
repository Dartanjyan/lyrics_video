import re
import os

from moviepy import ImageClip, ColorClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont


def parse_script(script_path):
    scenes = []
    with open(script_path, "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(r"(\d+:\d+)-(\d+:\d+) ?(.*)", line.strip())
            if match:
                start, end, content = match.groups()
                start_time = sum(int(x) * 60 ** i for i, x in enumerate(reversed(start.split(':'))))
                end_time = sum(int(x) * 60 ** i for i, x in enumerate(reversed(end.split(':'))))
                image_path, text = None, content

                img_match = re.match(r"\\i (.*?) \\t (.*)", content)
                if img_match:
                    image_path, text = img_match.groups()

                scenes.append({
                    "start": start_time,
                    "end": end_time,
                    "duration": end_time - start_time,
                    "image": image_path,
                    "text": text.strip()
                })
    return scenes


def create_text_image(text, width=1280, height=720, font_size=40):
    font = ImageFont.truetype("arial.ttf", font_size)
    image = Image.new("RGBA", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    text_width, text_height = draw.textsize(text, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Белый контур
    outline_range = 2
    for dx in range(-outline_range, outline_range + 1):
        for dy in range(-outline_range, outline_range + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=(255, 255, 255))

    # Чёрный текст
    draw.text((x, y), text, font=font, fill=(0, 0, 0))

    img_path = "temp_text.png"
    image.save(img_path)
    return img_path


def create_video(scenes, audio_path, output_path):
    clips = []
    for scene in scenes:
        if scene["image"]:
            img_clip = ImageClip(scene["image"]).set_duration(scene["duration"])
        else:
            img_clip = ColorClip((1280, 720), (0, 0, 0)).set_duration(scene["duration"])

        if scene["text"]:
            text_img_path = create_text_image(scene["text"])
            text_clip = ImageClip(text_img_path).set_duration(scene["duration"]).set_position("center")
            img_clip = CompositeVideoClip([img_clip, text_clip])

        clips.append(img_clip)

    final_video = concatenate_videoclips(clips).set_audio(AudioFileClip(audio_path))
    final_video.write_videofile(output_path, fps=24, codec='libx264')


# Пример использования
script_file = "script.txt"
audio_file = "Black November.mp3"
output_video = "output.mp4"

scenes_data = parse_script(script_file)
create_video(scenes_data, audio_file, output_video)
