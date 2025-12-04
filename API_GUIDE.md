# API 키 발급 가이드

이 문서는 뉴스/유튜브 수집 시스템을 사용하기 위해 필요한 API 키를 발급받는 방법을 안내합니다.

## 📰 네이버 검색 API

### 1. 네이버 개발자 센터 접속
- 웹사이트: https://developers.naver.com/
- 네이버 계정으로 로그인

### 2. 애플리케이션 등록
1. 상단 메뉴에서 **"Application"** → **"애플리케이션 등록"** 클릭
2. **애플리케이션 정보 입력:**
   - 애플리케이션 이름: `뉴스수집시스템` (원하는 이름)
   - 사용 API: **"검색"** 선택 ✅
   - 비로그인 오픈 API 서비스 환경: **"WEB 설정"** 선택
   - 웹 서비스 URL: `http://localhost` (또는 실제 URL)

3. **등록** 버튼 클릭

### 3. API 키 확인
- 등록 완료 후 **"내 애플리케이션"** 페이지에서 확인
- **Client ID**: `abcdefghijklmnopqrst` (예시)
- **Client Secret**: `ABCdefGHI123` (예시)

### 4. 사용 제한
- **하루 호출 한도**: 25,000건
- **초당 호출 한도**: 10건

---

## 🎥 유튜브 Data API v3

### 1. Google Cloud Console 접속
- 웹사이트: https://console.cloud.google.com/
- Google 계정으로 로그인

### 2. 프로젝트 생성
1. 상단의 **프로젝트 선택** 드롭다운 클릭
2. **"새 프로젝트"** 클릭
3. 프로젝트 이름: `뉴스수집프로젝트` (원하는 이름)
4. **만들기** 클릭

### 3. YouTube Data API v3 활성화
1. 왼쪽 메뉴에서 **"API 및 서비스"** → **"라이브러리"** 클릭
2. 검색창에 `YouTube Data API v3` 검색
3. **YouTube Data API v3** 선택
4. **사용** 버튼 클릭

### 4. API 키 생성
1. 왼쪽 메뉴에서 **"API 및 서비스"** → **"사용자 인증 정보"** 클릭
2. 상단의 **"+ 사용자 인증 정보 만들기"** 클릭
3. **"API 키"** 선택
4. API 키가 생성됨 (예: `AIzaSyABC123def456GHI789jkl`)
5. **키 복사** 후 안전하게 보관

### 5. API 키 제한 설정 (선택사항, 보안 강화)
1. 생성된 API 키 옆의 **편집** 아이콘 클릭
2. **"API 제한사항"** 섹션에서:
   - **"키 제한"** 선택
   - **"YouTube Data API v3"** 만 선택
3. **저장** 클릭

### 6. 사용 제한
- **하루 할당량**: 10,000 units (무료)
- **API 호출 비용**:
  - 검색: 100 units
  - 영상 정보: 1 unit
  - 댓글 조회: 1 unit
- **예상 사용량**:
  - 영상 50개 검색 + 댓글 5,000개 수집 = 약 5,100 units

---

## 🔐 API 키 보안 주의사항

### ⚠️ 반드시 지켜야 할 사항
1. **API 키를 공개 저장소(GitHub 등)에 업로드하지 마세요**
2. API 키는 개인적으로 안전하게 보관하세요
3. 의심스러운 활동이 있다면 즉시 키를 재발급하세요

### 🔒 안전한 사용 방법
- Streamlit Cloud 배포 시: **Secrets** 기능 사용
- 로컬 개발 시: `.env` 파일에 저장 (`.gitignore`에 추가)
- 팀원들과 공유 시: 안전한 채널(이메일, 메신저) 사용

---

## 📞 문제 해결

### 네이버 API 오류
- **401 Unauthorized**: Client ID/Secret 확인
- **429 Too Many Requests**: 일일 한도 초과, 다음 날 재시도
- **500 Server Error**: 네이버 서버 문제, 잠시 후 재시도

### 유튜브 API 오류
- **400 Bad Request**: API 키 형식 확인
- **403 Forbidden**: 
  - API가 활성화되어 있는지 확인
  - 할당량 초과 시 다음 날 재시도 (자정 PST 기준 리셋)
- **404 Not Found**: 요청한 리소스가 존재하지 않음

---

## 💡 팁

### 할당량 절약 방법
1. **필요한 만큼만 수집**: 최대 건수를 적절히 설정
2. **언론사 채널 필터 사용**: 불필요한 검색 줄이기
3. **중복 수집 방지**: 같은 키워드를 여러 번 검색하지 않기

### 효율적인 사용
1. **테스트 시작**: 소량(10-20건)으로 먼저 테스트
2. **시간대 분산**: 여러 사용자가 있다면 사용 시간 분산
3. **결과 저장**: 수집한 데이터는 CSV로 저장하여 재사용

---

## 📚 참고 자료

- [네이버 개발자 센터 - 검색 API](https://developers.naver.com/docs/serviceapi/search/news/news.md)
- [YouTube Data API - 개요](https://developers.google.com/youtube/v3/getting-started)
- [YouTube Data API - 할당량](https://developers.google.com/youtube/v3/determine_quota_cost)
