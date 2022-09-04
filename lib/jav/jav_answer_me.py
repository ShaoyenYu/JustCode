import re
import time
from io import BytesIO
from typing import Dict, Optional

import requests
from PIL import Image
from lxml import etree


def parse_serial_no(serial_no) -> Optional[str]:
    patt = "(?<![a-zA-Z])([a-zA-Z]{3,6})-?(\d{3,10})"
    if (matched := re.search(patt, serial_no)) is not None:
        serial_no_alpha, serial_no_num = matched.groups()
        return "-".join((serial_no_alpha, serial_no_num)).upper()
    return None


class JavLibraryApi:
    base_url = "https://www.javlibrary.com/cn"

    def __init__(self, session: requests.Session):
        self.session = session

    def impl_search_by_keyword(self, serial_no):
        url_video_list = f"{self.base_url}/vl_searchbyid.php?keyword={serial_no}"
        resp = self.session.get(url_video_list, allow_redirects=False)
        return resp

    def impl_get_video_detail(self, video_id):
        url_video_detail = f"{self.base_url}/?v={video_id}"
        return self.session.get(url_video_detail)

    def search_by_keyword(self, serial_no) -> Optional[Dict[str, str]]:
        resp = self.impl_search_by_keyword(serial_no)

        patt_video_id = re.compile(r"\.\/\?v=(.*)")
        res = {}
        if resp.status_code == 200:
            video_urls = etree.HTML(resp.text).xpath(".//div[@class='videos']/div[@class='video']/a")
            res = {
                parse_serial_no(video_url.get("title")): patt_video_id.match(video_url.get("href")).group(1)
                for video_url in video_urls
            }
        elif resp.status_code == 302:
            video_id = patt_video_id.match(resp.headers["location"]).group(1)
            res[serial_no] = video_id
        else:
            raise
        return res

    def get_video_detail(self, serial_no_reg, with_thumbnail=False):
        video_id = self.search_by_keyword(serial_no_reg)[serial_no_reg]
        resp_video_detail = self.impl_get_video_detail(video_id)

        root = etree.HTML(resp_video_detail.text)
        title = root.xpath(".//div[@id='video_title']//a[@rel='bookmark']/text()")[0]

        video_infos = dict(zip(
            ("serial_no", "publish_date", "length", "director", "maker", "publisher", "review", "category", "cast"),
            root.xpath(".//div[@id='video_info']/div")
        ))
        serial_no = video_infos["serial_no"].xpath(".//td[@class='text']/text()")[0]
        issue_date = video_infos["publish_date"].xpath(".//td[@class='text']/text()")[0]
        length = video_infos["length"].xpath(".//span[@class='text']/text()")[0]
        maker = video_infos["maker"].xpath(".//td[@class='text']/span/a/text()")[0].strip()
        publisher = video_infos["publisher"].xpath(".//td[@class='text']/span/a/text()")[0]
        casts = video_infos["cast"].xpath(".//td[@class='text']//span[@class='star']/a[@rel='tag']/text()")

        url_thumbnail = root.xpath(".//img[@id='video_jacket_img']/@src")[0]
        if not url_thumbnail.startswith("https:"):
            url_thumbnail = f"https:{url_thumbnail}"
        thumbnail = Image.open(BytesIO(requests.get(url_thumbnail).content)) if with_thumbnail else None

        res = {
            "title": title, "serial_no": serial_no, "publish_date": issue_date, "length": length,
            "maker": maker, "publisher": publisher, "cast": sorted(casts),
            "thumbnail": thumbnail

        }

        return res


class JavRecognizer:
    def __init__(self, session=None):
        self.session = session or self.prepare_session()
        self.jav_api = JavLibraryApi(self.session)

    @staticmethod
    def prepare_session():
        session = requests.session()
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "Referer": "https://www.javlibrary.com/cn/",
            "Proxy-Connection": "keep-alive",
        }
        session.proxies = {
            "https": "socks5://127.0.0.1:10808",
            "http": "socks5://127.0.0.1:10808"
        }
        return session

    def recognize(self, serial_no, with_thumbnail=True):
        serial_no_reg = parse_serial_no(serial_no)
        video_info = self.jav_api.get_video_detail(serial_no_reg, with_thumbnail)
        return video_info


def main():
    from matplotlib import pyplot as plt
    from util.logger import init_logger
    logger = init_logger("Logger(JavAnswerMe)")

    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    with_thumbnail = True if input("Download thumbnail? y(yes), n(no)") == "y" else False

    recognizer = JavRecognizer()
    while True:
        try:
            logger.info(f"{'#' * 64} \n")
            logger.info(f"Input a serial no:\n")
            serial_no = str(input(""))

            if serial_no == "?":
                break

            video_info = recognizer.recognize(serial_no, with_thumbnail=with_thumbnail)
            serial_no, casts, title, release_date, thumbnail = (
                video_info[k] for k in ("serial_no", "cast", "title", "publish_date", "thumbnail")
            )
            title = title.replace(serial_no, "").strip()
            casts = "&".join(casts)

            text = f"{casts}_{release_date}_{serial_no}_{title}"

            if with_thumbnail:
                plt.imshow(thumbnail)
                plt.title(text)
                plt.show()

            logger.info(text)
            logger.info(f"{'#' * 64} \n")
            time.sleep(1)
        except Exception as e:
            logger.info(e)
            continue


if __name__ == '__main__':
    main()
