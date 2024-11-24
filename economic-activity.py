import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import os
import glob
import numpy as np

# 텍스트
st.header('대한민국 경제 상황과') 
st.header('전국 행정구역 경제활동 상관관계 분석')

# 사이드바
st.sidebar.write('## 항목을 고르시오.')
option = st.sidebar.selectbox('항목', ['경제활동참가율(%)', '고용률(%)', '실업률(%)'])

st.write(f"선택된 항목: {option}")

# 데이터 경로 설정
data_path = os.path.abspath('전국_시군구_경제활동인구_총괄_20241121153501.csv')
if not os.path.exists(data_path):
    st.error(f"CSV 파일을 찾을 수 없습니다: {data_path}")
    st.stop()

# CSV 데이터 불러오기
df_korea_economics = pd.read_csv(data_path, encoding='utf-8')
st.write("CSV 파일 열 이름:", df_korea_economics.columns.tolist())
if 'A 행정구역별' not in df_korea_economics.columns:
    st.error("'A 행정구역별' 열이 CSV 파일에 존재하지 않습니다. 파일 구조를 확인하세요.")
    st.stop()

# CSV 파일 정제
df_korea_economics = df_korea_economics[['A 행정구역별', 'H202401 2024.1/2.5', 'H202402 2024.1/2.6', 'H202403 2024.1/2.7']]
df_korea_economics.columns = ['행정구', '경제활동참가율(%)', '고용률(%)', '실업률(%)']
df_korea_economics['행정구'] = df_korea_economics['행정구'].str.replace('\d+', '', regex=True).str.strip()
df_korea_economics.reset_index(drop=True, inplace=True)
df_korea_economics['경제활동참가율(%)'] = pd.to_numeric(df_korea_economics['경제활동참가율(%)'], errors='coerce').fillna(0)
df_korea_economics['고용률(%)'] = pd.to_numeric(df_korea_economics['고용률(%)'], errors='coerce').fillna(0)
df_korea_economics['실업률(%)'] = pd.to_numeric(df_korea_economics['실업률(%)'], errors='coerce').fillna(0)
st.dataframe(df_korea_economics, height=200)

# GeoJSON 파일 경로 설정
file_pattern = os.path.join('LARD_ADM_SECT_SGG_*.json')
file_list = glob.glob(file_pattern)

if not file_list:
    st.error(f"GeoJSON 파일을 찾을 수 없습니다: {file_pattern}")
    st.stop()

# GeoDataFrame 생성
gdfs = [gpd.read_file(file) for file in file_list]
gdf_korea_sido = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

# 'SGG_NM' 정제
gdf_korea_sido['행정구'] = gdf_korea_sido['SGG_NM'].str.split().str[1:].str.join(' ')
df_korea_economics['행정구'] = df_korea_economics['행정구'].str.replace('\d+', '', regex=True).str.strip()

# 선택한 옵션에 따라 다른 코드 실행
if option == '경제활동참가율(%)':
    selected_column = '경제활동참가율(%)'
elif option == '고용률(%)':
    selected_column = '고용률(%)'
elif option == '실업률(%)':
    selected_column = '실업률(%)'

if selected_column not in df_korea_economics.columns:
    st.error(f"선택한 항목 '{selected_column}' 열이 CSV 데이터에 없습니다.")
    st.stop()

# Choropleth 지도 생성
korea_map = folium.Map(location=[37, 126], zoom_start=7, tiles='cartodbpositron')
folium.Choropleth(
    geo_data=gdf_korea_sido,
    data=df_korea_economics,
    columns=['행정구', selected_column],
    key_on='feature.properties.행정구',
    legend_name=f'전국 시군구 {selected_column}',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.3
).add_to(korea_map)

st.markdown(f"<h3 align='center'>{selected_column}</h3>", unsafe_allow_html=True)
folium_static(korea_map)


