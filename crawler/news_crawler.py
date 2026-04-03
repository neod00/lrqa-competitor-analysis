import requests
from bs4 import BeautifulSoup
import datetime
from urllib.parse import quote
import yaml

class NewsCrawler:
    def __init__(self, days_ago=7):
        # 수집할 기간 설정 (기본값: 최근 7일)
        self.days_ago = days_ago
        with open("config.yaml", "r", encoding="utf-8") as f:
            self.competitors = yaml.safe_load(f)["crawling"]["competitors"]

    def fetch_latest_news(self):
        crawled_data = {}
        # 현재 기준 며칠 전의 날짜 계산 (새벽 시간대 고려)
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=self.days_ago)

        for key, name in self.competitors.items():
            print(f"[{name}] 뉴스 검색 중...")
            # 검색어: 경쟁사명 + 마케팅/비즈니스 관련 핵심 키워드
            query = f'"{name}" (인증 OR 심사 OR 세미나 OR 웨비나 OR 협약 OR MOU OR 교육)'
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
            
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")
                
                news_list = []
                for item in items:
                    pub_date_str = item.pubDate.text
                    
                    # RSS 날짜 변환 (예: Thu, 04 Apr 2026 07:00:00 GMT)
                    try:
                        pub_date = datetime.datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                        pub_date = pub_date.replace(tzinfo=datetime.timezone.utc) # UTC 지정
                    except ValueError:
                        continue
                        
                    # 지정한 최근 N일 이내의 기사만 필터링
                    if pub_date >= cutoff_date:
                        news_list.append({
                            "title": item.title.text,
                            "date": pub_date.strftime("%Y-%m-%d"),
                            "link": item.link.text
                        })
                
                if news_list:
                    # 상위 5개 기사까지만 AI에 전달하여 토큰 낭비 방지
                    crawled_data[name] = news_list[:5] 
                    
            except Exception as e:
                print(f"[{name}] 크롤링 실패: {e}")
        
        return crawled_data
