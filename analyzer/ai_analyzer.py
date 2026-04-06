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
      "details": "세부 내용 설명 요약"
    }}
  ],
  "local_competitors": [
    {{
      "competitor": "기관이름 (예: 한국표준협회)",
      "activity_type": "활동 요약",
      "details": "세부 내용 설명 요약"
    }}
  ],
  "insights": [
    "인사이트 1: ... LRQA 대응 전략 제안 ...",
    "인사이트 2: ... LRQA 대응 전략 제안 ..."
  ]
}}

주의: 해당 기관의 기사가 없다면 배열을 비워두세요.
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
