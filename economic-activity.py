import streamlit as st
# 텍스트
st.header('전국 시군구 출생률 👼🏻')


# 사이드바
st.sidebar.write('## 연도 및 분기를 고르시오.')
st.sidebar.selectbox('연도 및 분기', ['2023-1', '2023-2', '2023-3','2023-4','2024-1','2024-2','2024-3'])
