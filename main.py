import datetime
from mailer.sender import EmailSender
from analyzer.ai_analyzer import AIAnalyzer

def main():
    print("🚀 경쟁사 분석 자동화 스크립트 시작")
    
    # 1. 크롤링 (현재는 테스트를 위해 임시 데이터 사용. 추후 실제 크롤러 연동)
    print("⏳ 웹 크롤링 중...")
    mock_crawled_data = {
        "DNV": [{"title": "식품업계 대상 무료 웨비나 개최", "date": "2024-04-10", "type": "세미나"}],
        "TÜV SÜD": [{"title": "EU 포장재 규정(PPWR) 대응 세미나", "date": "2024-04-12", "type": "규제대응"}],
        "KSA": [{"title": "공공기관 ESG 가이드라인 전략", "date": "2024-04-15", "type": "정책"}],
    }
    
    # 2. AI 분석 및 HTML 생성
    print("🤖 AI 분석 및 보고서 생성 중...")
    analyzer = AIAnalyzer()
    
    # 프롬프트 처리로 인해 약 10~20초 소요 가능
    html_report = analyzer.generate_report(mock_crawled_data)
    
    if "오류 발생" in html_report:
        print("❌ AI 분석 중 문제가 생겼습니다. API 키를 확인해주세요.")
        return
        
    print("✅ AI 기반 보고서 HTML 완성")
    
    # 3. 이메일 발송
    today = datetime.date.today().strftime("%Y.%m.%d")
    subject = f"일일 보고서 ({today})"
    
    print("📧 이메일 발송 중...")
    mailer = EmailSender()
    success = mailer.send_report(subject, html_report)
    
    if success:
        print("🎉 성공적으로 컴파일 및 메일 발송을 마쳤습니다.")
    else:
        print("❌ 이메일 발송에 실패했습니다. 이메일 앱 비밀번호 설정을 확인하세요.")

if __name__ == "__main__":
    main()
