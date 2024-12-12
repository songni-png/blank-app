# 라이브러리 임포트
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import json
import os
import glob
# 타이틀 텍스트 출력
st.title('2000-2023 행정구역(시도) 별 경제활동인구')

st.write('.')

# 사이드바
st.sidebar.write('## 연도와 항목을 고르시오.') 

# 데이터 경로 설정
data_path = os.path.abspath('행정구역_시도_별_경제활동인구_20241126130730.csv')

# CSV 데이터 불러오기
df_korea_economics = pd.read_csv(data_path, header=1, encoding='utf-8')

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

# 연도 리스트를 내림차순으로 정렬
year_list = list(df_korea_economics.year.unique())[::-1]
# NumPy 배열로 변환 
year_list = [np.int64(year) for year in year_list]
# 연도 리스트를 내림차순으로 정렬
category_list = list(df_korea_economics.category.unique())[::-1]

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


# 그래프 함수

# Heatmap 그래프
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
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



# 대시보드 레이아웃
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]: # 왼쪽
    st.markdown('#### 증가/감소')

    df_population_difference_sorted = calculate_population_difference(df, selected_year, selected_category)

    if selected_year > 2014:
        first_state_name = df_population_difference_sorted.city.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2014:
        last_state_name = df_population_difference_sorted.city.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.population.iloc[-1])   
        last_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])   
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    
    st.markdown('#### 변동 시도 비율')

    if selected_year > 2014:
        # Filter states with population difference > 5000
        # df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
        df_greater_5000 = df_population_difference_sorted[df_population_difference_sorted.population_difference > 5000]
        df_less_5000 = df_population_difference_sorted[df_population_difference_sorted.population_difference < -5000]
        
        # % of States with population difference > 5000
        states_migration_greater = round((len(df_greater_5000)/df_population_difference_sorted.city.nunique())*100)
        states_migration_less = round((len(df_less_5000)/df_population_difference_sorted.city.nunique())*100)
        donut_chart_greater = make_donut(states_migration_greater, '전입', 'green')
        donut_chart_less = make_donut(states_migration_less, '전출', 'red')
    else:
        states_migration_greater = 0
        states_migration_less = 0
        donut_chart_greater = make_donut(states_migration_greater, '전입', 'green')
        donut_chart_less = make_donut(states_migration_less, '전출', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('증가')
        st.altair_chart(donut_chart_greater)
        st.write('감소')
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown('#### ' + str(selected_year) + '년 ' + str(selected_category))
    
    choropleth = make_choropleth(df_selected_year, korea_geojson, 'population', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(df, 'year', 'city', 'population', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)
    

with col[2]:
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
