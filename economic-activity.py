import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import os
import glob
# 텍스트
st.header('대한민국 경제 상황과') 
st.header('전국 행정구역 경제활동 상관관계 분석')

# 사이드바
st.sidebar.write('## 항목을 고르시오.')
option = st.sidebar.selectbox('항목', ['경제활동참가율(%)','취업률(%)', '실업률(%)'])

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


# 선택한 옵션에 따라 다른 코드 실행
if option == '경제활동참가율(%)':
    # 필요한 열만 선택
    df_korea_economics = df_korea_economics.iloc[:, [0, 6]]
    # 데이터 정제
    df_korea_economics.columns = ['행정구', '경제활동참가율(%)']
    df_korea_economics['행정구'] = df_korea_economics['행정구'].str.replace('\d+', '', regex=True).str.strip()
    df_korea_economics['경제활동참가율(%)'] = df_korea_economics['경제활동참가율(%)'].fillna(0)
    st.dataframe(df_korea_economics, height=200)

    # Choropleth map
    folium.Choropleth(
        geo_data=gdf_korea_sido,
        data=df_korea_economics,
        columns=['행정구', '경제활동참가율(%)'],
        key_on='feature.properties.행정구',
        legend_name='전국 시군구 경제활동참가율(%)',
        fill_color='BuPu',
        fill_opacity=0.7,
        line_opacity=0.3
    ).add_to(korea_map)

    # Streamlit 설정
    st.markdown(title_html, unsafe_allow_html=True)

    # Folium 지도 출력
    folium_static(korea_map)

elif option == '옵션 2':
    # 다른 열 선택 및 정제
    df_korea_economics = df_korea_economics.iloc[:, [0, 7]]
    df_korea_economics.columns = ['행정구', '고용률(%)']
    df_korea_economics['행정구'] = df_korea_economics['행정구'].str.replace('\d+', '', regex=True).str.strip()
    df_korea_economics['고용률(%)'] = df_korea_economics['고용률(%)'].fillna(0)
    st.dataframe(df_korea_economics, height=200)

    # Choropleth map
    folium.Choropleth(
        geo_data=gdf_korea_sido,
        data=df_korea_economics,
        columns=['행정구', '고용률(%)'],
        key_on='feature.properties.행정구',
        legend_name='전국 시군구 고용률(%)',
        fill_color='PiYG',
        fill_opacity=0.7,
        line_opacity=0.3
    ).add_to(korea_map)

    # Streamlit 설정
    st.markdown(title_html, unsafe_allow_html=True)

    # Folium 지도 출력
    folium_static(korea_map)

elif option == '옵션 3':
    # 또 다른 열 선택 및 정제
    df_korea_economics = df_korea_economics.iloc[:, [0, 9]]
    df_korea_economics.columns = ['행정구', '실업률(%)']
    df_korea_economics['행정구'] = df_korea_economics['행정구'].str.replace('\d+', '', regex=True).str.strip()
    df_korea_economics['실업률(%)'] = df_korea_economics['실업률(%)'].fillna(0)
    st.dataframe(df_korea_economics, height=200)

    # Choropleth map
    folium.Choropleth(
        geo_data=gdf_korea_sido,
        data=df_korea_economics,
        columns=['행정구', '실업률(%)'],
        key_on='feature.properties.행정구',
        legend_name='전국 시군구 실업률(%)',
        fill_color='RdPu',
        fill_opacity=0.7,
        line_opacity=0.3
    ).add_to(korea_map)

    # Streamlit 설정
    st.markdown(title_html, unsafe_allow_html=True)

    # Folium 지도 출력
    folium_static(korea_map)
