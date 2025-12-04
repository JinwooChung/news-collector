"""
유튜브 API를 사용하여 영상 및 댓글을 수집하는 모듈
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
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
    text = text.replace('&#39;', "'")
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    return text.strip()


def convert_utc_to_kst(utc_time_str):
    """
    UTC 시간을 한국 시간대(KST, UTC+9)로 변환
    
    Parameters:
    -----------
    utc_time_str : str
        UTC 시간 문자열 (ISO 8601 형식, 예: "2025-11-25T10:30:00Z")
    
    Returns:
    --------
    str
        한국 시간대 문자열 (YYYY-MM-DD HH:MM:SS)
    """
    if not utc_time_str:
        return ""
    
    try:
        from datetime import datetime as dt, timedelta
        
        # UTC 시간 파싱 (Z 또는 +00:00 제거)
        utc_time_str = utc_time_str.replace('Z', '+00:00')
        
        # ISO 8601 형식 파싱
        if '+' in utc_time_str or utc_time_str.endswith('00:00'):
            # 타임존 정보가 있는 경우
            utc_time = dt.fromisoformat(utc_time_str.replace('Z', '+00:00'))
            # naive datetime으로 변환 (UTC 기준)
            utc_time = utc_time.replace(tzinfo=None)
        else:
            utc_time = dt.fromisoformat(utc_time_str)
        
        # 한국 시간 = UTC + 9시간
        kst_time = utc_time + timedelta(hours=9)
        
        return kst_time.strftime("%Y-%m-%d %H:%M:%S")
    
    except Exception as e:
        # 파싱 실패 시 원본 반환
        return utc_time_str


# 주요 언론사 채널 ID 목록
MEDIA_CHANNELS = {
    "KBS 뉴스": "UCcQTRi69dsVYHN3exePtZ1A",
    "JTBC News": "UCXQeWk31YT3MlhfizLA_xMw",
    "연합뉴스TV": "UCxLR8OviGXLhE5BqgX23vhQ",
    "MBC 뉴스": "UCF4Wxdo3inmxP-Y59wXDsFw",
    "SBS 뉴스": "UCkinYTS9IHqOEwR1Sze2JTw",
    "YTN": "UChlgI3UHCOnwUGzWzbJ3H5w",
    "채널A 뉴스": "UCj9TF4paIhOerQ1j3dZiMpg",
    "TV조선 뉴스": "UCZ4RZuXImih-dAoLXCL-aLg",
    "MBN 뉴스": "UCIVSsrMlnj3QZYX0RvV_FTg",
    "뉴스1": "UC4-3VgJLc96awTpZQG7Xx-A"
}


def get_video_statistics(youtube, video_ids):
    """
    영상 ID 리스트로 상세 통계 정보 가져오기
    
    Parameters:
    -----------
    youtube : googleapiclient.discovery.Resource
        유튜브 API 클라이언트
    video_ids : list
        영상 ID 리스트
        
    Returns:
    --------
    dict
        video_id를 키로 하는 통계 정보 딕셔너리
    """
    if not video_ids:
        return {}
    
    stats_dict = {}
    
    # 한 번에 최대 50개씩 조회 가능
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        
        try:
            response = youtube.videos().list(
                part='statistics,snippet',
                id=','.join(batch_ids)
            ).execute()
            
            for item in response.get('items', []):
                video_id = item['id']
                statistics = item.get('statistics', {})
                snippet = item.get('snippet', {})
                
                stats_dict[video_id] = {
                    'view_count': int(statistics.get('viewCount', 0)),
                    'like_count': int(statistics.get('likeCount', 0)),
                    'comment_count': int(statistics.get('commentCount', 0)),
                    'tags': ', '.join(snippet.get('tags', []))  # 태그를 쉼표로 연결
                }
            
            time.sleep(0.1)
            
        except HttpError as e:
            print(f"통계 정보 조회 중 오류: {e}")
            continue
    
    return stats_dict


def collect_youtube_videos(api_key, query, start_date, end_date, channel_filter=True, max_results=50):
    """
    유튜브 영상 수집
    
    Parameters:
    -----------
    api_key : str
        유튜브 API 키
    query : str
        검색 키워드
    start_date : str
        시작일 (YYYY-MM-DD) - 한국 시간대 기준
    end_date : str
        종료일 (YYYY-MM-DD) - 한국 시간대 기준
    channel_filter : bool
        언론사 채널만 필터링할지 여부
    max_results : int
        최대 수집 건수
        
    Returns:
    --------
    pd.DataFrame
        수집된 영상 데이터
    """
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 한국 시간을 UTC로 변환 (한국은 UTC+9)
        from datetime import datetime as dt, timedelta
        
        # 시작일: 한국 시간 00:00:00 → UTC (9시간 빼기)
        start_datetime_kst = dt.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        start_datetime_utc = start_datetime_kst - timedelta(hours=9)
        start_datetime = start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 종료일: 한국 시간 23:59:59 → UTC (9시간 빼기)
        end_datetime_kst = dt.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S")
        end_datetime_utc = end_datetime_kst - timedelta(hours=9)
        end_datetime = end_datetime_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        results = []
        
        if channel_filter:
            # 언론사 채널별로 검색
            for channel_name, channel_id in MEDIA_CHANNELS.items():
                try:
                    search_response = youtube.search().list(
                        q=query,
                        channelId=channel_id,
                        part='id,snippet',
                        type='video',
                        publishedAfter=start_datetime,
                        publishedBefore=end_datetime,
                        maxResults=min(50, max_results),
                        order='date'
                    ).execute()
                    
                    for item in search_response.get('items', []):
                        if len(results) >= max_results:
                            break
                            
                        video_id = item['id']['videoId']
                        snippet = item['snippet']
                        
                        # published_at을 한국 시간대로 변환
                        published_at_utc = snippet.get('publishedAt', '')
                        published_at_kst = convert_utc_to_kst(published_at_utc)
                        
                        results.append({
                            'type': 'youtube_video',
                            'video_id': video_id,
                            'title': clean_html(snippet.get('title', '')),
                            'description': clean_html(snippet.get('description', '')),
                            'channel_name': channel_name,
                            'channel_id': snippet.get('channelId', ''),
                            'published_at': published_at_kst,
                            'url': f"https://www.youtube.com/watch?v={video_id}"
                        })
                    
                    time.sleep(0.1)  # API 제한 준수
                    
                except HttpError as e:
                    if e.resp.status == 403:
                        raise Exception("유튜브 API 할당량 초과. 내일 다시 시도해주세요.")
                    print(f"{channel_name} 검색 중 오류: {e}")
                    continue
                    
        else:
            # 전체 검색
            try:
                search_response = youtube.search().list(
                    q=query,
                    part='id,snippet',
                    type='video',
                    publishedAfter=start_datetime,
                    publishedBefore=end_datetime,
                    maxResults=min(50, max_results),
                    order='date'
                ).execute()
                
                for item in search_response.get('items', []):
                    video_id = item['id']['videoId']
                    snippet = item['snippet']
                    
                    # published_at을 한국 시간대로 변환
                    published_at_utc = snippet.get('publishedAt', '')
                    published_at_kst = convert_utc_to_kst(published_at_utc)
                    
                    results.append({
                        'type': 'youtube_video',
                        'video_id': video_id,
                        'title': clean_html(snippet.get('title', '')),
                        'description': clean_html(snippet.get('description', '')),
                        'channel_name': snippet.get('channelTitle', ''),
                        'channel_id': snippet.get('channelId', ''),
                        'published_at': published_at_kst,
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })
                    
            except HttpError as e:
                if e.resp.status == 403:
                    raise Exception("유튜브 API 할당량 초과. 내일 다시 시도해주세요.")
                raise Exception(f"유튜브 검색 중 오류: {str(e)}")
        
        if not results:
            return pd.DataFrame(columns=['type', 'video_id', 'title', 'description', 
                                         'channel_name', 'channel_id', 'published_at', 'url',
                                         'view_count', 'like_count', 'comment_count', 'tags'])
        
        # 수집된 영상 ID 리스트 추출
        video_ids = [result['video_id'] for result in results]
        
        # 상세 통계 정보 가져오기
        stats_dict = get_video_statistics(youtube, video_ids)
        
        # 각 결과에 통계 정보 추가
        for result in results:
            video_id = result['video_id']
            stats = stats_dict.get(video_id, {})
            result['view_count'] = stats.get('view_count', 0)
            result['like_count'] = stats.get('like_count', 0)
            result['comment_count'] = stats.get('comment_count', 0)
            result['tags'] = stats.get('tags', '')
        
        df = pd.DataFrame(results)
        return df
        
    except Exception as e:
        raise Exception(f"유튜브 영상 수집 중 오류: {str(e)}")


def collect_youtube_comments(api_key, video_ids, max_comments_per_video=100):
    """
    유튜브 댓글 수집
    
    Parameters:
    -----------
    api_key : str
        유튜브 API 키
    video_ids : list
        영상 ID 리스트
    max_comments_per_video : int
        영상당 최대 댓글 수
        
    Returns:
    --------
    pd.DataFrame
        수집된 댓글 데이터
    """
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        all_comments = []
        
        for video_id in video_ids:
            try:
                # 댓글 스레드 가져오기
                request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_comments_per_video),
                    order='relevance',
                    textFormat='plainText'
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    
                    # published_at과 updated_at을 한국 시간대로 변환
                    published_at_utc = comment.get('publishedAt', '')
                    updated_at_utc = comment.get('updatedAt', '')
                    published_at_kst = convert_utc_to_kst(published_at_utc)
                    updated_at_kst = convert_utc_to_kst(updated_at_utc)
                    
                    all_comments.append({
                        'type': 'youtube_comment',
                        'video_id': video_id,
                        'comment_id': item['id'],
                        'author': clean_html(comment.get('authorDisplayName', '')),
                        'text': clean_html(comment.get('textDisplay', '')),
                        'like_count': comment.get('likeCount', 0),
                        'published_at': published_at_kst,
                        'updated_at': updated_at_kst
                    })
                
                time.sleep(0.1)  # API 제한 준수
                
            except HttpError as e:
                if e.resp.status == 403:
                    # 댓글이 비활성화된 영상이거나 API 할당량 초과
                    if 'commentsDisabled' in str(e):
                        print(f"영상 {video_id}: 댓글이 비활성화되어 있습니다.")
                        continue
                    else:
                        raise Exception("유튜브 API 할당량 초과. 내일 다시 시도해주세요.")
                print(f"영상 {video_id} 댓글 수집 중 오류: {e}")
                continue
        
        if not all_comments:
            return pd.DataFrame(columns=['type', 'video_id', 'comment_id', 'author', 
                                         'text', 'like_count', 'published_at', 'updated_at'])
        
        df = pd.DataFrame(all_comments)
        return df
        
    except Exception as e:
        raise Exception(f"유튜브 댓글 수집 중 오류: {str(e)}")


def validate_api_key(api_key):
    """
    유튜브 API 키 유효성 검증
    
    Returns:
    --------
    tuple
        (성공 여부, 메시지)
    """
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 간단한 검색 요청으로 키 유효성 확인
        request = youtube.search().list(
            q='test',
            part='id',
            maxResults=1
        )
        
        request.execute()
        return True, "✅ 유튜브 API 키가 유효합니다."
        
    except HttpError as e:
        if e.resp.status == 400:
            return False, "❌ 유튜브 API 키가 유효하지 않습니다."
        elif e.resp.status == 403:
            return False, "❌ API 키 권한 오류 또는 할당량 초과"
        else:
            return False, f"❌ API 오류 (status {e.resp.status})"
            
    except Exception as e:
        return False, f"❌ API 연결 실패: {str(e)}"
