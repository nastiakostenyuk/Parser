import json
import requests
import bs4
import logging

from fake_useragent import UserAgent
from dateparser import parse

logging.basicConfig(level=logging.DEBUG)

url = "https://kam-pod.gov.ua/novini/town-news"

headers = {"User-Agent": UserAgent().random}
session = requests.Session()
session.headers.update(headers)


def parse_news_block(news_block) -> dict:
    link_element = news_block.select_one(".catItemTitle")
    desc = None
    try:
        desc = news_block.select_one(".catItemIntroText").text.strip()
    except:
        pass
    date = parse(news_block.select_one(".catItemDateCreated").text.strip())
    news = {
        "title": link_element.text.strip(),
        "date": date.isoformat(),
        "description": desc
    }
    return news


def prepare_page_param(page_number: int):
    return (page_number - 1) * 8


page = 1
news_list = []
last_page = 3

while page <= last_page:
    response = session.get(url, params={"start": prepare_page_param(page)},
                           headers={"x-requested-with": "XMLHttpRequest"})
    soup = bs4.BeautifulSoup(response.text, "lxml")
    news_block_list = soup.select(".catItemBody")
    current_news_list = list(map(parse_news_block, news_block_list))

    news_list.extend(current_news_list)
    page += 1

with open("kam-pods.json", "w", encoding='utf-8') as f:
    json.dump(news_list, f, ensure_ascii=False, indent=4, default=str)