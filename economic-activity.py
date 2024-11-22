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
df_korea_economics = df_korea_economics.iloc[:,[0,6]]
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
    legend_name = '전국 시군구 경제활동참가율(%)',
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
