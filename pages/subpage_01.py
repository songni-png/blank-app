#######################
# 라이브러리 임포트
import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import altair as alt
import plotly.express as px
import json
import os
import glob

#######################
# 타이틀 텍스트 출력
st.title('2016-2022 행정구역(시도) 별 경제성장률')

#######################
# 데이터 경로 설정
data_path = os.path.abspath('시도별_경제성장률.csv')

# CSV 데이터 불러오기
df_korea_growth = pd.read_csv('시도별_경제성장률.csv', header=0, encoding='utf-8')
df_korea_economics = pd.read_csv('행정구역_시도_별_경제활동인구_20241126130730.csv', header=1, encoding='utf-8')
korea_geojson = json.load(open('KOREA_시도_geoJSON.json', encoding="UTF-8")) # json 파일 불러오기

#######################
# 데이터 전처리

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
# 열 순서 변경
df_korea_economics = df_korea_economics[['city','code','year','category','population']]

# '계'를 '전국'으로 변경
df_korea_economics['city'] = df_korea_economics['city'].replace('계', '전국')

# CSV에서 city와 code의 매핑 생성
csv_mapping = dict(zip(df_korea_economics['city'], df_korea_economics['code']))

# GeoJSON 데이터를 GeoDataFrame으로 변환
if isinstance(korea_geojson, dict):  # GeoJSON이 딕셔너리 형식이라면
    korea_geojson = gpd.GeoDataFrame.from_features(korea_geojson['features'])

# GeoJSON의 CTPRVN_CD 값을 CSV 매핑을 기반으로 업데이트
korea_geojson['CTPRVN_CD'] = korea_geojson['CTP_KOR_NM'].map(csv_mapping).fillna(korea_geojson['CTPRVN_CD'])

# 숫자와 문자를 분리하는 코드 
df_korea_growth['city'] = df_korea_growth['행정구역별(1)']

df_korea_growth.drop('행정구역별(1)', axis=1, inplace=True)

# 데이터를 멜팅하여 데이터프레임으로 변환
df_korea_growth = df_korea_growth.melt(
    id_vars='city',
    var_name='year',
    value_name='growth_rate',
)

# city가 같은 열을 바탕으로 code 데이터를 추가
df_korea_growth['code'] = df_korea_growth['city'].map(csv_mapping)

# 'growth_rate' 열을 정수로 변환
df_korea_growth['growth_rate'] = df_korea_growth['growth_rate'].replace('-','0').fillna('0').astype(float)

df_korea_growth = df_korea_growth[['city','code','year','growth_rate']]

# 연도 리스트를 내림차순으로 정렬
year_list = list(df_korea_growth.year.unique())[-1]

#######################
# 사이드바 설정
with st.sidebar:
    st.title('대한민국 경제성장률 대시보드')
    
    year_list = list(df_korea_growth.year.unique())[::-1]  # 연도 리스트를 내림차순으로 정렬
   
    selected_year = st.selectbox('연도 선택', year_list) # selectbox에서 연도 선택
    
    df_selected_year = df_korea_growth.query('year == @selected_year') # 선택한 연도에 해당하는 데이터만 가져오기
    df_selected_year_sorted = df_selected_year.sort_values(by="year", ascending=False) # 선택한 연도에 해당하는 데이터를 인구수를 기준으로 내림차순 정렬

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('컬러 테마 선택', color_theme_list)



#######################
# 그래프 함수

# Heatmap 그래프
def make_heatmap(input_df_korea_growth, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df_korea_economics).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="연도", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap
 
# Choropleth map
def make_choropleth(input_df_korea_growth,input_korea_geojson,input_column, input_color_theme):
    # 'code' 열을 문자열로 변환 
    input_df_korea_growth['code'] = input_df_korea_growth['code'].astype(str)
    
    choropleth = px.choropleth_mapbox(input_df_korea_growth,
                                      geojson=input_korea_geojson,
                                      locations='code', 
                                      featureidkey='properties.CTPRVN_CD',
                                      mapbox_style='carto-darkmatter',
                                      zoom=5, 
                                      center = {"lat": 35.9, "lon": 126.98},
                                      color=input_column, 
                                      color_continuous_scale=input_color_theme,
                                      range_color=(0, max(input_df_korea_growth.growth_rate)),
                                      labels={'growth_rate':'경제성장률','code':'시도코드', 'city':'시도명'},
                                      hover_data=['city', 'growth_rate']
                                      )
    choropleth.update_geos(fitbounds="locations", visible=False)
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# 대시보드 레이아웃
col = st.columns((5,5), gap='large')

with col[0]: # 왼쪽
  st.markdown('#### ' + str(selected_year) + '년 경제성장률')
    
  choropleth = make_choropleth(df_selected_year, korea_geojson, 'growth_rate', selected_color_theme)
  st.plotly_chart(choropleth, use_container_width=True)
    
  heatmap = make_heatmap(df_korea_growth, 'year', 'city', 'growth_rate', selected_color_theme)
  st.altair_chart(heatmap, use_container_width=True)

with col[1]:
  st.markdown('#### 시도별 경제성장률')

  st.dataframe(df_selected_year_sorted,
              column_order=("city", "growth_rate"),
              hide_index=True,
              width=500,
              column_config={
                  "city": st.column_config.TextColumn(
                    "시도명",
                  ),
                  "growth_rate": st.column_config.ProgressColumn(
                    'growth_rate',
                    format="%f",
                    min_value=0,
                    max_value=max(df_selected_year_sorted.growth_rate),
                 )}
             )
  df_korea_growth
