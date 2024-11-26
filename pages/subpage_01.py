import streamlit as st  # streamlit 라이브러리 임포트

# 타이틀 텍스트 출력
st.title('2000-2023 행정구역(시도) 별 경제활동인구')

st.write('.')

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import os
import glob

# 사이드바
st.sidebar.write('## 연도와 항목을 고르시오.') 
# 연도 옵션 생성 
years = list(range(2023,1999, -1)) 
year_option = st.sidebar.selectbox('연도', years) 

# 항목 옵션 생성 
item_option = st.sidebar.selectbox('항목', ['경제활동참가율(%)', '고용률(%)', '실업률(%)']) 

# 데이터 경로 설정
data_path = os.path.abspath('행정구역_시도_별_경제활동인구_20241126130730.csv')

# CSV 데이터 불러오기
df_korea_economics= pd.read_csv(data_path,header=1,encoding='utf-8')
st.write("CSV 파일 열 이름:", df_korea_economics.columns.tolist())

# 열 이름 정제 
columns = ['행정구', '15세 이상 인구', '경제활동인구', '비경제활동인구', '경제활동참가율', '실업률', '고용률']
for i in range(1, 24): 
    columns += [f'15세 이상 인구.{i}', f'경제활동인구.{i}', f'비경제활동인구.{i}', f'경제활동참가율.{i}', f'실업률.{i}', f'고용률.{i}'] 

# 열 이름의 개수와 데이터프레임의 열 수가 일치하는지 확인 
if len(columns) == len(df_korea_economics.columns): 
    df_korea_economics.columns = columns 
else: 
    st.write("열 이름의 개수와 데이터프레임의 열 수가 일치하지 않습니다.")

# 선택한 연도에 해당하는 데이터 필터링 
year_index = 2023 - year_option 
selected_data = df_korea_economics.iloc[:, [0, year_index*6+1, year_index*6+2, year_index*6+3, year_index*6+4, year_index*6+5, year_index*6+6]] 

# 선택한 항목에 따라 데이터 출력 
if item_option == '경제활동참가율(%)': 
    st.write(selected_data[['행정구', f'경제활동참가율.{year_index}']]) 
elif item_option == '고용률(%)': 
    st.write(selected_data[['행정구', f'고용률.{year_index}']]) 
elif item_option == '실업률(%)': 
    st.write(selected_data[['행정구', f'실업률.{year_index}']])

df_korea_economics['행정구'] = df_korea_economics['행정구'].str.replace('\d+', '', regex=True).str.strip()
df_korea_economics[f'경제활동참가율(%).{year_index}'] = df_korea_economics[f'경제활동참가율(%).{year_index}'].fillna(0)

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
title = '행정구역(시도별) 경제활동참가율'
title_html = f'<h3 align="center" style="font-size:20px"><b>{title}</b></h3>'
korea_map.get_root().html.add_child(folium.Element(title_html))

# Choropleth map
folium.Choropleth(
    geo_data=gdf_korea_sido,
    data=df_korea_economics,
    columns = ['행정구', '경제활동인구'],
    key_on='feature.properties.행정구',
    legend_name= item_option,
    fill_color='BuPu',
    fill_opacity=0.7,
    line_opacity=0.3
).add_to(korea_map)

# Streamlit 설정
st.markdown(title_html, unsafe_allow_html=True)

# Folium 지도 출력
folium_static(korea_map)
