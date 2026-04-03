import datetime
from mailer.sender import EmailSender
from analyzer.ai_analyzer import AIAnalyzer
from crawler.news_crawler import NewsCrawler

def main():
    print("🚀 경쟁사 분석 자동화 스크립트 시작")
    
    # 1. 실제 구글 뉴스 검색 크롤링 (최근 7일 기준)
    print("⏳ 실제 인터넷 웹 크롤링 중 (최근 7일 동향)...")
    crawler = NewsCrawler(days_ago=7)
    crawled_data = crawler.fetch_latest_news()
    
    if not crawled_data:
        print("❌ 최근 7일 내에 검색된 경쟁사 기사가 없습니다.")
        # 빈 결과도 보고서로 보내려면 아래 리턴을 주석처리하면 됩니다.
        crawled_data = {"안내": [{"title": "최근 7일 내 경쟁사의 주요 언론 홍보 활동이 검색되지 않았습니다.", "date": datetime.date.today().strftime("%Y-%m-%d")}]}
        
    # 2. AI 분석 및 HTML 생성
    print("🤖 AI 분석 및 보고서 생성 중...")
    analyzer = AIAnalyzer()
    
    # 프롬프트 처리로 인해 약 10~30초 소요 가능
    html_report = analyzer.generate_report(crawled_data)
    
    if "오류 발생" in html_report:
        print("❌ AI 분석 중 문제가 생겼습니다. API 키를 확인해주세요.")
        return
        
    print("✅ AI 기반 보고서 HTML 완성")
    
    # 3. 이메일 발송
    today = datetime.date.today().strftime("%Y.%m.%d")
    subject = f"일일 분석 보고서 ({today})"
    
    print("📧 이메일 발송 중...")
    mailer = EmailSender()
    success = mailer.send_report(subject, html_report)
    
    if success:
        print("🎉 성공적으로 분석 요약 및 메일 발송을 마쳤습니다.")
    else:
        print("❌ 이메일 발송에 실패했습니다.")

if __name__ == "__main__":
    main()
