import requests
from bs4 import BeautifulSoup
import datetime
from urllib.parse import quote
import yaml
import email.utils

class NewsCrawler:
    def __init__(self, days_ago=30):
        self.days_ago = days_ago
        with open("config.yaml", "r", encoding="utf-8") as f:
            self.competitors = yaml.safe_load(f)["crawling"]["competitors"]

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
            
            # 검색어 최적화
            query = f'"{name}" 인증 OR 세미나 OR 협약'
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
            
            try:
                # 위장한 header 씌워서 요청 보내기
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"[{name}] 구글 뉴스 접속 실패 (상태 코드 막힘: {response.status_code})")
                    continue
                    
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")
                
                news_list = []
                for item in items:
                    pub_date_str = item.pubDate.text
                    try:
                        # 핵심 해결 2. 에러가 잦은 strptime 대신 강력한 이메일 표준 날짜 해석기 사용
                        pub_date = email.utils.parsedate_to_datetime(pub_date_str)
                    except Exception as e:
                        print(f"날짜 파싱 건너뜀: {e}")
                        continue
                        
                    if pub_date >= cutoff_date:
                        clean_title = item.title.text.replace(' - Google 검색', '')
                        news_list.append({
                            "title": clean_title,
                            "date": pub_date.strftime("%Y-%m-%d"),
                            "link": item.link.text
                        })
                
                if news_list:
                    # 중복 기사 필터링
                    unique_news = []
                    seen_titles = set()
                    for n in news_list:
                        if n['title'] not in seen_titles:
                            seen_titles.add(n['title'])
                            unique_news.append(n)
                            
                    crawled_data[name] = unique_news[:5] 
                else:
                    print(f"[{name}] 기간 내 조건에 맞는 기사 없음 (총 검색된 기사 수: {len(items)})")
                    
            except Exception as e:
                print(f"[{name}] 크롤링 완전 실패: {e}")
        
        return crawled_data
