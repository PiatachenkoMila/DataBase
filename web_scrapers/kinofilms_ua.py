from time import sleep
from urllib.parse import urljoin

import requests
from lxml import html


class KinofilmsArticles:
    def __init__(self):
        self.articles_links = list()
        self.articles = list()
        self.page1_url = 'https://www.kinofilms.ua/ukr/news/'

    def download_articles(self, start_page, end_page):
        for i in range(start_page, end_page + 1):
            self.pages_content(i)  # оброблення контенту сторінок
            print("Pages processed:{0}/{1}".format(str(i), str(end_page + 1)))

    def last_page_num(self):
        pass

    @staticmethod
    def normalize_article_text(text):
        lines = text.split("\n")
        for j in range(len(lines)):
            lines[j] = lines[j].strip()
        new_lines = [line for line in lines if line]
        return "\n".join(new_lines)

    def collect_article_links(self, tree):
        # оброблення сторінок з анонсами
        web1 = tree.xpath("//a[@class='o']")
        # отримуємо покликання анонсів на цій сторінці
        articles_urls = [urljoin("https://www.kinofilms.ua/",
                                 x.attrib['href']) for x in web1]
        self.articles_links.extend(articles_urls)

    def pages_content(self, num):
        # функція для отримання даних з певної сторінки:
        # https://www.kinofilms.ua/ukr/news/?page=2
        # https://www.kinofilms.ua/ukr/news/?page=10
        page_url = "https://www.kinofilms.ua/ukr/news/?page={0}/".format(num)
        page = requests.get(page_url)
        tree = html.fromstring(page.content)
        self.collect_article_links(tree)

    def get_articles(self, article_links):
        articles_count = len(article_links)
        for (i, url) in enumerate(article_links):
            self.get_article(url)
            status_text = "Texts downloaded: {} of {}".format(i + 1,
                                                              articles_count)
            print(status_text)

    def get_article(self, page_url):
        # видобування статті з анонсом новини
        ts = 5
        try:
            # звернення до веб-сайту за сторінкою
            page = requests.get(page_url)
        except requests.exceptions.ConnectionError:
            # якщо відмовлено у з'єднанні, призупиняємо роботу програми на
            # 5 секунд
            print("Connection error. Retry in {0} seconds...".format(ts))
            sleep(ts)
            page = requests.get(page_url)
            ts += 1

        tree = html.fromstring(page.content)
        # отримуємо заголовок новини
        header = tree.xpath("//h1/text()")[0]
        # отримуємо текст анонсу новини (частинами)
        article_parts = tree.xpath("//section//text()")
        # об'єднуємо частини у єдиний текст
        article = " ".join(article_parts)
        article = self.normalize_article_text(article)
        # зберігаємо до списку у форматі:
        # 1. заголовок
        # 2. вміст
        # 3. покликання на анонс
        self.articles.append([header, article, page_url])
