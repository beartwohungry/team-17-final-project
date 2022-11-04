from urllib.request import urlopen, quote
from pyecharts.charts import Pie
from pyecharts import options as opts
from PIL import Image
from plotly.subplots import make_subplots
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import streamlit as st
import streamlit_echarts
import plotly.graph_objects as go
import requests
import json
import cufflinks as cf

cf.set_config_file(offline=True)

image = Image.open('picture.png')
st.image(image, use_column_width=True)

st.title('Best Cities & Countries for Startups')
st.text('The dataset has about 1000 unique values and 9 columns. It shows best startups from\ndifferent cities and countries. Each startup is matched with four scores showing its\ncapacity in different aspects. Doing research on this dataset will provide us with\nknowledge about how to manage a success startup.')
st.header('Revised DataFrame') 
st.text('We split the \'city \' column into two columns \'city\'  \'country\' to make further \nresearch easier.')

plt.style.use('seaborn')

df = pd.read_csv('best cities for startups in 2022 - in 2022.csv', encoding='gbk')
for i in range(len(df)):
    if (df['sign of change in position'][i] != '+') & (df['sign of change in position'][i] != '-'):
        df['sign of change in position'].fillna('0', inplace = True)
df_2 = df['city'].str.split(',', expand = True)
df_3 = df.drop('city', axis = 1).join(df_2)
df_3.rename(columns={0:'city', 1:'country'}, inplace=True)
df_3.index = np.arange(1, len(df)+1)
st.dataframe(df_3)

df_country = df_3.groupby(['country']).mean()
df_country.sort_values(['total score'], axis=0, ascending=False, inplace=True)
df_country = df_country.reset_index()

#chart 1
st.header('Analysis 1: Best countries for startups')
st.subheader('Histogram of top 10 countries for startups') 
st.text('The histogram shows top 10 cities with highest total score.')
df_4 = df_country.head(10)
df_5 = df_4[['country','total score']].set_index('country')
fig_1 = df_5.iplot(asFigure=True, kind='bar',title='Top 10 Countries for Startups\n(Total Score)')
st.plotly_chart(fig_1)
st.text('We can find that Singapore has the highest average score for the best cities.')

#add a new column to the existing interactive table
city_count_list = []

for country in df_country.country:
    city_count_list.append(df_3[df_3['country'] == country].groupby('country')['country'].value_counts()[0])

#make a sort according to the number of the best cities in the country
df_city_count = df_3.country
result_city_count = df_city_count.value_counts()

#chart 2
st.subheader('Number of best cities in a country')
fig_2 = result_city_count[::-1][-10:].iplot(asFigure=True, kind='barh',title='Top 10 Countries for Startups\n(Best City Total)')
st.plotly_chart(fig_2)
st.text(' Although Singapore has the highest average score for the best cities, its number of\nbest cities is not even in the top ten. The US has the highest number of best cities\nand a high average score.')

#show new interactive table(score_top_10)
df_country.index = np.arange(1, len(df_country)+1)
df_country = df_country.drop('position', axis = 1)
df_country['best cities'] = city_count_list
st.dataframe(df_country[:10])

#add captions to pie charts
st.subheader('Proportion of the Best Cities in the Top 10 Countries')
st.text('It is an interactive pie. By clicking taggings on the right, you can add or erase\ncountries from pie chart.')
#make pie charts
score_top_countries = df_country[:10].country.tolist()#[' United Arab Emirates', ' Singapore', ' China', ' United States', ' South Korea', ' Israel', ' Estonia', ' Indonesia', ' Japan', ' India']#
value = df_country[:10]['best cities'].tolist()#[3, 1, 44, 257, 5, 13, 2, 5, 11, 37]

streamlit_echarts.st_pyecharts(
        Pie()
        .add(
            '',
            list(zip(score_top_countries, value)),
            center=["45%", "50%"],
            label_opts=opts.LabelOpts(
                is_show=True,
                position='outside',
                font_size=15,
                #b c d
                #country；count；position
                formatter='{b|{b}: }{c}  {per|{d}%}  ',
                background_color='#d6fffa',
                border_color='#aaa',
                border_width=1,
                border_radius=4,
                #Unable to find how to directly set lineheight, so try to call rich text
                rich={
                    "b": {"lineHeight": 29},  
                },
            ),
        )
        .set_global_opts(
            #title_opts=opts.TitleOpts(title='Proportion of the Best Cities in the Top 10 Countries'),
            legend_opts=opts.LegendOpts(type_='scroll', pos_left='80%', item_gap = 20, item_width = 20, orient='vertical'),# orient='vertical'
        )
    )

