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
st.title('2000-2023 행정구역(시도) 별 경제활동인구')

#######################
# 데이터 경로 설정
data_path = os.path.abspath('행정구역_시도_별_경제활동인구_20241126130730.csv')

# CSV 데이터 불러오기
df_korea_economics = pd.read_csv(data_path, header=1, encoding='utf-8')

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
# 'population' 열을 정수로 변환
df_korea_economics['population'] = df_korea_economics['population'].replace('-','0').fillna('0').astype(float)
# 열 순서 변경
df_korea_economics = df_korea_economics[['city','code','year','category','population']]

# 연도 리스트를 내림차순으로 정렬
year_list = list(df_korea_economics.year.unique())[::-1]
# NumPy 배열로 변환 
year_list = [np.int64(year) for year in year_list]
# 연도 리스트를 내림차순으로 정렬
category_list = list(df_korea_economics.category.unique())[::-1]

# CSV에서 city와 code의 매핑 생성
csv_mapping = dict(zip(df_korea_economics['city'], df_korea_economics['code']))

# GeoJSON 데이터를 GeoDataFrame으로 변환
if isinstance(korea_geojson, dict):  # GeoJSON이 딕셔너리 형식이라면
    korea_geojson = gpd.GeoDataFrame.from_features(korea_geojson['features'])


# GeoJSON의 CTPRVN_CD 값을 CSV 매핑을 기반으로 업데이트
korea_geojson['CTPRVN_CD'] = korea_geojson['CTP_KOR_NM'].map(csv_mapping).fillna(korea_geojson['CTPRVN_CD'])



#######################
# 사이드바 설정
with st.sidebar:
    st.title('대한민국 경제활동인구 대시보드')
    
    year_list = list(df_korea_economics.year.unique())[::-1]  # 연도 리스트를 내림차순으로 정렬
    category_list = list(df_korea_economics.category.unique())  # 카테고리 리스트
    
    selected_year = st.selectbox('연도 선택', year_list) # selectbox에서 연도 선택
    selected_category = st.selectbox('카테고리 선택', category_list) # selectbox에서 카테고리 선택

    df_selected_year = df_korea_economics.query('year == @selected_year & category == @selected_category') # 선택한 연도와 카테고리에 해당하는 데이터만 가져오기
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False) # 선택한 연도와 카테고리에 해당하는 데이터를 인구수를 기준으로 내림차순 정렬

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('컬러 테마 선택', color_theme_list)

#######################
 # 화면을 2개의 컬럼으로 나누기
cl1, cl2 = st.columns(2)

# 첫번째 컬럼(카테고리별 데이터 보기)
with cl1:
    with st.expander("연도별 데이터 보기"):    # 확장창
        st.dataframe(df_selected_year_sorted.style.background_gradient(cmap="Blues"))  # 데이터프레임 출력
        csv = df_selected_year_sorted.to_csv(index = False).encode('utf-8')  # 데이터프레임을 csv로 변환
        st.download_button(
            "데이터 다운로드",    # 다운로드 버튼 명칭
            data = csv,          # 데이터 유형
            file_name = "Year.csv",  # 파일명
            mime = "text/csv",   # 파일 형식
            help = 'CSV 파일로 데이터를 다운로드하기 위해 클릭하세요.' # 마우스 버튼 이동시 도움말 표시
        )

# 두번째 컬럼(지역별 데이터 보기)
with cl2:
    with st.expander("항목별 데이터 보기"):
        category = df_selected_category_sorted.groupby(   # 지역별 판매액 계산
            by = "city",              # 지역별 그룹화
            as_index = False            # 인덱스 사용 안함
            )                           # 판매액 합계
        st.dataframe(category.style.background_gradient(cmap="Oranges"))  # 데이터프레임 출력
        csv = df_selected_category_sorted.to_csv(index = False).encode('utf-8')   # 데이터프레임을 csv로 변환
        st.download_button(
            "데이터 다운로드", 
            data = csv, 
            file_name = "Category.csv", 
            mime = "text/csv",
            help = 'CSV 파일로 데이터를 다운로드하기 위해 클릭하세요.'
        )

#######################
# 그래프 함수

# Heatmap 그래프
def make_heatmap(input_df_korea_economics, input_y, input_x, input_color, input_color_theme):
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
def make_choropleth(input_df_korea_economics,input_korea_geojson,input_column, input_color_theme):
    # 'code' 열을 문자열로 변환 
    input_df_korea_economics['code'] = input_df_korea_economics['code'].astype(str)
    
    choropleth = px.choropleth_mapbox(input_df_korea_economics,
                                      geojson=input_korea_geojson,
                                      locations='code', 
                                      featureidkey='properties.CTPRVN_CD',
                                      mapbox_style='carto-darkmatter',
                                      zoom=5, 
                                      center = {"lat": 35.9, "lon": 126.98},
                                      color=input_column, 
                                      color_continuous_scale=input_color_theme,
                                      range_color=(0, max(input_df_korea_economics.population)),
                                      labels={'population':selected_category, 'code':'시도코드', 'city':'시도명'},
                                      hover_data=['city', 'population']
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

df_korea_economics['population'] = (
    df_korea_economics['population']
    .replace('-', '0')  # '-'를 0으로 대체
    .fillna('0')        # NaN을 0으로 대체
    .astype(float)      # 숫자로 변환
)




# 대시보드 레이아웃
col = st.columns((5,5), gap='large')

with col[0]: # 왼쪽
  st.markdown('#### ' + str(selected_year) + '년 ' + str(selected_category))
    
  choropleth = make_choropleth(df_selected_year, korea_geojson, 'population', selected_color_theme)
  st.plotly_chart(choropleth, use_container_width=True)
    
  heatmap = make_heatmap(df_korea_economics, 'year', 'city', 'population', selected_color_theme)
  st.altair_chart(heatmap, use_container_width=True)

with col[1]:
  st.markdown('#### 시도별 ' + str(selected_category))

  st.dataframe(df_selected_year_sorted,
              column_order=("city", "population"),
              hide_index=True,
              width=500,
              column_config={
                  "city": st.column_config.TextColumn(
                    "시도명",
                  ),
                  "population": st.column_config.ProgressColumn(
                    str(selected_category),
                    format="%f",
                    min_value=0,
                    max_value=max(df_selected_year_sorted.population),
                 )}
             )






