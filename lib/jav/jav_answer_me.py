import requests
import re
from util.win32.base import set_text


session = requests.session()
session.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    "Referer": "http://www.h28o.com/cn/",
    "Proxy-Connection": "keep-alive",
}
session.proxies = {
    "https": "socks5://127.0.0.1:9527",
    "http": "socks5://127.0.0.1:9527"
}


def search(serie_no=None):
    serie_no = re.sub("-| |\.", "", serie_no)
    serie_no = "-".join((
        "".join([x for x in serie_no if x.isalpha()]),
        "".join([x for x in serie_no if x.isdigit()]),
    )).upper()

    print("parsing...")
    base_url = "http://www.h28o.com/cn"
    api_search, api_detail = "vl_searchbyid.php?keyword=", "?v="

    api = f"{base_url}/{api_search}{serie_no}"

    print(api)
    resp = session.get(api)

    def check_and_redirect(resp):
        if not resp.url.startswith(f"{base_url}/{api_detail}"):
            res_candidates = re.findall("\<a href=\".*?v=(.*?)\" title=(.*?)\"\>\<div class=\"id\"\>(.*?)\<", resp.text)
            print(res_candidates)
            res_candidates = {x[2]: x[0] for x in res_candidates}

            return session.get(f"{base_url}/{api_detail}{res_candidates[serie_no]}")
        return resp

    def parse_title(resp):
        whole_title = re.search("<title>(.*?)</title>", resp.text).group(1)
        whole_title = whole_title.replace(" - JAVLibrary", "")
        serie_no, content = whole_title.split(" ", maxsplit=1)

        context_rev_splitted = content[::-1].split(" ", maxsplit=1)
        if len(context_rev_splitted) == 2:
            actress, title = (x[::-1] for x in context_rev_splitted)
        else:
            title, = (x[::-1] for x in context_rev_splitted)
            actress = None

        return serie_no, actress, title

    def parse_date(resp):
        return re.search("发行日期.*?(\d{4}-\d{2}-\d{2})", re.sub("\s", "", resp.text)).group(1)

    resp = check_and_redirect(resp)
    serie_no, actress, title = parse_title(resp)
    release_date = parse_date(resp).replace("-", ".")

    return serie_no.upper(), actress, title, release_date


def main():
    import time
    while True:
        try:
            no = str(input())
            if no == "?":
                break

            serie_no, actress, title, release_date = search(no)

            text = f"{release_date} {serie_no} {title}"
            set_text(text)
            print(actress)
            print(text)
            time.sleep(1)
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    main()
