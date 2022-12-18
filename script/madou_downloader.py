from urllib.parse import quote

from lib.pornvids.madou import MadouDownloader

if __name__ == '__main__':
    dl = MadouDownloader()
    dl.session.proxies = {
        "https": "socks5://127.0.0.1:10808",
        "http": "socks5://127.0.0.1:10808",
    }

    tasks = [
        "https://madou.club/kd016-%e7%b2%89%e7%ba%a2%e5%a5%b3%e4%bb%86%e8%af%b1%e6%83%91-%e9%82%bb%e5%ae%b6%e5%b0%8f%e5%a6%b9%e7%b4%a2%e7%88%b1.html",
        "https:/madou.club/twa0022-%e5%92%8c%e6%86%a7%e6%86%ac%e7%9a%84%e7%be%8e%e5%a5%b3%e8%80%81%e5%b8%88%e5%8f%91%e7%94%9f%e4%ba%b2%e5%af%86%e6%8e%a5%e8%a7%a6.html",
        "https://madou.club/twa0017-%e6%9a%97%e6%81%8b%e7%9a%84%e5%a5%b3%e5%90%8c%e5%ad%a6%e7%94%a8%e7%be%8e%e8%85%bf%e9%80%bc%e6%88%91%e5%b0%84%e7%b2%be.html",
        "https://madou.club/twa0011-%e6%9a%91%e5%81%87%e4%b8%80%e6%a5%bc%e4%b8%80%e5%87%a4%e4%b9%b0%e5%8f%af%e4%b9%9001.html",
        "https://madou.club/fsog063-%e5%86%85%e5%b0%84%e8%b6%85%e5%ab%a9%e5%ad%a6%e7%94%9f%e5%a6%b9.html",
        "https://madou.club/%e6%9e%9c%e5%86%bb%e4%bc%a0%e5%aa%92-%e6%97%a5%e6%9c%ac%e5%a5%b3%e7%94%9f%e6%8b%9c%e9%87%91%e7%a8%8b%e5%ba%a6%e5%a4%a7%e8%80%83%e9%aa%8c.html",
        "https://madou.club/%e6%9e%9c%e5%86%bb%e4%bc%a0%e5%aa%92-91%e7%89%b9%e6%b4%be%e5%91%98-%e4%b8%9c%e4%ba%ac%e6%b9%be%e6%81%8b%e4%ba%ba.html",
    ]
    for tag in tasks[::-1]:
        dl.download_video(tag)

    tags = [
        "绯丽", "翁雨澄", "浅尾美羽", "徐婕", "沙美辰", "王筱璐", "不见星空", "李蕊", "李依依", "林嫣",
        "周宁", "顾桃桃", "玥可岚", "樱桃", "琳达", "夏晴子", "cola酱", "汁汁", "夜夜", "蒋佑怡",
        "黎娜", "何雨", "依涵", "唐伯虎", "吴梦梦", "尤莉", "七濑恋", "小遥", "小敏儿", "雪千夏",
        "三月樱花", "楚梦舒"
    ]
    for tag in tags[::-1]:
        tag_url = f"https://madou.club/tag/{quote(tag)}"
        print(f"{tag}: {tag_url}")
        dl.download_by_tag(tag_url)

    print("Bye!")
