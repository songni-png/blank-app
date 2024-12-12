import streamlit as st  # streamlit 라이브러리 임포트

# 타이틀 텍스트 출력
st.title('2000-2023 행정구역(시도) 별 경제활동인구')

st.write('.')

import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import os
import glob

# 사이드바
st.sidebar.write('## 연도와 항목을 고르시오.') 

# 데이터 경로 설정
data_path = os.path.abspath('행정구역_시도_별_경제활동인구_20241126130730.csv')

# CSV 데이터 불러오기
df_korea_economics = pd.read_csv(data_path, header=1, encoding='utf-8')
st.write("CSV 파일 열 이름:", df_korea_economics.columns.tolist())

# 숫자와 문자를 분리하는 코드 
df_korea_economics[['code', 'city']] = df_korea_economics['A 시도별(1)'].str.extract(r'(\d+)\s*(.*)')

df_korea_economics.drop('A 시도별(1)',axis=1,inplace=True)

# 데이터를 멜팅하여 데이터프레임으로 변환
df_korea_economics = df_korea_economics.melt(
                     id_vars = ['city','code'],
                     var_name = 'property',
                     value_name = 'population',
)
# 연도 리스트 생성 
years = [] 
for i in range(2023, 1999, -1): 
    years.extend([i] * 126) 
years = years[:len(df_korea_economics)] 
# 'property' 열을 'year'와 'category' 열로 분리 
df_korea_economics['year'] = years 
df_korea_economics['category'] = df_korea_economics['property'].str.extract(r'^\D*\d+\s*(.*)')[0] 
# 'category' 열에서 '(' 이후 부분 제거 
df_korea_economics['category'] = df_korea_economics['category'].str.split('(').str[0].str.strip() 
# 'property' 열 삭제 
df_korea_economics.drop('property', axis=1, inplace=True) 
# 'population' 열을 정수로 변환
df_korea_economics['population'] = df_korea_economics['population'].replace('-','0').fillna('0').astype(float)
# 열 순서 변경
df_korea_economics = df_korea_economics[['city','code','year','category','population']]

df_korea_economics

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
title = '행정구역(시도별) 경제활동참가율'
title_html = f'<h3 align="center" style="font-size:20px"><b>{title}</b></h3>'
korea_map.get_root().html.add_child(folium.Element(title_html))

# Choropleth map
folium.Choropleth(
    geo_data=gdf_korea_sido,
    data=df_korea_economics,
    columns=['행정구', '경제활동인구'],
    key_on='feature.properties.행정구',
    legend_name=item_option,
    fill_color='BuPu',
    fill_opacity=0.7,
    line_opacity=0.3
).add_to(korea_map)

# Streamlit 설정
st.markdown(title_html, unsafe_allow_html=True)

# Folium 지도 출력
folium_static(korea_map)