st.text('By looking at the pie chart, we can draw the conclusion that America is indeed the\nbest country for startups.')

# analyze the impact of each kind of scores on entrepreneurship by using stack graph
st.header('Analysis 2: Impact of each kind of scores on startups') 
st.subheader('Stacked chart of different scores')
st.text('In order to find clues about what element can affect a startup most, we use stack\nchart to analyze.')

#make stack bar
top_cities = df.head(20)
top_cities_info = top_cities[['city', 'quantity score', 'quality score', 'business score']].set_index('city')

fig_3 = top_cities_info.iplot(asFigure=True, kind='bar',barmode='stack')
st.plotly_chart(fig_3)
st.text('It is obvious that quality score accounts for the most part of total scores. We can\nassume that quality scores are determinant of total scores. To test the hypothesis,\nwe can use the line chart.')

#make line chart
st.subheader('Relationship between total score and other scores') 
fig_4 = make_subplots(rows=2, cols=2,subplot_titles=['Total & Other Scores','Total & Quality Scores','Total & Quantity Scores','Total & Business Scores'])
x_list = [i + 1 for i in range(20)]

fig_4.add_trace(go.Scatter(x=x_list, y=top_cities['total score'].to_list(), name='total score'), 
              row=1, col=1)
fig_4.add_trace(go.Scatter(x=x_list,y=top_cities['quality score'].to_list(), name='quality score'), 
              row=1, col=1)
fig_4.add_trace(go.Scatter(x=x_list,y=top_cities['quantity score'].to_list(), name='quantity score'), 
              row=1, col=1)
fig_4.add_trace(go.Scatter(y=top_cities['business score'].to_list(), name='business score'), 
              row=1, col=1)
fig_4.add_trace(go.Scatter(x=x_list, y=top_cities['total score'].to_list(), name='total score'), 
              row=1, col=2)
fig_4.add_trace(go.Scatter(x=x_list,y=top_cities['quality score'].to_list(), name='quality score'), 
              row=1, col=2)
fig_4.add_trace(go.Scatter(x=x_list,y=top_cities['total score'].to_list(), name='total score'), 
              row=2, col=1)
fig_4.add_trace(go.Scatter(x=x_list,y=top_cities['quantity score'].to_list(), name='quantity score'), 
              row=2, col=1)
fig_4.add_trace(go.Scatter(x=x_list,y=top_cities['total score'].to_list(), name='total score'), 
              row=2, col=2)
fig_4.add_trace(go.Scatter(y=top_cities['business score'].to_list(), name='business score'), 
              row=2, col=2)

fig_4.update_xaxes(title_text="countries' position", row=1, col=1) 
fig_4.update_xaxes(title_text="countries' position", row=1, col=2) 
fig_4.update_xaxes(title_text="countries' position", row=2, col=1)
fig_4.update_xaxes(title_text="countries' position", row=2, col=2)  

fig_4.update_yaxes(title_text="score", row=1, col=1)
fig_4.update_yaxes(title_text="score", row=2, col=1)

fig_4.update_layout(height=500, width = 700)
st.plotly_chart(fig_4)
st.text('We can see that the line of quality and the line of total score is quite close to\neach other and their trends are most the same. However, when it comes to quantity\nline and bussiness line, they are almost flat and have little relation with total\nscores.')
st.text('So quality score, that is, environmental score, plays the most important role in\naffecting the total score.')

##get geographical information about the city
#for i in df_3[df_3['country'] == ' China']['city'].index:
#    if df_3[df_3['country'] == ' China']['city'][i].find("'") != -1:
#        df_3.loc[i, 'city']= df_3.loc[i, 'city'].replace("'",'')

#addr_city = df_3[df_3['country'] == ' China']['city'].tolist()
 
#def gaode(addr_city):
#    para = {
#        "address": quote(addr_city), 
#        "key": "6c4d227098e7cda4345c79be1778faa6"
#    }
#    url = "https://restapi.amap.com/v3/geocode/geo?"
#    req = requests.get(url,para)
#    req = req.json()
#    m = req
#    return m

