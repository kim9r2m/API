import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium

st.title("🌤️ Open-Meteo Interactive Weather Dashboard")
st.write("지도에서 위치를 클릭하면 해당 지역의 시간별 기온 데이터를 불러옵니다.")

# 1️⃣ Create map
m = folium.Map(location=[37.57, 126.98], zoom_start=4)
map_data = st_folium(m, height=400)

# 2️⃣ When user clicks on the map
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    st.success(f"📍 선택된 위치: 위도 {lat:.4f}, 경도 {lon:.4f}")

    # 3️⃣ Call the API
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Asia/Seoul"
    data = requests.get(url).json()

    df = pd.DataFrame({
        "time": data["hourly"]["time"],
        "temperature (°C)": data["hourly"]["temperature_2m"]
    })

    # 4️⃣ Draw chart
    st.header("2️⃣ 시간별 기온 변화 그래프")
    fig = px.line(df, x="time", y="temperature (°C)", title=f"{lat:.2f}, {lon:.2f} 지역의 시간별 기온")
    st.plotly_chart(fig, use_container_width=True)

    # 5️⃣ Show table
    st.header("3️⃣ 원시 데이터 보기 (상위 24개)")
    st.dataframe(df.head(24))
