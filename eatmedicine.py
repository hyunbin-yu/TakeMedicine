from flask import Flask
import requests
import time

class Smeal:  # Smeal 클래스 생성
    def __init__(self, ooe, code, sclass):  # 초기화자 메서드 선언 (기본학교정보설정)
        city_dict = {"서울": "sen.go.kr", "부산": "pen.go.kr", "대구": "dge.go.kr",
                     "인천": "ice.go.kr", "광주": "gen.go.kr", "대전": "dje.go.kr",
                     "울산": "use.go.kr", "세종": "sje.go.kr", "경기": "goe.go.kr",
                     "강원": "kwe.go.kr", "충북": "cbe.go.kr", "충남": "cne.go.kr",
                     "전북": "jbe.go.kr", "전남": "jne.go.kr", "경북": "gbe.kr",
                     "경남": "gne.go.kr", "제주": "jje.go.kr"}  # 학교 목록

        self.ooe = city_dict.get(ooe, "nocity")
        self.sclass = sclass  # 교급
        self.code = code  # 학교 고유 코드

    def day(self, yeon, dal, il, kind):  # 하루치 급식을 조회
        if type(self.ooe) != str or type(yeon) != str or type(self.sclass) != str\
                or type(kind) != str or type(self.code) != str or type(dal) != str\
                or type(il) != str:  # 문자열 형식으로 올바르게 받았는지 확인하는 코드
            return("TYPE ERROR")

        if len(yeon) != 4 or len(dal) != 2 or len(il) != 2\
                or len(self.sclass) != 1 or len(kind) != 1:  # 길이가 알맞는지 확인하는 코드
            return("SIZE ERROR")

        if self.ooe == "nocity":
            return("OFFICE ERROR")

        ymd = yeon + "." + dal + "." + il  # 년도 조합

        url = "http://stu." + self.ooe + "/sts_sci_md01_001.do"  # 나이스 급식 조회 주소
        para = {
            "schulCode": self.code,  # 학교 코드
            "schulCrseScCode": self.sclass,  # 교급
            "schulKnaScCode": "0" + self.sclass,  # 교급
            "schMmealScCode": kind,  # 식단 종류
            "schYmd": ymd  # 조회년월일
        }

        response = requests.get(url, params=para)  # 급식 정보 조회
        if int(response.status_code) != 200:  # 응답이 200 (정상응답)이 아닐경우
            return('SERVER ERROR')  # 에러 반환

        foodhtml = BeautifulSoup(response.text, 'html.parser')  # 급식정보 파싱 준비
        foodhtml_data_tr = foodhtml.find_all('tr')  # 모든 tr태그 불러오기

        # 몇번째 행에 급식 정보가 존재하는지 구분하는 로직

        foodhtml_data = foodhtml_data_tr[0].find_all('th')  # 날짜 정보가 있는 열을 불러옴

        try:  # 예외 처리를 위한 try
            for i in range(1, 7):  # 월요일부터 일요일까지 하나하나 대입 준비
                date = str(foodhtml_data[i])  # i요일째 날짜 정보 확인
                date_filter = ['<th class="point2" scope="col">', '<th class="last point1" scope="col">',
                               '<th scope="col">', '</th>', '(', ')', '일', '월', '화', '수', '목', '금', '토']  # 제거해야 하는 목록

                for sakje in date_filter:
                    date = date.replace(sakje, '')  # 찌끄레기를 삭제

                if date != ymd:  # 날짜와 입력날짜 동일 여부 확인
                    continue

                hang = i - 1  # 급식정보가 존재하는 행 선언
                break  # 존재 확인 로직 정지

        except:  # 에러 발생시 데이터베이스 에러 반환
            return("NO DATABASE")

        # 급식 정보 조회 시작

        try:
            food = foodhtml_data_tr[2].find_all(
                'td')  # 급식정보가 있는 행의 모든 td 태그 불러오기
            food = str(food[hang])  # hang 번째에 있는 급식 정보 불러옴

            food_filter = ['<td class="textC">',
                           '<td class="textC last">', '</td>']  # 제거해야 하는 목록

            for sakje in food_filter:
                food = food.replace(sakje, '')  # 찌끄레기를 삭제

            if food == ' ':
                food = '급식이 예정되지 않았거나 정보가 존재하지 않습니다.'  # 만약 조회시 급식정보가 없다면 미존재 안내

        except:
            food = 'NO DATABASE'  # 급식 조회 실패시 안내

        return(food)  # 정보 반환

    def month(self, yeon, dal, kind, output):  # 한달치 급식을 조회
        # 조회하는 월의 마지막 날 구하는 로직
        if dal == '02':  # 2월 조회시
            if int(yeon) % 4 == 0 and int(yeon) % 100 != 0:  # 윤년일 경우 29일이 마지막
                last_day = 29
            elif int(yeon) % 400 == 0:
                last_day = 29
            else:  # 아니면 28이 마지막
                last_day = 28
        elif dal == '01' or dal == '03' or dal == '05' or dal == '07' or dal == '08' or dal == '10' or dal == '12':  # 끝날이 31일 목록
            last_day = 31
        else:  # 이외는 모두 30일이 마지막
            last_day = 30

        if output == "e":  # 엑셀 저장 기능
            op = openpyxl.Workbook()
            ex = op.active

            try:  # 예외 처리를 위한 try문
                for i in range(1, last_day + 1):  # 한달치 모두 대입하는 반복문
                    if i < 10:  # 일 정보가 10 미만일때
                        i = str(i)
                        i = "0" + i  # 매개변수 입력 규칙에 의거 두자리로 변환

                    i = str(i)

                    meal = self.day(yeon, dal, i, kind)  # 급식 정보 불러옴
                    ex.cell(row=int(i), column=1).value = yeon + \
                        "년" + dal + "월" + i + "일"  # 날짜 정보 엑셀 삽입
                    ex.cell(row=int(i), column=2).value = meal  # 급식 정보 삽입

                op.save(self.code + "_" + yeon + "년 " + dal + "월" + ".xlsx")
                op.close
                return("SUCCEED")

            except:  # 실패시 실패 에러 안내
                op.close()  # 엑셀 닫기
                return("EXCEL ERROR")

       
