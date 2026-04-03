import datetime
from mailer.sender import EmailSender
from analyzer.ai_analyzer import AIAnalyzer
from crawler.news_crawler import NewsCrawler

def main():
    print("🚀 경쟁사 분석 웹 크롤링 자동화 시작")
    
    # 1. 실제 인터넷 웹 크롤링 (최근 30일 기준)
    print("⏳ 인터넷에서 뉴스기사 수집 중 (최근 30일)...")
    crawler = NewsCrawler(days_ago=30)
    crawled_data = crawler.fetch_latest_news()
    
    if not crawled_data:
        print("❌ 최근 30일 내에 검색된 기사가 전혀 없습니다.")
        crawled_data = {"안내": [{"title": "검색 결과 없음. 최근 30일 내 경쟁사의 주요 홍보 활동이 포착되지 않았습니다.", "date": datetime.date.today().strftime("%Y-%m-%d")}]}
        
    # 2. AI 분석 및 HTML 생성
    print("🤖 AI 분석 및 보고서 생성 중...")
    analyzer = AIAnalyzer()
    
    html_report = analyzer.generate_report(crawled_data)
    
    if "오류 발생" in html_report:
        print("❌ AI 분석 중 문제가 생겼습니다.")
        return
        
    print("✅ AI 기반 보고서 코딩 완료!")
    
    # 3. 이메일 발송
    today = datetime.date.today().strftime("%Y.%m.%d")
    subject = f"일일 분석 보고서 ({today})"
    
    print("📧 이메일 발송 중...")
    mailer = EmailSender()
    success = mailer.send_report(subject, html_report)
    
    if success:
        print("🎉 모든 작업이 끝났습니다.")
    else:
        print("❌ 이메일 전송 에러.")

if __name__ == "__main__":
    main()
