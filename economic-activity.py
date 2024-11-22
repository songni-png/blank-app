# 텍스트
st.header('전국 시군구 출생률 👼🏻')

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import os
import glob

# 데이터 경로 설정
data_path = os.path.abspath('전국_시군구_경제활동인구_총괄_20241121153501.csv')
# CSV 데이터 불러오기
df_korea_economics= pd.read_csv(data_path,encoding='utf-8')

# 필요한 열만 선택
df_korea_economics = df_korea_economics[['A 행정구역별', '62.1']]

# 데이터 정제
df_korea_economics.columns = ['행정구', '경제활동참가율(%)']
df_korea_economics['행정구'] = df_korea_economics['행정구'].str.replace('\d+', '', regex=True).str.strip()
df_korea_economics['경제활동참가율(%)'] = df_korea_economics['경제활동참가율(%)'].fillna(0)

st.dataframe(df_korea_economics, height=200)

# GeoJSON 파일 경로 설정
file_pattern = os.path.join('LARD_ADM_SECT_SGG_*.json')
file_list = glob.glob(file_pattern)

if not file_list:
    raise FileNotFoundError(f"GeoJSON 파일을 찾을 수 없습니다: {file_pattern}")

# GeoDataFrame 생성
gdfs = [gpd.read_file(file) for file in file_list]
gdf_korea_sido = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

# 'SGG_NM' 정제
gdf_korea_sido['행정구'] = gdf_korea_sido['SGG_NM'].str.split().str[1:].str.join(' ')

# 좌표계 변경
korea_5179 = gdf_korea_sido.to_crs(epsg=5179)


# 기본 지도 생성
korea_map = folium.Map(location=[37, 126], zoom_start=7, tiles='cartodbpositron')

# 제목 설정
title = '전국 시군구 경제활동참가율'
title_html = f'<h3 align="center" style="font-size:20px"><b>{title}</b></h3>'
korea_map.get_root().html.add_child(folium.Element(title_html))

# Choropleth map
folium.Choropleth(
    geo_data=gdf_korea_sido,
    data=df_korea_economics,
    columns=['행정구', '경제활동참가율(%)'],
    key_on='feature.properties.행정구',
    legend = '전국 시군구 경제활동참가율(%)',
    fill_color='BuPu',
    fill_opacity=0.7,
    line_opacity=0.3
).add_to(korea_map)

# Streamlit 설정
st.markdown(title_html, unsafe_allow_html=True)

# Folium 지도 출력
folium_static(korea_map)


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

# 사용자 입력
st.header('🤖 사용자 입력')

text = st.text_input('여기에 텍스트를 입력하세요') # 텍스트 입력은 입력된 값을 반환
st.write(f'입력된 텍스트: {text}')

number = st.number_input('여기에 숫자를 입력하세요') # 숫자 입력은 입력된 값을 반환
st.write(f'입력된 숫자: {number}')

check = st.checkbox('여기를 체크하세요') # 체크박스는 True/False 값을 반환
if check:
    st.write('체크되었습니다.')

radio = st.radio('여기에서 선택하세요', ['선택 1', '선택 2', '선택 3']) # 라디오 버튼은 선택된 값을 반환
st.write(radio+'가 선택되었습니다.')

select = st.selectbox('여기에서 선택하세요', ['선택 1', '선택 2', '선택 3']) # 셀렉트박스는 선택된 값을 반환
st.write(select+'가 선택되었습니다.')

slider = st.slider('여기에서 값을 선택하세요', 0, 100, 50) # 슬라이더는 선택된 값을 반환
st.write(f'현재의 값은 {slider} 입니다.')

multi = st.multiselect('여기에서 여러 값을 선택하세요', ['선택 1', '선택 2', '선택 3']) # 멀티셀렉트박스는 선택된 값을 리스트로 반환
st.write(f'{type(multi) = }, {multi}가 선택되었습니다.')

button = st.button('여기를 클릭하세요') # 버튼은 클릭 여부를 반환
if button:
    st.write('버튼이 클릭되었습니다.(일반 텍스트: st.write()')
    st.success('버튼이 클릭되었습니다.(메시지: st.success())')  # 성공 메시지 출력
    st.balloons() # 풍선 애니메이션 출력

# 캐싱
st.header('🤖 캐싱 적용')

import time

@st.cache_data
def long_running_function(param1):
    time.sleep(5)
    return param1*param1

start = time.time()
num_1 = st.number_input('입력한 숫자의 제곱을 계산합니다.') # 숫자 입력은 입력된 값을 반환
st.write(f'{num_1}의 제곱은 {long_running_function(num_1)} 입니다. 계산시간은 {time.time()-start:.2f}초 소요')


# 세션 상태
st.header('🤖 세션 상태')

import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.randn(20, 2), columns=["x", "y"])

st.header("session_state를 사용하지 않은 경우")
color1 = st.color_picker("Color1", "#FF0000")
st.divider() # 구분선
st.scatter_chart(df, x="x", y="y", color=color1)

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(np.random.randn(20, 2), columns=["x", "y"])

st.header("session_state를 사용한 경우")
color2 = st.color_picker("Color2", "#FF0000")
st.divider() # 구분선
st.scatter_chart(st.session_state.df, x="x", y="y", color=color2)
# Streamlit 앱 설정
st.title('전국 시군구 출생률')
st.markdown(title_html, unsafe_allow_html=True)