# ~~ 3. 학교 학사일정을 불러오는 api ~~

class Scalendar:  # Scalendar 클래스 생성
    def __init__(self, ooe, code, sclass):  # 초기화자 선언
        city_dict = {"서울": "sen.go.kr", "부산": "pen.go.kr", "대구": "dge.go.kr",
                     "인천": "ice.go.kr", "광주": "gen.go.kr", "대전": "dje.go.kr",
                     "울산": "use.go.kr", "세종": "sje.go.kr", "경기": "goe.go.kr",
                     "강원": "kwe.go.kr", "충북": "cbe.go.kr", "충남": "cne.go.kr",
                     "전북": "jbe.go.kr", "전남": "jne.go.kr", "경북": "gbe.kr",
                     "경남": "gne.go.kr", "제주": "jje.go.kr"}  # 학교 목록

        self.ooe = city_dict.get(ooe, "nocity")
        self.sclass = sclass  # 교급
        self.code = code  # 학교 고유 코드

    def month(self, yeon, dal):
        if type(self.ooe) != str or type(yeon) != str or type(self.sclass) != str\
                or type(yeon) != str or type(self.code) != str or type(dal) != str:  # 문자열 형식으로 올바르게 받았는지 확인하는 코드
            return("TYPE ERROR")

        if len(yeon) != 4 or len(dal) != 2 or len(self.sclass) != 1:  # 길이가 알맞는지 확인하는 코드
            return("SIZE ERROR")

        if self.ooe == "nocity":
            return("OFFICE ERROR")

        try:
            url = "http://stu." + self.ooe + "/sts_sci_sf01_001.do"  # 월간 계획 주소
            para = {
                "schulCode": self.code,  # 학교코드
                "schulCrseScCode": self.sclass,  # 교급
                "schulKndScCode": "0" + self.sclass,  # 교급
                "ay": yeon,  # 조회년도
                "mm": dal  # 조회월
            }

            re = requests.get(url, params=para)  # 나이스 학사일정 조회
            if int(re.status_code) != 200:  # 비정상 접속시 에러 반환
                return("SERVER ERROR")

            html = BeautifulSoup(re.text, 'html.parser')  # 파싱 준비
            html = html.find_all('td')  # td(테이블 구분) 태그만 불러옴

            html_size = len(html)  # 몇줄 있는지 확인
            calendar = {}

            for i in range(0, html_size):  # 날짜 및 일정 내용 분류
                html_date = str(html[i].find('em'))  # 날짜 정보 빼오기
                html_body = str(html[i].find('strong'))  # 일정 정보 빼오기

                for sakje in ['<em>', '</em>', '<em class="point2">']:
                    html_date = html_date.replace(sakje, '')  # html 태그 제거

                for sakje in ['<strong>', '</strong>']:
                    html_body = html_body.replace(sakje, '')  # html 태그 제거

                if html_body == "None":  # 학사일정 미 존재시
                    html_body = "학사일정이 존재하지 않습니다."  # 안내멘트

                if html_date == "":  # 날짜정보 미 존재시
                    continue  # 반복문 탈출

                calendar[html_date] = html_body  # 딕셔너리 추가

        except:
            calendar = "NO DATABASE"  # 에러 전달

        return(calendar)  # 반환

app = Flask(__name__)

@app.route('/meal', methods=['POST'])
def meal():
    c = Smeal("대전", "G100000202", time.strftime('%m', time.localtime(time.time())))
    return c.month("2022", time.strftime('%m', time.localtime(time.time())))[time.strftime('%d', time.localtime(time.time()))]
