"""
네이버 뉴스 API를 사용하여 뉴스 기사를 수집하는 모듈
"""
import requests
import pandas as pd
from datetime import datetime
import time
import re


def clean_html(text):
    """HTML 태그 및 특수문자 제거"""
    if not text:
        return ""
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # HTML 엔티티 변환
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    return text.strip()


def collect_naver_news(client_id, client_secret, query, start_date, end_date, max_results=1000):
    """
    네이버 뉴스 API를 사용하여 뉴스 기사 수집
    
    Parameters:
    -----------
    client_id : str
        네이버 API Client ID
    client_secret : str
        네이버 API Client Secret
    query : str
        검색 키워드
    start_date : str
        시작일 (YYYY-MM-DD)
    end_date : str
        종료일 (YYYY-MM-DD)
    max_results : int
        최대 수집 건수
        
    Returns:
    --------
    pd.DataFrame
        수집된 뉴스 데이터
    """
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    base_url = "https://openapi.naver.com/v1/search/news.json"
    
    # 날짜 변환
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = []
    total_collected = 0
    
    # 100건씩 페이징하여 수집
    for start in range(1, max_results + 1, 100):
        if total_collected >= max_results:
            break
            
        params = {
            "query": query,
            "display": min(100, max_results - total_collected),
            "start": start,
            "sort": "date"
        }
        
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    break  # 더 이상 결과가 없으면 중단
                
                for item in items:
                    try:
                        # 날짜 파싱 (예: "Mon, 01 Nov 2025 10:30:00 +0900")
                        pub_dt = datetime.strptime(item["pubDate"], "%a, %d %b %Y %H:%M:%S %z")
                        pub_date_naive = pub_dt.replace(tzinfo=None)
                        
                        # 날짜 범위 확인
                        if not (start_dt <= pub_date_naive <= end_dt):
                            continue
                        
                        results.append({
                            "type": "naver_news",
                            "title": clean_html(item.get("title", "")),
                            "description": clean_html(item.get("description", "")),
                            "link": item.get("link", ""),
                            "originallink": item.get("originallink", ""),
                            "pubDate": pub_date_naive.strftime("%Y-%m-%d %H:%M:%S"),
                            "source": None,
                            "author": None
                        })
                        
                        total_collected += 1
                        
                    except Exception as e:
                        print(f"항목 처리 중 오류: {e}")
                        continue
                
                # API 제한 준수를 위한 대기
                time.sleep(0.1)
                
            elif response.status_code == 429:
                print("API 호출 한도 초과. 잠시 대기 중...")
                time.sleep(1)
                continue
                
            else:
                error_msg = f"API 오류 (status {response.status_code}): {response.text}"
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            print("요청 시간 초과. 다시 시도 중...")
            time.sleep(1)
            continue
            
        except Exception as e:
            raise Exception(f"네이버 API 호출 중 오류 발생: {str(e)}")
    
    if not results:
        return pd.DataFrame(columns=["type", "title", "description", "link", "originallink", 
                                     "pubDate", "source", "author"])
    
    df = pd.DataFrame(results)
    return df


def validate_api_key(client_id, client_secret):
    """
    네이버 API 키 유효성 검증
    
    Returns:
    --------
    tuple
        (성공 여부, 메시지)
    """
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    base_url = "https://openapi.naver.com/v1/search/news.json"
    params = {
        "query": "테스트",
        "display": 1
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            return True, "✅ 네이버 API 키가 유효합니다."
        elif response.status_code == 401:
            return False, "❌ 네이버 API 키가 유효하지 않습니다."
        else:
            return False, f"❌ API 오류 (status {response.status_code})"
            
    except Exception as e:
        return False, f"❌ API 연결 실패: {str(e)}"
