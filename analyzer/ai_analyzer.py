import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import yaml

import httpx

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        # SSL 방화벽 우회를 위한 httpx 클라이언트
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(api_key=self.api_key, http_client=http_client)
        
        with open("config.yaml", "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["ai"]

    def generate_report(self, crawled_data):
        if not self.api_key:
            return "<p>OpenAI API Key가 설정되지 않았습니다.</p>"

        prompt = f"""
당신은 LRQA의 마케팅 전략 분석가입니다.
아래 크롤링된 경쟁사들의 최근 30일 간의 활동을 분석하여 주요 인사이트를 추출해주세요.
결과는 반드시 아래의 JSON 포맷 형식을 정확히 지켜서 반환해야 합니다. HTML은 절대 포함하지 마세요.

[크롤링 데이터]
{json.dumps(crawled_data, ensure_ascii=False, indent=2)}

[요청하는 JSON 구조]
{{
  "global_competitors": [
    {{
      "competitor": "경쟁사이름 (예: TÜV SÜD)",
      "activity_type": "활동 요약 (예: 규제 대응 / MOU)",
      "details": "세부 내용 설명 요약",
      "link": "해당 기사의 원본 링크 URL (제공된 크롤링 데이터의 link 값 사용)"
    }}
  ],
  "local_competitors": [
    {{
      "competitor": "기관이름 (예: 한국표준협회)",
      "activity_type": "활동 요약",
      "details": "세부 내용 설명 요약",
      "link": "해당 기사의 원본 링크 URL (제공된 크롤링 데이터의 link 값 사용)"
    }}
  ],
  "insights": [
    "인사이트 1: ... LRQA 대응 전략 제안 ...",
    "인사이트 2: ... LRQA 대응 전략 제안 ..."
  ]
}}

[필수 주의사항]
1. 수집된 크롤링 데이터의 **개별 뉴스 기사 각각을 독립적인 1개의 JSON 객체(배열 요소)**로 생성하세요.
2. 특정 기관의 기사가 3개라면, 해당 기관의 객체도 배열 내에 3개가 있어야 합니다. 여러 기사를 하나의 항목으로 뭉뚱그려 요약하지 마세요.
3. 개별 기사의 `link` 값을 꼭 포함하여, 각 뉴스별로 원래 기사로 넘어갈 수 있도록 해야 합니다.
4. 해당 기관의 기사가 아예 없다면 배열을 비워두세요.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": "You are a helpful marketing analyst. You must output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config["temperature"],
                response_format={"type": "json_object"}
            )
            
            # JSON 텍스트를 파이썬 딕셔너리로 변환하여 반환
            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)
            
        except Exception as e:
            print(f"AI 분석 중 오류 발생: {e}")
            return {"error": f"AI 분석 중 오류 발생: {e}"}
