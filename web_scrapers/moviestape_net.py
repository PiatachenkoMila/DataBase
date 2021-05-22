import re
from time import sleep

import requests
from lxml import html


class MoviestapeArticles:
    def __init__(self):
        self.articles_links = list()
        self.articles = list()
        self.page1_url = 'http://moviestape.net/novyny_kino/'

    def download_articles(self, start_page, end_page):
        for i in range(start_page, end_page + 1):
            self.pages_content(i)  # оброблення контенту сторінок

    def last_page_num(self):
        # функція для визначення останньої сторінки з анонсами новин
        page = requests.get(self.page1_url)
        tree = html.fromstring(page.content)
        xpath_pages = tree.xpath("//div[@class='navigation']/a")
        # отримуємо покликання з панелі із номерами сторінок
        pages_urls = [x.attrib['href'] for x in xpath_pages]
        # за допомогою регулярного виразу видобуваємо номери з покликань
        num_pattern = '\d+'
        find_numbers = []
        for url in pages_urls:
            find_numbers.extend(re.findall(num_pattern, url))
        # знаходимо максимальний номер сторінки
        last_num = max([int(x) for x in find_numbers])
        return last_num

    def collect_article_links(self, tree):
        # оброблення сторінок з анонсами
        web1 = tree.xpath("//div[contains(@class, 'fl-r info')]/h2/a")
        # отримуємо покликання анонсів на цій сторінці
        articles_urls = [x.attrib['href'] for x in web1]
        self.articles_links.extend(articles_urls)

    def pages_content(self, num):
        # функція для отримання даних з певної сторінки:
        # http://moviestape.net/novyny_kino/page/2/
        # http://moviestape.net/novyny_kino/page/10/
        page_url = "http://moviestape.net/novyny_kino/page/{0}/".format(num)
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
        article_parts = tree.xpath("//div[contains(@id, 'news-id-')]//text()")
        # об'єднуємо частини у єдиний текст
        article = " ".join(article_parts)
        # зберігаємо до списку у форматі:
        # 1. заголовок
        # 2. вміст
        # 3. покликання на анонс
        self.articles.append([header, article, page_url])
