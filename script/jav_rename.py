from io import BytesIO
from pathlib import Path

from PIL import Image
from mutagen.mp4 import MP4, MP4Cover

from lib.jav import jav_answer_me


def image_to_byte_array(image: Image) -> bytes:
    # BytesIO is a fake file stored in memory
    img_byte_io = BytesIO()
    # image.save expects a file as a argument, passing a bytes io ins
    image.save(img_byte_io, format=image.format)
    # Turn the BytesIO object back into a bytes object
    return img_byte_io.getvalue()


if __name__ == '__main__':

    recognizer = jav_answer_me.JavRecognizer()

    file_name = "NNPJ-426_副本.mp4"
    file_path = f"Z:/{file_name}"
    file_cover = f"Z:/NNPJ-426_cover.jpg"
    file = Path(file_path)

    res = recognizer.recognize("ipz001", True)

    video = MP4(file_path)  # A: Capture the file to edit
    video["\xa9ART"] = ["a1/a2/b1/c1"]
    video["covr"] = [
        MP4Cover(image_to_byte_array(res["thumbnail"]), imageformat=MP4Cover.FORMAT_JPEG),
    ]
    video.save()
