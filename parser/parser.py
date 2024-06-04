import codecs
import selenium
from bs4 import BeautifulSoup
import requests
import json
import lxml

url = "https://www.eveonline.com/ru/news/"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"

}
response = requests.get(url, headers=headers)

src = response.text

#
soup = BeautifulSoup(src, "lxml")
def get_news():
    add_news = []
    article_one = soup.find(class_="lazyload-wrapper").find_parent("a")
    article_two = soup.find(class_="CardFeatured_card__Hr9Mq").find('h2')
    description = article_two.text.strip()
    # print(article_one)
    # print(article_two)
    href = article_one.get('href')
    # text = article_one.text.strip()
    add_news.append(f'\n {description} \n https://www.eveonline.com{href}\n')
    articles = soup.find(class_="NewsPage_grid__2X8g7 NewsPage_grid3__2fCvj").find_all("article")
    for article in articles:
        description = article.find('div', class_="Card_content__2B4VA").find("p").text
        text = article.find('div', class_="Card_content__2B4VA").find("h3").text
        href = article.find('div', class_="Card_content__2B4VA").find("h3").find("a").get("href")
        add_news.append(f'{text}\n {description} \n https://www.eveonline.com{href}\n')
    articles = soup.find(class_="NewsPage_grid__2X8g7 NewsPage_grid2__2QfQT").find_all("article")
    

    return add_news

# def get_news():
#     add_news = []
#
#     # Используем класс 'NewsPage_grid__2X8g7' без регулярного выражения
#     add_article = soup.find('div', class_='NewsPage_grid__2X8g7 NewsPage_grid2_1__Dj-2s')
#
#
#     href = add_article.get('href')
#     text = add_article.text.strip()
#     add_news.append(f'{text}-https://www.eveonline.com/ru{href}')


    # return add_news
    #
    # add_article_all = soup.find_all('NewsPage_grid__2X8g7')
    #
    # for a in add_article_all:
    #     href_all = a.get('href')
    #     text = a.text.strip()
    #     print(f" Все новости {text_all}-https://www.eveonline.com/ru{href_all}")
    #     add_news.append(f' {text} -https://www.eveonline.com/ru{href_all}')
    # print(add_news)
    # return add_news
