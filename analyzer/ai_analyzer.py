import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import yaml

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        
        with open("config.yaml", "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["ai"]

    def generate_report(self, crawled_data):
        """크롤링 데이터를 기반으로 AI 마케팅 분석 보고서(HTML) 생성"""
        
        if not self.api_key:
            return "<p>OpenAI API Key가 설정되지 않았습니다.</p>"

        prompt = f"""
당신은 LRQA의 마케팅 전략 분석가입니다.
아래 크롤링된 경쟁사들의 최근 활동을 분석하여 이메일 보고서를 HTML 로 작성해주세요.

[크롤링 데이터]
{json.dumps(crawled_data, ensure_ascii=False, indent=2)}

[요구사항]
1. 모바일 이메일 클라이언트에서 보기 좋은 깔끔하고 세련된 HTML 테이블, 반응형 형식으로 작성.
2. 내용은 다음 3가지를 포함:
   - 글로벌 경쟁사 주요 활동
   - 국내 주요 기관 활동
   - 핵심 마케팅 인사이트 및 LRQA 대응 전략 제안
3. ```html ``` 마크다운 블록 코드 태그는 제거하고, <html> 태그나 <body> 태그 없이 바로 <div>로 시작하는 내용만 출력할 것.
4. CSS를 인라인으로 작성하여 이메일 클라이언트에서 스타일이 깨지지 않도록 할 것.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": "You are a helpful marketing analyst and HTML output generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config["temperature"],
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI 분석 중 오류 발생: {e}")
            return f"<p>AI 분석 중 오류 발생: {e}</p>"
