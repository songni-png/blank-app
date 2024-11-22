# 텍스트
st.header('전국 시군구 출생률 👼🏻')


# 사이드바
st.sidebar.write('## 연도 및 분기를 고르시오.')
st.sidebar.selectbox('연도 및 분기', ['2023-1', '2023-2', '2023-3','2023-4','2024-1','2024-2','2024-3'])



# 레이아웃: 탭
st.header('🤖 탭 레이아웃')
tab_1, tab_2, tab_3 = st.tabs(['탭A', '탭B', '탭C'])  # 탭 인스턴스 생성. 3개의 탭을 생성

with tab_1:
    st.write('## 탭A')
    st.write('이것은 탭A의 내용입니다.')

with tab_2:
    st.write('## 탭B')
    st.write('이것은 탭B의 내용입니다.')

tab_3.write('## 탭C')
tab_3.write('이것은 탭C의 내용입니다.')
