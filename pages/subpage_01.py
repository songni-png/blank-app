import streamlit as st  # streamlit 라이브러리 임포트

# 타이틀 텍스트 출력
st.title('경제성장률')

st.write('물가상승률')

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
df_korea_economics= pd.read_csv(data_path,header=5,encoding='utf-8')

# 필요한 열만 선택
df_korea_economics = df_korea_economics[['A 행정구역별', 'H202401 2024.1/2']]
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
