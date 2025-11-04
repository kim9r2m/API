import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# 🌦️ Page Setup
st.set_page_config(page_title="Open-Meteo Weather Dashboard", page_icon="🌤️", layout="wide")

st.title("🌦️ Open-Meteo Interactive Weather Dashboard")
st.write("지도에서 위치를 클릭하거나 도시 이름을 입력하여 기상 데이터를 시각화하세요.")

# --------------------------------------------------
# 1️⃣ 위치 선택
# --------------------------------------------------
st.sidebar.header("🌍 위치 선택 방법")
location_mode = st.sidebar.radio("위치를 선택하세요:", ["지도 클릭", "도시 이름 입력"])

lat, lon = None, None

if location_mode == "도시 이름 입력":
    city = st.sidebar.text_input("도시 이름 (예: Seoul, London, New York)")
    if city:
        with st.spinner("🔍 도시 좌표를 찾는 중..."):
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_response = requests.get(geo_url).json()
            results = geo_response.get("results")

            if results:
                lat = results[0]["latitude"]
                lon = results[0]["longitude"]
                st.success(f"📍 {results[0]['name']} ({results[0]['country']}) - 위도 {lat:.2f}, 경도 {lon:.2f}")
            else:
                st.error("⚠️ 해당 도시를 찾을 수 없습니다. 다시 입력해주세요.")
else:
    st.header("1️⃣ 지도에서 클릭하여 위치를 선택하세요")
    m = folium.Map(location=[37.57, 126.98], zoom_start=3)
    map_data = st_folium(m, height=400)
    if map_data and map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.success(f"📍 선택된 위치: 위도 {lat:.4f}, 경도 {lon:.4f}")

# --------------------------------------------------
# 2️⃣ 변수 선택 및 색상 매핑
# --------------------------------------------------
variable_options = {
    "기온 (Temperature °C)": "temperature_2m",
    "강수량 (Precipitation mm)": "precipitation",
    "풍속 (Wind Speed m/s)": "windspeed_10m",
    "습도 (Relative Humidity %)": "relativehumidity_2m"
}

# 🎨 Custom color mapping
variable_colors = {
    "temperature_2m": "#FF6B6B",   # red
    "precipitation": "#4D96FF",    # blue
    "windspeed_10m": "#FFD93D",    # yellow
    "relativehumidity_2m": "#6BCB77"  # green
}

selected_vars = st.multiselect(
    "📊 시각화할 변수를 선택하세요:",
    options=list(variable_options.keys()),
    default=["기온 (Temperature °C)"]
)

# Show colored tags for each selected variable
st.markdown("**선택된 변수:**")
if selected_vars:
    color_tags = []
    for var_label in selected_vars:
        var_key = variable_options[var_label]
        color = variable_colors.get(var_key, "#999")
        color_tags.append(f"<span style='background-color:{color}; color:white; padding:4px 8px; border-radius:8px; margin-right:5px;'>{var_label}</span>")
    st.markdown(" ".join(color_tags), unsafe_allow_html=True)
else:
    st.info("변수를 하나 이상 선택하세요.")

# --------------------------------------------------
# 3️⃣ 데이터 가져오기 및 시각화
# --------------------------------------------------
if lat and lon and selected_vars:
    hourly_vars = ",".join([variable_options[var] for var in selected_vars])
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly={hourly_vars}&timezone=Asia/Seoul"
    )

    with st.spinner("🌍 데이터를 불러오는 중..."):
        response = requests.get(api_url)
        data = response.json()

    hourly_data = data.get("hourly", {})
    df = pd.DataFrame(hourly_data)

    if not df.empty:
        st.header("2️⃣ 시간별 데이터 시각화")

        df_melted = df.melt(id_vars=["time"], var_name="variable", value_name="value")

        # ✅ Apply consistent color mapping
        fig = px.line(
            df_melted,
            x="time",
            y="value",
            color="variable",
            color_discrete_map=variable_colors,
            title=f"{lat:.2f}, {lon:.2f} 지역의 시간별 기상 변화"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.header("3️⃣ 원시 데이터 보기 (상위 24개)")
        st.dataframe(df.head(24))
    else:
        st.warning("⚠️ 데이터가 없습니다.")
