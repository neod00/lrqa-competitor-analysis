import json
import os

import httpx
import yaml
from dotenv import load_dotenv
from openai import OpenAI


class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        # 사내 SSL/방화벽 환경에서 인증서 검증 문제가 생기는 경우를 우회합니다.
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(api_key=self.api_key, http_client=http_client)

        with open("config.yaml", "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["ai"]

    def generate_report(self, crawled_data):
        if not self.api_key:
            return {"error": "OpenAI API Key가 설정되지 않았습니다."}

        prompt = f"""
당신은 LRQA의 마케팅 전략 분석가입니다.
아래 수집 데이터를 바탕으로 최근 30일간 경쟁사 활동과 규제 동향을 분석해 주요 인사이트를 추출하세요.
결과는 반드시 아래 JSON 스키마를 정확히 지켜 반환해야 합니다. HTML은 포함하지 마세요.

[수집 데이터]
{json.dumps(crawled_data, ensure_ascii=False, indent=2)}

[요청 JSON 구조]
{{
  "global_competitors": [
    {{
      "competitor": "경쟁사 이름 (예: TUV SUD)",
      "activity_type": "활동 요약 (예: 규제 대응 / MOU / 교육 / 인증 서비스)",
      "details": "본문 내용을 2~4문장으로 요약하고 LRQA 관점의 의미를 포함",
      "date": "기사 발행일 (예: 2026-04-01)",
      "link": "해당 기사 또는 원문 링크 URL",
      "threat_score": "위협도 (높음/보통/낮음 중 하나)"
    }}
  ],
  "local_competitors": [
    {{
      "competitor": "기관 이름 (예: 한국표준협회)",
      "activity_type": "활동 요약",
      "details": "본문 내용을 2~4문장으로 요약하고 LRQA 관점의 의미를 포함",
      "date": "기사 발행일 (예: 2026-04-01)",
      "link": "해당 기사 또는 원문 링크 URL",
      "threat_score": "위협도 (높음/보통/낮음 중 하나)"
    }}
  ],
  "regulations": [
    {{
      "keyword": "규제 키워드 (예: CBAM 동향)",
      "title": "규제 관련 기사 제목",
      "details": "기사 내용과 시장 영향을 요약",
      "date": "기사 발행일 (예: 2026-04-01)",
      "link": "원문 링크",
      "threat_score": "위협도 (높음/보통/낮음 중 하나)"
    }}
  ],
  "insights": [
    "인사이트 1: LRQA 영업/마케팅 관점의 구체적인 대응 제안",
    "인사이트 2: ..."
  ]
}}

[필수 지침]
1. 수집 데이터의 개별 뉴스 기사 각각을 독립적인 JSON 객체 1개로 작성하세요. 여러 기사를 하나로 묶지 마세요.
2. 개별 기사마다 `link`와 `date` 값을 반드시 포함하세요.
3. 이름이 "규제: ~" 형태인 데이터는 경쟁사 배열이 아니라 `regulations` 배열에 넣으세요.
4. `threat_score`는 반드시 "높음", "보통", "낮음" 중 하나만 사용하세요.
5. 단순 홍보성 글은 "낮음", 실질적인 신규 서비스/시장 진입/대형 협약은 "높음"으로 판단하세요.
6. 글로벌 경쟁사와 국내 기관을 정확히 구분하세요.
   - 글로벌 경쟁사: DNV, BSI, SGS, BV, Bureau Veritas, TUV SUD, TUV Rheinland, Intertek, DQS 등
   - 국내 주요 기관: 한국표준협회, 한국품질재단, 한국경영인증원, 한국생산성본부인증원 등
7. 규제 동향은 CBAM, ESG/CSRD, AI, 사이버보안, 공급망 실사 등 주제가 고르게 나오도록 구성하세요.
8. 해당 카테고리에 유효한 기사가 없으면 빈 배열을 반환하세요.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": "You are a helpful marketing analyst. You must output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config["temperature"],
                response_format={"type": "json_object"},
            )

            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)

        except Exception as e:
            print(f"AI 분석 중 오류 발생: {e}")
            return {"error": f"AI 분석 중 오류 발생: {e}"}
