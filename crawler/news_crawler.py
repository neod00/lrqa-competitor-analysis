import requests
from bs4 import BeautifulSoup
import datetime
from urllib.parse import quote
import yaml
import email.utils
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NewsCrawler:
    def __init__(self, days_ago=30):
        self.days_ago = days_ago
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)["crawling"]
            self.competitors = config["competitors"]
            self.regulations = config.get("regulations", [])
            self.naver_blogs = config.get("naver_blogs", {})

    def fetch_latest_news(self):
        crawled_data = {}
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=self.days_ago)
        
        # 핵심 해결 1. 구글의 클라우드 봇 차단을 뚫기 위해 PC 크롬 유저인 척 위장
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        for key, name in self.competitors.items():
            print(f"[{name}] 구글 뉴스 크롤링 접속 중...")
            query = f'"{name}" 인증 OR 세미나 OR 협약'
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
            self._fetch_rss(url, name, headers, cutoff_date, crawled_data)

        # 핵심 추가사항: 글로벌 규제 동향 크롤링 (config.yaml 활용, 유연한 OR 검색 허용)
        for reg_name, reg_query in self.regulations.items():
            print(f"[규제 동향: {reg_name}] 구글 뉴스 크롤링 접속 중...")
            url = f"https://news.google.com/rss/search?q={quote(reg_query)}&hl=ko&gl=KR&ceid=KR:ko"
            self._fetch_rss(url, f"규제: {reg_name}", headers, cutoff_date, crawled_data)

        # 핵심 추가사항: 네이버 블로그 RSS 크롤링
        for blog_id, blog_name in self.naver_blogs.items():
            print(f"[네이버 블로그: {blog_name}] 크롤링 접속 중...")
            url = f"https://rss.blog.naver.com/{blog_id}.xml"
            self._fetch_rss(url, blog_name, headers, cutoff_date, crawled_data)

        return crawled_data

    def _fetch_rss(self, url, name, headers, cutoff_date, crawled_data):
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code != 200:
                print(f"[{name}] 구글 뉴스 접속 실패 (상태 코드: {response.status_code})")
                return
                
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")
            
            news_list = []
            for item in items:
                pub_date_str = item.pubDate.text
                try:
                    pub_date = email.utils.parsedate_to_datetime(pub_date_str)
                except Exception as e:
                    continue
                    
                if pub_date >= cutoff_date:
                    clean_title = item.title.text.replace(' - Google 검색', '')
                    news_list.append({
                        "title": clean_title,
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "link": item.link.text
                    })
            
            if news_list:
                unique_news = []
                seen_titles = set()
                for n in news_list:
                    if n['title'] not in seen_titles:
                        seen_titles.add(n['title'])
                        unique_news.append(n)
                        
                # 2안 적용: 규제 동향은 상위 2개, 일반 경쟁사는 상위 3개로 엄격히 제한하여 AI 토큰 부담(쏠림 현상) 방지
                limit = 2 if name.startswith("규제:") else 3
                crawled_data[name] = unique_news[:limit] 
            else:
                print(f"[{name}] 기간 내 조건에 맞는 기사 없음 (총 검색 기사 수: {len(items)})")
                
        except Exception as e:
            print(f"[{name}] 크롤링 완전 실패: {e}")
