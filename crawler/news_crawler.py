import requests
from bs4 import BeautifulSoup
import datetime
from urllib.parse import quote
import yaml

class NewsCrawler:
    def __init__(self, days_ago=30):
        # 수집할 기간 기본값: 최근 30일로 확장
        self.days_ago = days_ago
        with open("config.yaml", "r", encoding="utf-8") as f:
            self.competitors = yaml.safe_load(f)["crawling"]["competitors"]

    def fetch_latest_news(self):
        crawled_data = {}
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=self.days_ago)

        for key, name in self.competitors.items():
            print(f"[{name}] 구글 뉴스 검색 중...")
            
            # 검색 조건 완화: 괄호와 따옴표를 빼서 더 유연하게 탐색
            query = f'{name} 인증 OR 세미나 OR 협약 OR 심사'
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
            
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")
                
                news_list = []
                for item in items:
                    pub_date_str = item.pubDate.text
                    try:
                        pub_date = datetime.datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                        pub_date = pub_date.replace(tzinfo=datetime.timezone.utc)
                    except ValueError:
                        continue
                        
                    if pub_date >= cutoff_date:
                        # ' - Google 검색' 같은 의미 없는 꼬리표 타이틀에서 제거
                        clean_title = item.title.text.replace(' - Google 검색', '')
                        news_list.append({
                            "title": clean_title,
                            "date": pub_date.strftime("%Y-%m-%d"),
                            "link": item.link.text
                        })
                
                if news_list:
                    # 중복 뉴스가 검색되는 것을 방지
                    unique_news = []
                    seen_titles = set()
                    for n in news_list:
                        if n['title'] not in seen_titles:
                            seen_titles.add(n['title'])
                            unique_news.append(n)
                            
                    crawled_data[name] = unique_news[:5] 
            except Exception as e:
                print(f"[{name}] 크롤링 실패: {e}")
        
        return crawled_data
