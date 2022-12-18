import re
import shutil
import subprocess
from hashlib import md5
from io import BytesIO
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from urllib.parse import unquote

import requests
from Crypto.Cipher import AES
from PIL import Image
from lxml import etree


class MadouDownloader:
    session = requests.session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Referer": "https://www.javlibrary.com/cn/",
        "Proxy-Connection": "keep-alive",
    }

    def __init__(self, save_dir="Z:\Madou", pool=20):
        self.pool_num = pool
        self.save_dir = Path(save_dir)

    def get_binary(self, url):
        try:
            resp = self.session.get(url)

            while resp.status_code != 200:
                print(f"retry: {url}")
                resp = self.session.get(url)

            return resp.content
        except:
            return self.get_binary(url)

    def convert_ts_to_mp4(self, file_src_ts, file_dst_mp4, meta: dict):
        file_in = Path(file_src_ts).as_posix()
        file_out = Path(file_dst_mp4).as_posix()
        file_thumbnail = Path(meta["thumbnail"]).as_posix()
        cmd = f"ffmpeg " \
              f"-i {file_in} " \
              f"-i {file_thumbnail} -map 0 -map 1 -c copy -c:v:1 png -disposition:v:1 attached_pic " \
              f"-metadata title=\"{meta['title']}\" " \
              f"{file_out} "
        res = subprocess.run(cmd)
        return res

    @staticmethod
    def decrypt(data, key, iv):
        """Decrypt using AES CBC"""
        decryptor = AES.new(key, AES.MODE_CBC, IV=iv)
        return decryptor.decrypt(data)

    def parse_url_meta(self, url):
        resp = self.session.get(url)
        et = etree.HTML(resp.text)
        url_video = et.xpath("//iframe/@src")[-1]
        resp_meta = self.session.get(url_video).text
        token = re.search("var token = \"(.*?)\"", resp_meta).group(1)
        uri_m3u8 = re.search("var m3u8 = '/(.*?/index.m3u8)'", resp_meta).group(1)
        url_m3u8 = f"https://dash.madou.club/{uri_m3u8}?token={token}"
        text_m3u8 = self.session.get(url_m3u8).text

        uri_ts_path_base = f"https://dash.madou.club/{uri_m3u8.split('/index.m3u8')[0]}"

        ts_key_uri, ts_iv_str, = re.search('#EXT-X-KEY:METHOD=AES-128,URI="(.*)",IV=(.*)\s', text_m3u8).groups()
        ts_key, ts_iv = self.get_binary(ts_key_uri), bytes.fromhex(ts_iv_str.replace("0x", ""))
        ts_urls = [f"{uri_ts_path_base}/{filename}" for filename in text_m3u8.splitlines() if filename.endswith(".ts")]

        url_thumbnail = re.search("shareimage : \'(.*?)\'", re.sub("\s+", " ", resp.text)).group(1)

        return ts_key, ts_iv, ts_urls, url_thumbnail

    def download_single_ts(self, ts_url, ts_key, ts_iv, save_file_path):
        data_enc = self.get_binary(ts_url)
        with open(save_file_path, "wb") as file_handle:
            data_dec = self.decrypt(data_enc, ts_key, ts_iv)
            file_handle.write(data_dec)

    def _download_ts(self, ts_urls, ts_key, ts_iv, thumbnail_url, save_file_path, convert=True):
        save_file_path = Path(save_file_path)
        file_dir, file_name = save_file_path.parent, save_file_path.stem

        temp_dir = file_dir / f"temp_{md5(file_name.encode()).hexdigest()}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        print("Downloading Thumbnail...")
        file_thumbnail = temp_dir / "thumbnail.png"
        Image.open(BytesIO(self.get_binary(thumbnail_url))).save(file_thumbnail)

        print("Downloading Files...")
        thread_pool = ThreadPool(self.pool_num)
        for idx, ts_url in enumerate(ts_urls):
            temp_file_name = ts_url.split("/")[-1]
            temp_file_index = re.search("index(\d*?)\.ts", temp_file_name).group(1)
            temp_file_path = temp_dir / f"ts_{temp_file_index:0>5}.temp"
            thread_pool.apply_async(
                self.download_single_ts,
                args=(ts_url, ts_key, ts_iv, temp_file_path),
                error_callback=print
            )
        thread_pool.close()
        thread_pool.join()

        print("Merge Files...")
        temp_file_merged = f"{temp_dir}/{file_name}.ts.merge"
        with open(temp_file_merged, "wb") as file_merged:
            for ts_file in sorted(filter(lambda f: f.suffix == ".temp", temp_dir.iterdir())):
                with open(ts_file, "rb") as file_chunk:
                    shutil.copyfileobj(fsrc=file_chunk, fdst=file_merged)

        if convert:
            print("Converting ts to mp4, and adding meta")
            meta = {"thumbnail": file_thumbnail, "title": file_name}
            self.convert_ts_to_mp4(temp_file_merged, save_file_path.parent / f"{save_file_path.stem}.mp4", meta)
        else:
            shutil.move(temp_file_merged, save_file_path)

        print("Clean Up...")
        shutil.rmtree(temp_dir)

    def download_video(self, url, save_dir=None, check_existed=True):
        save_dir = save_dir or self.save_dir
        video_name = f"{unquote(Path(url).stem)}".upper()
        save_file = f"{save_dir}/{video_name}.ts"

        if check_existed:
            if video_name in set(x.stem for x in save_dir.iterdir()):
                return True

        print(f"Parsing Video Meta: {video_name}")
        ts_key, ts_iv, ts_urls, thumbnail_url = self.parse_url_meta(url)

        self._download_ts(ts_urls, ts_key, ts_iv, thumbnail_url, save_file, convert=True)

    def download_by_tag(self, url_with_tag, check_existed=True):
        tag = unquote(Path(url_with_tag).stem)
        save_dir = self.save_dir / tag
        save_dir.mkdir(exist_ok=True, parents=True)

        urls_whole = []
        for i in range(100000):
            urls = etree.HTML(self.session.get(f"{url_with_tag}/page/{i}").text).xpath("//article/a/@href")
            urls_whole.extend(urls)
            if len(urls) == 0:
                break
        print(f"Tag: {tag}. Found {len(urls_whole)} videos.")

        for url in urls_whole:
            print(f"Start Downloading {unquote(url)}")
            self.download_video(url, save_dir, check_existed=check_existed)
            print(f"Finished Downloading {unquote(url)}")

        print("All Videos Finished")
