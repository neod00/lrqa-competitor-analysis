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
      "date": "기사 발행일 (예: 2026-04-01)",
      "link": "해당 기사의 원본 링크 URL",
      "threat_score": "위협도 (높음/보통/낮음 중 택1)"
    }}
  ],
  "local_competitors": [
    {{
      "competitor": "기관이름 (예: 한국표준협회)",
      "activity_type": "활동 요약",
      "details": "세부 내용 설명 요약",
      "date": "기사 발행일 (예: 2026-04-01)",
      "link": "해당 기사의 원본 링크 URL",
      "threat_score": "위협도 (높음/보통/낮음 중 택1)"
    }}
  ],
  "regulations": [
    {{
      "keyword": "규제 키워드 (예: CBAM 동향)",
      "title": "규제 관련 기사 제목",
      "details": "기사 세부 영향도 요약",
      "date": "기사 발행일 (예: 2026-04-01)",
      "link": "원문 링크",
      "threat_score": "위협도 (높음/보통/낮음 중 택1)"
    }}
  ],
  "insights": [
    "인사이트 1: ... 영업 타겟팅(Actionable) 관점의 구체적인 제안 ...",
    "인사이트 2: ..."
  ]
}}

[필수 주의사항]
1. 수집된 크롤링 데이터의 **개별 뉴스 기사 각각을 독립적인 1개의 JSON 객체(배열 요소)**로 생성하세요.
2. 특정 기관의 기사가 3개라면, 해당 기관의 객체도 배열 내에 3개가 있어야 합니다. 여러 기사를 하나의 항목으로 뭉뚱그려 요약하지 마세요.
3. 개별 기사의 `link`와 `date` 값을 꼭 포함하세요.
4. 각 기사가 LRQA의 비즈니스(시장 점유율, 경쟁 상황 등)에 미치는 파급력을 평가하여 `threat_score`를 **"높음"**, **"보통"**, **"낮음"** 중 하나로 작성해 주세요. (예: 단순 파트너십은 낮음, 신제품/독점계약은 높음)
5. 크롤링 데이터 중 이름이 "규제: ~" 형태로 들어온 데이터는 경쟁사 배열이 아닌 `regulations` 배열에 따로 담아주세요.
6. 해당 카테고리의 기사가 아예 없다면 배열을 비워두세요.
7. (매우 중요) 규제 동향에 다양한 주제(CBAM, ESG, AI 등)가 포함된 경우, 특정 주제(예: CBAM)에만 편중되지 않도록 제공된 모든 주제가 골고루 표출되게 주의해서 배열을 구성하세요.
8. (매우 중요) 글로벌 경쟁사(`global_competitors`)와 국내 기관(`local_competitors`)을 엄격히 구분하세요.
   - **글로벌 경쟁사:** DNV, BSI, SGS, BV, TÜV SÜD, Intertek
   - **국내 주요 기관:** 한국표준협회, 한국품질재단, 한국경영인증원, 한국생산성본부인증원 등 한국어 이름 기관
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
