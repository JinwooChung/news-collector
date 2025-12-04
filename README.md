# 뉴스/유튜브 수집 시스템

특정 키워드와 기간으로 네이버 뉴스, 유튜브 영상 및 댓글을 수집하는 Streamlit 웹 애플리케이션입니다.

## 기능

- ✅ 네이버 뉴스 기사 수집
- ✅ 유튜브 영상 수집 (특정 언론사 채널)
- ✅ 유튜브 댓글 수집
- 📊 수집 결과 미리보기 및 CSV 다운로드

## 설치 방법

```bash
pip install -r requirements.txt
```

## 로컬 실행

```bash
streamlit run app.py
```

## Streamlit Cloud 배포

1. GitHub에 코드 업로드
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. "New app" 클릭
4. GitHub 저장소 연결
5. 배포 완료!

## API 키 발급

### 네이버 API
1. https://developers.naver.com/ 접속
2. 로그인 후 "애플리케이션 등록"
3. 애플리케이션 이름 입력
4. 사용 API: "검색" 선택
5. Client ID와 Client Secret 복사

### 유튜브 API
1. https://console.cloud.google.com/ 접속
2. 프로젝트 생성
3. "API 및 서비스" → "라이브러리"
4. "YouTube Data API v3" 검색 및 활성화
5. "사용자 인증 정보" → "API 키 만들기"

## 사용 방법

1. 웹 애플리케이션 접속
2. API 키 입력 (첫 사용 시 1회)
3. 검색 조건 입력:
   - 키워드
   - 시작일/종료일
   - 수집 대상 선택
4. "수집 시작" 클릭
5. 결과 확인 및 CSV 다운로드

## 주의사항

- 네이버 API: 하루 25,000건 제한
- 유튜브 API: 하루 10,000 units 제한
- 각자의 API 키를 사용하면 독립적인 한도 적용
