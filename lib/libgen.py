import re
from typing import Tuple, Dict

import requests
from PIL import Image
from lxml import etree


class LibgenDownloader:
    domain = "http://libgen.rs"

    urls = {
        "api_search_book": f"{domain}/search.php",
        "api_book_detail": f"{domain}/book/index.php?md5=",
        "api_get_downloads": "http://library.lol/main",
    }

    payload = {
        "req": "",  # req should be the first parameter, for this site
        "open": 0,
        "view": "simple",
        "res": None,
        "phrase": 1,
        "column": "",
        "page": None
    }

    @staticmethod
    def maybe_isbn(s: str) -> bool:
        if not (len(s) == 13 or len(s) == 10):
            return False
        try:
            int(s)
        except ValueError:
            return False
        return True

    @classmethod
    def _request_search_book(cls, book: str, by: str = None, offset=50, page=1):
        columns = {"title": "def", "isbn": "identifier"}
        if by is None:
            by = "isbn" if cls.maybe_isbn(book) else "title"

        payload = cls.payload.copy()
        payload.update(**{
            "req": book.replace(" ", "+"),
            "column": columns[by],
            "res": offset,
            "page": page
        })
        # payload["req"] =
        # payload["column"] = columns[by]
        # payload["res"] = offset
        # payload["page"] = page

        payload_encoded = "&".join((f"{k}={v}" for k, v in payload.items()))
        url = f"{cls.urls['api_search_book']}?{payload_encoded}"
        print(url)
        return requests.get(url)

    @staticmethod
    def _parse_page_book_index(string):
        html_tree = etree.HTML(string)
        files_found = int(re.match(
            "([0-9]*) files found",
            html_tree.xpath("//table//font[@color='grey']/text()")[0]
        ).groups()[0])
        print(f"files found: {files_found}")
        if len((trs := html_tree.xpath("//table[@class='c']//tr"))) <= 1:  # means at least 1 result
            return None, 0

        def parse_title(td):
            tag_a = td.xpath("./a")[-1]
            book_md5 = tag_a.get("href")[19:]  # len("book/index.php?md5=") = 19
            book_title = tag_a.xpath("./text()")[0].strip()
            return book_md5, book_title

        books = {}
        for tr in trs[1:]:
            tds = tr.xpath("./td")

            md5, title = parse_title(tds[2])

            books[md5] = {
                "id": tds[0].text,
                "author(s)": [author.strip() for author in tds[1].xpath(".//a/text()")],
                "title": title,
                "year": elements[0].strip() if len(elements := tds[4].xpath(".//text()")) == 1 else None,
                "pages": "".join((x.strip() for x in elements)) if len(
                    elements := tds[5].xpath(".//text()")) > 0 else None,
                "language": elements[0].strip() if len(elements := tds[6].xpath("./text()")) == 1 else None,
                "size": elements[0].strip() if len(elements := tds[7].xpath("./text()")) == 1 else None,
                "format": elements[0].strip() if len(elements := tds[8].xpath("./text()")) == 1 else None,
            }

        return books, files_found

    @classmethod
    def search_book(cls, book: str, extension=None, page=1, offset=50) -> Tuple[int, Dict[str, Dict]]:
        """

        Args:
            book: str
                Book name or ISBN(10/13 digit) to search;
            extension: str, optional {"pdf", "zip", "epub"}
                Format to filter;
            page: int
                ...
            offset: int, optional {25, 50, 100}
                ...

        Returns:
            tuple(book_num: int, books: dict)
        """
        resp = cls._request_search_book(book, None, offset, page)
        books, books_num = cls._parse_page_book_index(resp.text)
        if extension is not None:
            books = dict(filter(lambda kv: kv[1]["format"] == extension, books.items()))
        return books_num, books

    @classmethod
    def get_download_links(cls, book_md5):
        url = cls.urls["api_get_downloads"]
        resp = requests.get(f"{url}/{book_md5}")
        html_tree = etree.HTML(resp.text)
        return {tag_a.text: tag_a.get("href") for tag_a in html_tree.xpath("//table//li/a")}

    @staticmethod
    def get_book_detail(book_md5):
        res = requests.get(f"http://libgen.rs/book/index.php?md5={book_md5}")
        tree = etree.HTML(res.text)

        isbns = sorted(tree.xpath("//tr[./td//font[text() = 'ISBN:']]/td[2]/text()"), key=lambda s: len(s))
        url_picture = f"{LibgenDownloader.domain}/{tree.xpath('//img/@src')[0]}"
        im = Image.open(requests.get(url_picture, stream=True).raw)
        trs = tree.xpath("//tr[./td/nobr/font[text() = 'Book attributes:']]/td[2]/table/tr")
        attributes = (a.strip().lower().replace(":", "") for a in trs[0].xpath("./td//text()"))
        values = (
            "?" if (v_stripped := v.strip()) == "" else v_stripped
            for v in trs[1].xpath("./td//text()")
        )

        book_info_detail = dict(filter(lambda a_v: a_v[0] in {"ocr", "bookmarked", "scanned"}, zip(attributes, values)))
        book_info_detail["ISBN"] = isbns
        book_info_detail["thumbnail"] = im
        return book_info_detail


if __name__ == '__main__':
    books_num, books = LibgenDownloader.search_book(book="introduction to algorithms")

    for book_md5, book_info in books.items():
        print(book_info)
        print(LibgenDownloader.get_download_links(book_md5))
        print(LibgenDownloader.get_book_detail(book_md5))
