"""
뉴스/유튜브 수집 시스템 - Streamlit 웹 애플리케이션
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import naver_collector
import youtube_collector


# 페이지 설정
st.set_page_config(
    page_title="ARGOS-K",
    page_icon="📰",
    layout="wide"
)

# CSS 스타일링
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #e35d14;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    # 헤더
    st.markdown('<div class="main-header">ARGOS-K</div>', unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'collected_data' not in st.session_state:
        st.session_state.collected_data = None
    if 'collection_stats' not in st.session_state:
        st.session_state.collection_stats = {}
    
    # 사이드바 - API 키 입력
    with st.sidebar:
        st.markdown('<div class="section-header">🔑 API 키 설정</div>', unsafe_allow_html=True)
        
        st.markdown("#### 네이버 API")
        naver_client_id = st.text_input(
            "Client ID",
            type="password",
            help="네이버 개발자 센터에서 발급받은 Client ID"
        )
        naver_client_secret = st.text_input(
            "Client Secret",
            type="password",
            help="네이버 개발자 센터에서 발급받은 Client Secret"
        )
        
        st.markdown("#### 유튜브 API")
        youtube_api_key = st.text_input(
            "API Key",
            type="password",
            help="Google Cloud Console에서 발급받은 API Key"
        )
        
        st.markdown("---")
        
        # API 키 검증
        if st.button("🔍 API 키 검증", use_container_width=True):
            with st.spinner("API 키 검증 중..."):
                results = []
                
                if naver_client_id and naver_client_secret:
                    valid, msg = naver_collector.validate_api_key(naver_client_id, naver_client_secret)
                    results.append(msg)
                
                if youtube_api_key:
                    valid, msg = youtube_collector.validate_api_key(youtube_api_key)
                    results.append(msg)
                
                if results:
                    for result in results:
                        st.write(result)
                else:
                    st.warning("⚠️ API 키를 입력해주세요.")
        
        st.markdown("---")
        
        # API 발급 가이드
        with st.expander("📘 API 키 발급 방법"):
            st.markdown("""
            **네이버 API**
            1. [네이버 개발자 센터](https://developers.naver.com/) 접속
            2. 로그인 후 '애플리케이션 등록'
            3. 사용 API에서 '검색' 선택
            4. Client ID와 Secret 복사
            
            **유튜브 API**
            1. [Google Cloud Console](https://console.cloud.google.com/) 접속
            2. 프로젝트 생성
            3. 'YouTube Data API v3' 활성화
            4. '사용자 인증 정보'에서 API 키 생성
            """)
    
    # 메인 콘텐츠
    st.markdown('<div class="section-header">🔍 검색 조건 설정</div>', unsafe_allow_html=True)
    
    # 검색 조건 입력
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        keyword = st.text_input(
            "검색 키워드",
            placeholder="예: 중대재해, 산업재해, 건설사고 (쉼표로 구분)",
            help="여러 키워드를 쉼표(,)로 구분하여 입력하면 OR 검색 효과 (중복 자동 제거)"
        )
    
    with col2:
        start_date = st.date_input(
            "시작일",
            value=datetime.now() - timedelta(days=30),
            help="수집 시작 날짜"
        )
    
    with col3:
        end_date = st.date_input(
            "종료일",
            value=datetime.now(),
            help="수집 종료 날짜"
        )
    
    # 수집 대상 선택
    st.markdown("#### 📰 수집 대상 선택")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        collect_naver = st.checkbox("네이버 뉴스", value=True)
        if collect_naver:
            naver_max = st.number_input(
                "최대 수집 건수",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
                key="naver_max"
            )
    
    with col2:
        collect_youtube = st.checkbox("유튜브 영상", value=True)
        if collect_youtube:
            youtube_max = st.number_input(
                "최대 수집 건수",
                min_value=10,
                max_value=200,
                value=50,
                step=10,
                key="youtube_max"
            )
            youtube_channel_filter = st.checkbox(
                "언론사 채널만",
                value=True,
                help="KBS, MBC, SBS, JTBC, TV조선, 채널A, MBN, 뉴스1, 연합뉴스TV"
            )
    
    with col3:
        collect_comments = st.checkbox("유튜브 댓글", value=True)
        if collect_comments:
            comments_per_video = st.number_input(
                "영상당 댓글 수",
                min_value=10,
                max_value=500,
                value=100,
                step=10,
                key="comments_max"
            )
    
    # 정보 박스
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    **💡 수집 팁**
    - 네이버 API: 하루 25,000건 제한
    - 유튜브 API: 하루 10,000 units 제한
    - 각자의 API 키를 사용하면 독립적인 한도 적용
    - 수집 시간은 선택한 항목과 건수에 따라 달라집니다
    - **여러 키워드 입력:** 쉼표로 구분하면 자동으로 통합 (중복 제거)
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API 사용량 예측
    if keyword and (collect_naver or collect_youtube or collect_comments):
        keywords = [k.strip() for k in keyword.split(',') if k.strip()]
        num_keywords = len(keywords)
        
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown(f"**📊 예상 API 사용량 (키워드 {num_keywords}개)**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if collect_naver:
                # 네이버: 한 번의 API 호출 = 1건
                # 100건씩 페이징하므로 (max/100)번 호출
                naver_calls = (naver_max // 100 + 1) * num_keywords
                naver_percent = (naver_calls / 25000) * 100
                st.write(f"**네이버 API**")
                st.write(f"- 약 {naver_calls:,}회 호출")
                st.write(f"- 일일 한도 대비: {naver_percent:.1f}%")
        
        with col2:
            if collect_youtube:
                # 유튜브: 검색 1회 = 100 units
                youtube_units = 100 * num_keywords
                
                if collect_comments and youtube_max > 0:
                    # 댓글 조회: 1개 영상당 1 unit
                    youtube_units += youtube_max * num_keywords
                
                youtube_percent = (youtube_units / 10000) * 100
                st.write(f"**유튜브 API**")
                st.write(f"- 약 {youtube_units:,} units")
                st.write(f"- 일일 한도 대비: {youtube_percent:.1f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 수집 시작 버튼
    st.markdown("---")
    
    if st.button("수집 시작", type="primary", use_container_width=True):
        # 입력 검증
        errors = []
        
        if not keyword:
            errors.append("검색 키워드를 입력해주세요.")
        
        if start_date > end_date:
            errors.append("시작일이 종료일보다 늦을 수 없습니다.")
        
        if collect_naver and (not naver_client_id or not naver_client_secret):
            errors.append("네이버 API 키를 입력해주세요.")
        
        if (collect_youtube or collect_comments) and not youtube_api_key:
            errors.append("유튜브 API 키를 입력해주세요.")
        
        if not collect_naver and not collect_youtube and not collect_comments:
            errors.append("최소 하나의 수집 대상을 선택해주세요.")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # 키워드 파싱
            keywords = [k.strip() for k in keyword.split(',') if k.strip()]
            
            # 수집 실행
            run_collection(
                keywords,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                collect_naver,
                collect_youtube,
                collect_comments,
                naver_client_id,
                naver_client_secret,
                youtube_api_key,
                naver_max if collect_naver else 0,
                youtube_max if collect_youtube else 0,
                youtube_channel_filter if collect_youtube else True,
                comments_per_video if collect_comments else 0
            )
    
    # 결과 표시
    if st.session_state.collected_data is not None:
        display_results()


def run_collection(keywords, start_date, end_date, collect_naver, collect_youtube, 
                   collect_comments, naver_id, naver_secret, youtube_key,
                   naver_max, youtube_max, youtube_filter, comments_max):
    """수집 실행 - 다중 키워드 지원"""
    
    st.markdown('<div class="section-header">📊 수집 진행 상황</div>', unsafe_allow_html=True)
    
    # 키워드 정보 표시
    if len(keywords) > 1:
        st.info(f"🔍 {len(keywords)}개의 키워드로 검색: {', '.join(keywords)}")
    
    all_data = []
    stats = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_steps = len(keywords) * sum([collect_naver, collect_youtube, collect_comments])
    current_step = 0
    
    try:
        for keyword_idx, keyword in enumerate(keywords, 1):
            if len(keywords) > 1:
                st.markdown(f"**키워드 {keyword_idx}/{len(keywords)}: '{keyword}'**")
            
            # 1. 네이버 뉴스 수집
            if collect_naver:
                status_text.text(f"📰 네이버 뉴스 수집 중... (키워드: {keyword})")
                try:
                    naver_df = naver_collector.collect_naver_news(
                        naver_id, naver_secret, keyword, start_date, end_date, naver_max
                    )
                    if not naver_df.empty:
                        all_data.append(naver_df)
                    
                    if keyword_idx == 1:
                        stats['naver_news'] = len(naver_df)
                    else:
                        stats['naver_news'] = stats.get('naver_news', 0) + len(naver_df)
                    
                    st.success(f"✅ '{keyword}' 네이버 뉴스: {len(naver_df)}건")
                except Exception as e:
                    st.error(f"❌ '{keyword}' 네이버 뉴스 수집 실패: {str(e)}")
                
                current_step += 1
                progress_bar.progress(current_step / total_steps)
            
            # 2. 유튜브 영상 수집
            video_ids = []
            if collect_youtube:
                status_text.text(f"🎥 유튜브 영상 수집 중... (키워드: {keyword})")
                try:
                    youtube_df = youtube_collector.collect_youtube_videos(
                        youtube_key, keyword, start_date, end_date, youtube_filter, youtube_max
                    )
                    if not youtube_df.empty:
                        all_data.append(youtube_df)
                        video_ids = youtube_df['video_id'].tolist()
                    
                    if keyword_idx == 1:
                        stats['youtube_videos'] = len(youtube_df)
                    else:
                        stats['youtube_videos'] = stats.get('youtube_videos', 0) + len(youtube_df)
                    
                    st.success(f"✅ '{keyword}' 유튜브 영상: {len(youtube_df)}건")
                except Exception as e:
                    st.error(f"❌ '{keyword}' 유튜브 영상 수집 실패: {str(e)}")
                
                current_step += 1
                progress_bar.progress(current_step / total_steps)
            
            # 3. 유튜브 댓글 수집
            if collect_comments and video_ids:
                status_text.text(f"💬 유튜브 댓글 수집 중... (키워드: {keyword})")
                try:
                    comments_df = youtube_collector.collect_youtube_comments(
                        youtube_key, video_ids, comments_max
                    )
                    if not comments_df.empty:
                        all_data.append(comments_df)
                    
                    if keyword_idx == 1:
                        stats['youtube_comments'] = len(comments_df)
                    else:
                        stats['youtube_comments'] = stats.get('youtube_comments', 0) + len(comments_df)
                    
                    st.success(f"✅ '{keyword}' 유튜브 댓글: {len(comments_df)}건")
                except Exception as e:
                    st.error(f"❌ '{keyword}' 유튜브 댓글 수집 실패: {str(e)}")
                
                current_step += 1
                progress_bar.progress(current_step / total_steps)
            elif collect_comments and not video_ids:
                st.warning(f"⚠️ '{keyword}': 수집된 영상이 없어 댓글을 수집할 수 없습니다.")
                current_step += 1
                progress_bar.progress(current_step / total_steps)
        
        # 데이터 통합 및 중복 제거
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 중복 제거
            original_count = len(combined_df)
            
            # 각 타입별로 중복 제거 기준 다르게 적용
            if 'type' in combined_df.columns:
                deduplicated_dfs = []
                
                # 네이버 뉴스: link 기준
                if 'naver_news' in combined_df['type'].values:
                    naver_df = combined_df[combined_df['type'] == 'naver_news']
                    if 'link' in naver_df.columns:
                        naver_df = naver_df.drop_duplicates(subset=['link'], keep='first')
                    deduplicated_dfs.append(naver_df)
                
                # 유튜브 영상: video_id 기준
                if 'youtube_video' in combined_df['type'].values:
                    youtube_df = combined_df[combined_df['type'] == 'youtube_video']
                    if 'video_id' in youtube_df.columns:
                        youtube_df = youtube_df.drop_duplicates(subset=['video_id'], keep='first')
                    deduplicated_dfs.append(youtube_df)
                
                # 유튜브 댓글: comment_id 기준
                if 'youtube_comment' in combined_df['type'].values:
                    comments_df = combined_df[combined_df['type'] == 'youtube_comment']
                    if 'comment_id' in comments_df.columns:
                        comments_df = comments_df.drop_duplicates(subset=['comment_id'], keep='first')
                    deduplicated_dfs.append(comments_df)
                
                combined_df = pd.concat(deduplicated_dfs, ignore_index=True)
            
            duplicate_count = original_count - len(combined_df)
            
            if duplicate_count > 0:
                st.info(f"🔄 중복 제거: {duplicate_count}건 (최종 {len(combined_df)}건)")
            
            # 통계 업데이트
            if 'type' in combined_df.columns:
                stats['naver_news'] = len(combined_df[combined_df['type'] == 'naver_news'])
                stats['youtube_videos'] = len(combined_df[combined_df['type'] == 'youtube_video'])
                stats['youtube_comments'] = len(combined_df[combined_df['type'] == 'youtube_comment'])
            
            st.session_state.collected_data = combined_df
            st.session_state.collection_stats = stats
            
            status_text.text("✅ 수집 완료!")
            progress_bar.progress(1.0)
        else:
            st.warning("⚠️ 수집된 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"❌ 수집 중 오류 발생: {str(e)}")


def display_results():
    """결과 표시"""
    
    st.markdown('<div class="section-header">📊 수집 결과</div>', unsafe_allow_html=True)
    
    df = st.session_state.collected_data
    stats = st.session_state.collection_stats
    
    # 통계 표시
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 수집 건수", f"{len(df):,}")
    
    with col2:
        if 'naver_news' in stats:
            st.metric("네이버 뉴스", f"{stats['naver_news']:,}")
    
    with col3:
        if 'youtube_videos' in stats:
            st.metric("유튜브 영상", f"{stats['youtube_videos']:,}")
    
    with col4:
        if 'youtube_comments' in stats:
            st.metric("유튜브 댓글", f"{stats['youtube_comments']:,}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 데이터 미리보기
    st.markdown("#### 📋 데이터 미리보기 (상위 10개)")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Excel 파일 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"수집결과_{timestamp}.xlsx"
    
    # BytesIO 객체로 Excel 파일 생성
    from io import BytesIO
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 네이버 뉴스 시트
        if 'naver_news' in stats and stats['naver_news'] > 0:
            naver_df = df[df['type'] == 'naver_news'].copy()
            # 필요한 컬럼만 선택
            naver_columns = ['title', 'description', 'link', 'originallink', 'pubDate']
            naver_df = naver_df[[col for col in naver_columns if col in naver_df.columns]]
            naver_df.to_excel(writer, sheet_name='네이버_뉴스', index=False)
            
            # 컬럼 폭 자동 조정
            worksheet = writer.sheets['네이버_뉴스']
            for idx, col in enumerate(naver_df.columns):
                max_length = max(
                    naver_df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        # 유튜브 영상 시트
        if 'youtube_videos' in stats and stats['youtube_videos'] > 0:
            youtube_df = df[df['type'] == 'youtube_video'].copy()
            # 필요한 컬럼만 선택
            youtube_columns = ['title', 'description', 'channel_name', 'published_at', 
                             'view_count', 'like_count', 'comment_count', 'tags', 'url', 'video_id']
            youtube_df = youtube_df[[col for col in youtube_columns if col in youtube_df.columns]]
            youtube_df.to_excel(writer, sheet_name='유튜브_영상', index=False)
            
            # 컬럼 폭 자동 조정
            worksheet = writer.sheets['유튜브_영상']
            for idx, col in enumerate(youtube_df.columns):
                max_length = max(
                    youtube_df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        # 유튜브 댓글 시트
        if 'youtube_comments' in stats and stats['youtube_comments'] > 0:
            comments_df = df[df['type'] == 'youtube_comment'].copy()
            # 필요한 컬럼만 선택
            comments_columns = ['video_id', 'author', 'text', 'like_count', 'published_at']
            comments_df = comments_df[[col for col in comments_columns if col in comments_df.columns]]
            comments_df.to_excel(writer, sheet_name='유튜브_댓글', index=False)
            
            # 컬럼 폭 자동 조정
            worksheet = writer.sheets['유튜브_댓글']
            for idx, col in enumerate(comments_df.columns):
                max_length = max(
                    comments_df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    excel_data = output.getvalue()
    
    # Excel 다운로드 버튼
    st.download_button(
        label="📥 Excel 다운로드",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )
    
    # 데이터 타입별 분포
    if 'type' in df.columns:
        st.markdown("#### 📊 데이터 타입별 분포")
        type_counts = df['type'].value_counts()
        st.bar_chart(type_counts)


if __name__ == "__main__":
    main()
