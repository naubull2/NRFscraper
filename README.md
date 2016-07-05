# NRFscraper (연구과제 공고 게시판 알림)

## Prerequisites
다음의 Python 패키지를 사용합니다.
- schedule
- smtplib
- lxml
- email

## Usage
Python 스케쥴러로 한 시간 마다 게시판들을 확인하여 당일 올라온 게시물을 스크랩 해둡니다.
스크랩해둔 게시물은 매일 지정해주는 시간에 지정한 관리자 메일로 보내주고 다시 새로 올라오는 게시물을 스크랩합니다.
- 본 코드는 게시물 제목만 긁어오기 때문에 과제 확인은 본인이 직접 해야합니다!
사용법은 다음과 같이 실행만 해주면 됩니다.
'''sh
python NRFscrap.py links.txt 10:00 admin@your.mail.domain
'''
- 시간 포맷은 24시간 표기로 사용합니다.
- 실행 전에 NRFscrap.py를 본인 환경에 맞게 설정 하셔야 합니다.

## Configuration 
- links.txt에 확인 하고 싶은 과제 공고 게시판 주소를 한 줄에 한개씩 저장합니다.
- NRFscrap.py의 job 함수에 새로 추가한 게시판 주소에서 과제 제목, 날짜 등 필요한 내용을 수집하는 코드를 추가해줍니다.
- 기본적으로 제공하는 게시판은 한국연구재단, 국가 R&D 사업관리, 정보통신기술진흥센터, 한국전자통신연구원, 서울대학교 산학협력단 공고 게시판입니다.
- 코드에 포함된 내용을 참고하시면 어렵지 않게 다른 게시판도 추가 할 수 있습니다.

- notify 함수
    - 'SUBJECT': 받을 메일 제목
    - 'TEXT': 받을 메일 내용
    - 'server': smtplib.SMTP 의 host와 port를 사용하는 메일 서버로 설정

## Built For
- Python - 2.7
  

