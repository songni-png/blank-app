import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import os
import glob
import numpy as np

# 텍스트
st.title('대한민국 경제 상황 분석')
st.subheader('전국 행정구역 경제활동 데이터 시각화')

# 데이터 경로 설정
data_path = os.path.abspath('전국_시군구_경제활동인구_총괄_20241121153501.csv')
df_korea_economics = pd.read_csv(data_path, encoding='utf-8')

# GeoJSON 파일 경로 설정
file_pattern = os.path.join('LARD_ADM_SECT_SGG_*.json')
file_list = glob.glob(file_pattern)

if not file_list:
    st.error("GeoJSON 파일을 찾을 수 없습니다.")
    st.stop()

# GeoDataFrame 생성
gdfs = [gpd.read_file(file) for file in file_list]
gdf_korea_sido = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

# 'SGG_NM' 정제
gdf_korea_sido['행정구'] = gdf_korea_sido['SGG_NM'].str.split().str[1:].str.join(' ')
gdf_korea_sido = gdf_korea_sido[['행정구', 'geometry']]

# 탭 인터페이스
tabs = st.tabs(["경제활동참가율", "고용률", "실업률"])

# 각 탭별로 데이터를 보여줌
for tab, column_name, fill_color in zip(
    tabs,
    ['경제활동참가율(%)', '고용률(%)', '실업률(%)'],
    ['BuPu', 'PiYG', 'RdPu']
):
    with tab:
        st.write(f"### {column_name} 데이터 시각화")
        
        if column_name not in df_korea_economics.columns:
            st.error(f"{column_name} 데이터가 없습니다.")
            continue

        # 데이터 정리
        df_selected = df_korea_economics[['행정구', column_name]].copy()
        df_selected['행정구'] = df_selected['행정구'].str.replace('\d+', '', regex=True).str.strip()
        df_selected[column_name] = pd.to_numeric(df_selected[column_name], errors='coerce').fillna(0)

        st.dataframe(df_selected, height=200)

        # GeoDataFrame과 병합
        merged = gdf_korea_sido.merge(df_selected, on='행정구', how='left')

        # 지도 시각화
        korea_map = folium.Map(location=[37, 126], zoom_start=7, tiles='cartodbpositron')
        title_html = f'<h3 align="center" style="font-size:20px"><b>전국 시군구 {column_name}</b></h3>'
        korea_map.get_root().html.add_child(folium.Element(title_html))

        folium.Choropleth(
            geo_data=merged,
            data=merged,
            columns=['행정구', column_name],
            key_on='feature.properties.행정구',
            legend_name=f'{column_name}',
            fill_color=fill_color,
            fill_opacity=0.7,
            line_opacity=0.3,
            nan_fill_color='white',
            nan_fill_opacity=0.4,
        ).add_to(korea_map)

        # 지도와 표를 나란히 배치
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(title_html, unsafe_allow_html=True)
            folium_static(korea_map)
        with col2:
            st.write(f"#### {column_name} 데이터 요약")
            st.dataframe(df_selected.describe())
