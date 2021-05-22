import json
from time import sleep

import requests
from lxml import html


class CinemaBlendArticles:
    def __init__(self):
        self.articles_links = list()
        self.articles = list()
        self.page1_url = 'https://www.cinemablend.com/news'

    def download_articles(self, newest_id, oldest_id):
        for i in range(newest_id, oldest_id - 1, -1):
            self.get_article("{0}/{1}".format(self.page1_url, str(i)))

    @staticmethod
    def normalize_article_text(text):
        lines = text.split("\n")
        for j in range(len(lines)):
            lines[j] = lines[j].strip()
        new_lines = [line for line in lines if line]
        return "\n".join(new_lines)

    def collect_article_links(self, tree):
        # оброблення сторінок з анонсами
        web1 = tree.xpath("//div[@class='partial content_story_cb_related topics']/div[contains(@class, " +
                          "'story_item  item')]/div[@class='content']/div/a")
        # отримуємо покликання анонсів на цій сторінці
        articles_urls = ["https://www.cinemablend.com" +
                         x.attrib['href'] for x in web1]
        self.articles_links.extend(articles_urls)

    def pages_content(self, num):
        # функція для отримання даних з певної сторінки:
        # https://www.cinemablend.com/news?page=2
        # https://www.cinemablend.com/news?page=10
        page_url = "https://www.cinemablend.com/news?page={0}".format(num)
        page = requests.get(page_url)
        tree = html.fromstring(page.content)
        self.collect_article_links(tree)

    def get_articles(self, article_links):
        pass

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
        try:
            tree = html.fromstring(page.content)
            # отримуємо заголовок новини
            # отримуємо текст анонсу новини (частинами)
            xpath_ = """//script[@type='application/ld+json']//text()"""
            article_parts_json = tree.xpath(xpath_)
            article_json = json.loads(article_parts_json[0])
            article_url = article_json['url']
            if "https://www.cinemablend.com/title/" in article_url:
                print("Article skipped\n{0}".format(article_url))
                return
            header = article_json['headline']
            header = header.strip("\n")
            article = article_json['articleBody']
            # об'єднуємо частини у єдиний текст
            article = self.normalize_article_text(article)
            # зберігаємо до списку у форматі:
            # 1. покликання на анонс
            # 2. заголовок
            # 3. вміст
            self.articles.append([header, article, article_url])
            self.articles_links.append(article_url)
            print("Success with page\n{0}".format(article_url))
        except IndexError:
            print("Error on downloading text\n{0}".format(page_url))
            print(len(self.articles))
        except KeyError:
            print("Error on downloading text\n{0}".format(page_url))
            print(len(self.articles))
