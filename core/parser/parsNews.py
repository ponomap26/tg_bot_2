#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер новостей EVE Online
Извлекает заголовки, ссылки, описания, даты, авторов и теги
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional


class EveNewsParser:
    """Парсер новостей EVE Online"""

    BASE_URL = "https://www.eveonline.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

    def _parse_article(self, article: BeautifulSoup) -> Optional[Dict]:
        """Парсит одну статью"""
        news_item = {}

        # Ссылка на новость
        main_link = article.find("a", href=lambda x: x and "/ru/news/view/" in x)
        if main_link:
            href = main_link.get("href", "")
            news_item["link"] = (
                f"{self.BASE_URL}{href}" if href.startswith("/") else href
            )

        # Изображение
        img_wrapper = article.find("div", class_="Card_imgWrapper__JJsP1")
        if img_wrapper:
            img = img_wrapper.find("img")
            if img:
                news_item["image"] = img.get("src", "")

        # Контент
        content_div = article.find("div", class_="Card_content__zpl+B")
        if content_div:
            # Дата и автор
            date_author = content_div.find(
                "span", class_="DateAndAuthor_author_date__sXdb2"
            )
            if date_author:
                full_text = date_author.get_text(separator=" ", strip=True)
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", full_text)
                if date_match:
                    news_item["date"] = date_match.group(1)
                    after_date = full_text[date_match.end() :]
                    author = re.sub(r"^\s*-\s*", "", after_date).strip()
                    news_item["author"] = author

            # Заголовок
            title_tag = content_div.find("h3", class_="Card_title__cPVUS")
            if title_tag:
                title_link = title_tag.find("a")
                if title_link:
                    news_item["title"] = title_link.get_text(strip=True)

            # Описание
            desc_tag = content_div.find("p", class_="Card_desc__+Ixi3")
            if desc_tag:
                news_item["description"] = desc_tag.get_text(strip=True)

        # Теги
        tags = []
        tags_ul = article.find("ul", class_="Tags_tags__mqwB3")
        if tags_ul:
            for tag_li in tags_ul.find_all("li"):
                tag_a = tag_li.find("a")
                if tag_a:
                    tag_name = tag_a.find("span")
                    tags.append(
                        {
                            "name": (
                                tag_name.get_text(strip=True)
                                if tag_name
                                else tag_a.get_text(strip=True).replace("#", "")
                            ),
                            "link": (
                                f"{self.BASE_URL}{tag_a.get('href', '')}"
                                if tag_a.get("href", "").startswith("/")
                                else tag_a.get("href", "")
                            ),
                        }
                    )
        news_item["tags"] = tags

        # Возвращаем только если есть ссылка и заголовок
        if news_item.get("link") and news_item.get("title"):
            return news_item
        return None

    def parse_news_page(self, url: str = f"{BASE_URL}/ru/news") -> List[Dict]:
        """
        Парсит страницу новостей

        Args:
            url: URL страницы с новостями

        Returns:
            Список словарей с данными новостей
        """
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        news_list = []

        # Ищем все карточки новостей
        articles = soup.find_all("article", class_="Card_card__MB2BP")

        for article in articles:
            news_item = self._parse_article(article)
            if news_item:
                news_list.append(news_item)

        return news_list

    def parse_archive(
        self, year: Optional[int] = None, month: Optional[int] = None, page: int = 1
    ) -> List[Dict]:
        """
        Парсит архив новостей

        Note: Архив загружается динамически через JavaScript,
        поэтому этот метод может не работать без браузера

        Args:
            year: Год для фильтрации
            month: Месяц для фильтрации
            page: Номер страницы

        Returns:
            Список словарей с данными новостей
        """
        url = f"{self.BASE_URL}/ru/news/archive"
        params = {}

        if year:
            url = f"{url}/{year}"
        if page > 1:
            params["p"] = page

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        news_list = []
        articles = soup.find_all("article", class_="Card_card__MB2BP")

        for article in articles:
            news_item = self._parse_article(article)
            if news_item:
                news_list.append(news_item)

        return news_list

    def save_to_json(self, news_list: List[Dict], filename: str = "eve_news.json"):
        """Сохраняет новости в JSON файл"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(news_list)} новостей в {filename}")

    def print_news(self, news_list: List[Dict]):
        """Красивый вывод новостей"""
        for i, news in enumerate(news_list, 1):
            print(f"\n{'='*70}")
            print(f"Новость #{i}")
            print(f"{'='*70}")
            print(f"Заголовок: {news.get('title', 'N/A')}")
            print(f"Ссылка: {news.get('link', 'N/A')}")
            print(f"Дата: {news.get('date', 'N/A')}")
            print(f"Автор: {news.get('author', 'N/A')}")
            desc = news.get("description", "N/A")
            if desc and desc != "N/A":
                print(f"Описание: {desc[:150]}{'...' if len(desc) > 150 else ''}")
            else:
                print("Описание: N/A")
            if news.get("tags"):
                tags_str = ", ".join([t["name"] for t in news["tags"]])
                print(f"Теги: {tags_str}")
            if news.get("image"):
                print(f"Изображение: {news['image'][:70]}...")


# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===
if __name__ == "__main__":
    parser = EveNewsParser()

    print("Парсинг новостей EVE Online...")
    print("-" * 70)

    # Парсим главную страницу новостей
    news = parser.parse_news_page()

    if news:
        parser.print_news(news)
        parser.save_to_json(news, "eve_news.json")
        print(f"\n\nВсего найдено: {len(news)} новостей")
    else:
        print("Новости не найдены или произошла ошибка")


parser = EveNewsParser()
