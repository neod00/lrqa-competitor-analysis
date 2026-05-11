import datetime
import email.utils
from urllib.parse import quote

import requests
import urllib3
import yaml
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NewsCrawler:
    def __init__(self, days_ago=30):
        self.days_ago = days_ago
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)["crawling"]
            self.competitors = config["competitors"]
            self.regulations = config.get("regulations", {})
            self.naver_blogs = config.get("naver_blogs", {})

    def fetch_latest_news(self):
        crawled_data = {}
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=self.days_ago)

        # Google News RSS가 봇 접근을 막는 경우를 줄이기 위한 일반 브라우저 헤더입니다.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        for _key, name in self.competitors.items():
            print(f"[{name}] Google News RSS 수집 중...")
            query = f'"{name}" 인증 OR 세미나 OR 협약 OR 교육 OR 보고서 OR 서비스'
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
            self._fetch_rss(url, name, headers, cutoff_date, crawled_data)

        for reg_name, reg_query in self.regulations.items():
            print(f"[규제 동향: {reg_name}] Google News RSS 수집 중...")
            url = f"https://news.google.com/rss/search?q={quote(reg_query)}&hl=ko&gl=KR&ceid=KR:ko"
            self._fetch_rss(url, f"규제: {reg_name}", headers, cutoff_date, crawled_data)

        for blog_id, blog_name in self.naver_blogs.items():
            print(f"[네이버 블로그: {blog_name}] RSS 수집 중...")
            url = f"https://rss.blog.naver.com/{blog_id}.xml"
            self._fetch_rss(url, blog_name, headers, cutoff_date, crawled_data)

        return crawled_data

    def _fetch_rss(self, url, name, headers, cutoff_date, crawled_data):
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code != 200:
                print(f"[{name}] RSS 접속 실패 (상태 코드: {response.status_code})")
                return

            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")

            news_list = []
            for item in items:
                pub_date_node = item.find("pubDate")
                title_node = item.find("title")
                link_node = item.find("link")
                if not pub_date_node or not title_node or not link_node:
                    continue

                try:
                    pub_date = email.utils.parsedate_to_datetime(pub_date_node.text)
                except Exception:
                    continue

                if pub_date >= cutoff_date:
                    clean_title = title_node.text.replace(" - Google 뉴스", "")
                    news_list.append(
                        {
                            "title": clean_title,
                            "date": pub_date.strftime("%Y-%m-%d"),
                            "link": link_node.text,
                        }
                    )

            if news_list:
                unique_news = []
                seen_titles = set()
                for news in news_list:
                    if news["title"] not in seen_titles:
                        seen_titles.add(news["title"])
                        unique_news.append(news)

                # 규제 동향은 주제별 상위 2개, 경쟁사/블로그는 상위 3개만 보내 AI 토큰 사용량을 제한합니다.
                limit = 2 if name.startswith("규제:") else 3
                crawled_data[name] = unique_news[:limit]
            else:
                print(f"[{name}] 기간 조건에 맞는 기사 없음 (총 검색 기사 수: {len(items)})")

        except Exception as e:
            print(f"[{name}] RSS 수집 실패: {e}")
