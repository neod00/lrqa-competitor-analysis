from jinja2 import Environment, FileSystemLoader


dummy_data = {
    "global_competitors": [],
    "local_competitors": [],
    "regulations": [],
    "insights": [],
}

try:
    with open("dummy.json", "r", encoding="utf-8"):
        # 이전 분석 결과 파일을 붙여 넣어 테스트할 수 있도록 남겨둔 자리입니다.
        ai_result_json = dummy_data
except FileNotFoundError:
    ai_result_json = dummy_data

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("email_template.html")
html_report = template.render(data=ai_result_json)

with open("preview_report_banner.html", "w", encoding="utf-8") as f:
    f.write(html_report)

print("배너 테스트용 HTML 생성 완료")
