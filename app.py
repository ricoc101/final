"""
Name: Fernando A. Rivera Diaz
CS230: Section 4
Data: Motor Vehicle Crashes in MA in 2017 (145068 rows, use 10000)
URL:
Description:
The program works.

"""
import streamlit as st
import pydeck as pdk
import pandas as pd
import random as rd
import matplotlib.pyplot as plt

def read_data(path="C:/Users/Fernando/Desktop/SCHOOL/PythonProjects/Final/2017_Crashes_10000_sample.csv",index="OBJECTID"):
    return pd.read_csv(path).set_index(index)


def filter_data(towns=["WORCESTER","BOSTON","SPRINGFIELF","LOWELL","NEW BEDFORD"], weather=["Clear"], cars=1):
    df=read_data()
    df=df.loc[df['CITY_TOWN_NAME'].isin(towns)]
    df=df.loc[df['WEATH_COND_DESCR'].isin(weather)]
    df = df.loc[df['NUMB_VEHC']==cars]
    return df

def all_towns(df):
    lst=[]
    for ind, row in df.iterrows():
        if row['CITY_TOWN_NAME'] not in lst:
            lst.append(row['CITY_TOWN_NAME'])
    return lst
def all_weather(df):
    lst=[]
    for ind, row in df.iterrows():
        if row['WEATH_COND_DESCR'] not in lst:
            lst.append(row['WEATH_COND_DESCR'])
    return lst

def count_towns(list, df, filter):
    if filter=="towns":
        return [df.loc[df['CITY_TOWN_NAME'].isin([town])].shape[0] for town in list]
    if filter=="weather":
        return [df.loc[df['WEATH_COND_DESCR'].isin([town])].shape[0] for town in list]

#counts=[df[df['CITY_TOWN_NAME'] == town].shape[0] for town in towns]
def generate_pie_chart(counts, towns, title="Pie Chart"):
    plt.figure()
    plt.pie(counts, labels=towns,autopct="%.1f%%",labeldistance=1.3)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.title(title)
    return plt
def generate_bar_chart(dict, title):
    plt.figure()
    x=dict.keys() #[PY5]
    y=dict.values()
    plt.bar(x,y)
    plt.title(title)
    return plt
def generate_map(df, type="Simple"): #[PY1]
    df = df.dropna(subset=['LAT', 'LON']) #got this line of code from ChatGPT. drops null values
    df.rename(columns={"LAT": "lat", "LON": "lon"}, inplace=True)
    if df.empty:
        st.write("No valid latitude or longitude values found in the DataFrame.")
    else:
        if type == "Simple":
            st.title('Simple Map')
            # The most basic map, st.map(df)
            st.map(df)
        elif type=="Scatter":
            map_df=df.filter(['CITY_TOWN_NAME','lat','lon', 'WEATH_COND_DESCR', 'CRASH_DATE_TEXT'])
            st.title("Scatterplot map")
            view_state = pdk.ViewState(
                latitude=map_df["lat"].mean(),
                longitude=map_df["lon"].mean(),
                zoom=8,
                pitch=0)
            layer = pdk.Layer('ScatterplotLayer',
                           data=map_df,
                           get_position='[lon, lat]',
                           get_radius=900,
                           get_color=[250, 50, 50],
                           pickable=True
                           )
            tool_tip = {'html': "Town:<br/> <b>{CITY_TOWN_NAME}</b> <br/> <b>{WEATH_COND_DESCR}<b> "
                                "<br/> <b>{CRASH_DATE_TEXT}<b> ",
                    'style': {'backgroundColor': 'steelblue', 'color': 'white'}}
            map = pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v12',
                initial_view_state=view_state,
                layers=[layer],  # The following layer would be on top of the previous layers
                tooltip=tool_tip)
            st.pydeck_chart(map)
def top5(df, column):
    if column=="Towns":
        sorted_crashes = sorted(town_crashes(df).items(), key=lambda item: item[1], reverse=True) #got this from ChatGPT
    if column=="Weather":
        sorted_crashes = sorted(weather_crashes(df).items(), key=lambda item: item[1], reverse=True)
    return dict(sorted_crashes[:5])


def town_crashes(df): #[PY5]
    df=df.sort_values(['CITY_TOWN_NAME','CRASH_DATE_TEXT'], ascending=[True, False]) #[DA2]
    crashes_per_town={}
    for ind, row in df.iterrows():
        town=row['CITY_TOWN_NAME']
        if town in crashes_per_town:
            crashes_per_town[town]+=1
        else:
            crashes_per_town[town] = 1
    return crashes_per_town
def weather_crashes(df):
    df=df.sort_values(['WEATH_COND_DESCR','CRASH_DATE_TEXT'], ascending=[True, False]) #[DA2]
    crashes_per_weather={}
    for ind, row in df.iterrows():
        town=row['WEATH_COND_DESCR']
        if town in crashes_per_weather:
            crashes_per_weather[town]+=1
        else:
            crashes_per_weather[town] = 1
    return crashes_per_weather
def main():
    st.title("Car Crashes in Massachussetts in 2017")
    df=read_data()
    default=filter_data()

    st.sidebar.write("Please choose your options to display data.")
    towns=st.sidebar.multiselect("Select a Town: ", all_towns(df))
    weather=st.sidebar.multiselect("Select a Weather Pattern: ", all_weather(df))
    cars=st.sidebar.slider("Select amount of cars in crash: ",1,12)
    data=filter_data(towns, weather,cars)

    series = count_towns(towns, data, "towns")
    top_5_weather=[]
    for i in top5(df,"Weather"):
        top_5_weather.append(i)
    count_weather = count_towns(top_5_weather, df, "weather")
    top_5_towns=[]
    for i in top5(df,"Towns"):
        top_5_towns.append(i)
    top_towns=count_towns(top_5_towns,df,"towns")

    selected_vis = st.sidebar.radio("Please select the visualization you want:",["Main","Scatter", "Bar Chart", "Pie Chart"])
    if selected_vis=="Main":
        st.pyplot(generate_bar_chart(top5(df, "Towns"), "Towns with Most Crashes"))
        st.pyplot(generate_pie_chart(count_weather,top_5_weather),"Weather with Most Crashes")
        generate_map(df)
    elif selected_vis == "Scatter":
        st.write("View a Map of Crashes")
        if data.empty:
            st.write("Displaying default map.")
            generate_map(default, "Scatter")
        else:
            generate_map(data, "Scatter")
    elif selected_vis=="Bar Chart":
        if data.empty:
            st.pyplot(generate_bar_chart(town_crashes(default), "Top 5 Towns"))
        else:
            st.pyplot(generate_bar_chart(town_crashes(data), "Bar Chart"))
    elif selected_vis=="Pie Chart":
        if data.empty:
            st.pyplot(generate_pie_chart(top_towns, top_5_towns),"Top 5 Towns")
        else:
            st.pyplot(generate_pie_chart(series, towns))
main()

