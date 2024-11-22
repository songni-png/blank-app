import streamlit as st
# 텍스트
st.header('대한민국 경제 상황과 전국 행정구역 경제활동 상관관계 분석')

# 사이드바
st.sidebar.write('## 항목을 고르시오.')
st.sidebar.selectbox('항목', ['경제활동참가율(%)','취업률(%)', '실업률(%)'])