#lat_list = []
#lon_list = []
#for city in addr_city:
#    lon_list.append(gaode(city)['geocodes'][0]['location'].split(',')[0])
#    lat_list.append(gaode(city)['geocodes'][0]['location'].split(',')[1])

##update a new dataframe
#df_china=df_3[df_3['country'] == ' China']
#df_china.index = np.arange(1, len(df_china) + 1)
#df_china['lat'] = lat_list
#df_china['lon'] = lon_list
#df_china = df_china.drop('country', axis = 1)
#df_china['lon'] = df_china['lon'].astype(float)
#df_china['lat'] = df_china['lat'].astype(float)

##create a new column for sidebar filter items
#position_change = []

#for i in df_china.index:
#    if df_china['change in position from 2021'][i] != 'new':
#        if (df_china['sign of change in position'][i] == '+') & (int(df_china['change in position from 2021'][i]) > 100) :
#            position_change.append('substantial increase')
#        elif (df_china['sign of change in position'][i] == '+') & (int(df_china['change in position from 2021'][i]) > 10) :
#            position_change.append('obvious increase')
#        elif (df_china['sign of change in position'][i] == '+') & (int(df_china['change in position from 2021'][i]) <= 10):
#            position_change.append('small increase')
#        elif (df_china['sign of change in position'][i] == '-') & (int(df_china['change in position from 2021'][i]) > 100) :
#            position_change.append('substantial decrease')
#        elif (df_china['sign of change in position'][i] == '-') & (int(df_china['change in position from 2021'][i]) > 10) :
#            position_change.append('obvious decrease')
#        elif (df_china['sign of change in position'][i] == '-') & (int(df_china['change in position from 2021'][i]) <= 10):
#            position_change.append('small decrease')
#        else :
#            position_change.append('remain unchanged')
#    else:
#        position_change.append('new best city')

##delete existing columns and add new ones
#df_china = df_china.drop('sign of change in position', axis=1).drop('change in position from 2021', axis=1)
#df_china['position change'] = position_change

##save as new file (makes filtering quicker)
#df_china.to_csv('df_map_china.csv', index=False)
##read new file
df_map = pd.read_csv('df_map_china.csv')
st.subheader('Distribution of the best cities in China')
st.dataframe(df_map)

#create sidebar filters
#enter a value as a filter
form = st.sidebar.form('total_score_form')
total_score_filter = form.text_input('The total score is above?(please enter a integer number)', '0')
form.form_submit_button('Apply')

#choose a change as a filter
position_change_filter = st.sidebar.multiselect(
    'World ranking compared with 2021',
        df_map['position change'].unique(),
        df_map['position change'].unique()
)

#radio 
business_score_filter = st.sidebar.radio(
    "Choose business score level",
    ('>2','>1','all')
)
quality_score_filter = st.sidebar.radio(
    "Choose quality level",
    ('>50','>10','all')
)
quantity_score_filter = st.sidebar.radio(
    "Choose quantity level",
    ('>5','>1','all')
)

#filter by these filter
if total_score_filter!= '0':
    df_map = df_map[df_map['total score'] >= int(total_score_filter)]
    
df_map = df_map[df_map['position change'].isin(position_change_filter)]

if business_score_filter == '>2':
    df_map = df_map[df_map['business score'] > 2]
if business_score_filter == '>1':
    df_map = df_map[df_map['business score'] > 1]
if business_score_filter == 'all':
    df_map = df_map[df_map['business score'] > 0]

if quality_score_filter == '>50':
    df_map = df_map[df_map['quality score'].astype(float) > 50]
if quality_score_filter == '>10':
    df_map = df_map[df_map['quality score'].astype(float) > 10]
if quality_score_filter == 'all':
    df_map = df_map[df_map['quality score'].astype(float) > 0]

if quantity_score_filter == '>5':
    df_map = df_map[df_map['quantity score'].astype(float) > 5]
if quantity_score_filter == '>1':
    df_map = df_map[df_map['quantity score'].astype(float) > 1]
if quantity_score_filter == 'all':
    df_map = df_map[df_map['quantity score'].astype(float) > 0]

#draw a map
st.text('It is an interactive map.')
st.text('we use the geocoding of Gaode Mapsthe to determine the latitude and longitude of\ncities in China for our map.')
st.text('The map can show best cities for starups in China.')
st.text('* You can choose different conditions on the sidebar.')
st.map(df_map)
