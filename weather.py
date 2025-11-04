import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# 🌦️ Streamlit Page Setup
st.set_page_config(page_title="Open-Meteo Interactive Weather Dashboard", page_icon="🌤️", layout="wide")

st.title("🌤️ Open-Meteo Interactive Weather Dashboard")
st.write("지도에서 위치를 클릭하면 해당 지역의 시간별 기상 데이터를 불러옵니다.")

# --------------------------------------------------
# 1️⃣ User selects variable(s)
# --------------------------------------------------
variable_options = {
    "기온 (Temperature °C)": "temperature_2m",
    "강수량 (Precipitation mm)": "precipitation",
    "풍속 (Wind Speed m/s)": "windspeed_10m",
    "습도 (Relative Humidity %)": "relativehumidity_2m"
}

selected_vars = st.multiselect(
    "📊 시각화할 변수를 선택하세요:",
    options=list(variable_options.keys()),
    default=["기온 (Temperature °C)"]
)

# --------------------------------------------------
# 2️⃣ Map for selecting a location
# --------------------------------------------------
st.header("1️⃣ 지역 선택 (지도를 클릭하세요)")
m = folium.Map(location=[37.57, 126.98], zoom_start=4)
map_data = st_folium(m, height=400)

# --------------------------------------------------
# 3️⃣ When a user clicks a location
# --------------------------------------------------
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    st.success(f"📍 선택된 위치: 위도 {lat:.4f}, 경도 {lon:.4f}")

    # Create API parameter string (e.g., hourly=temperature_2m,precipitation)
    hourly_vars = ",".join([variable_options[var] for var in selected_vars])

    # --------------------------------------------------
    # 4️⃣ Call Open-Meteo API
    # --------------------------------------------------
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly={hourly_vars}&timezone=Asia/Seoul"
    )

    with st.spinner("🌍 데이터를 불러오는 중..."):
        response = requests.get(url)
        data = response.json()

    hourly_data = data.get("hourly", {})
    df = pd.DataFrame(hourly_data)

    if not df.empty:
        st.header("2️⃣ 시간별 데이터 시각화")

        # Melt DataFrame for easier plotting
        df_melted = df.melt(id_vars=["time"], var_name="variable", value_name="value")

        # Display chart
        fig = px.line(
            df_melted,
            x="time",
            y="value",
            color="variable",
            title=f"{lat:.2f}, {lon:.2f} 지역의 시간별 기상 변화",
        )
        st.plotly_chart(fig, use_container_width=True)

        # --------------------------------------------------
        # 5️⃣ Show raw data
        # --------------------------------------------------
        st.header("3️⃣ 원시 데이터 보기 (상위 24개)")
        st.dataframe(df.head(24))
    else:
        st.warning("⚠️ 해당 지역에 대한 데이터가 없습니다.")
