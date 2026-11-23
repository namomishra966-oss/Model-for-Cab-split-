import streamlit as st
import pandas as pd
import requests
import math

st.set_page_config(page_title="College Cab-Sharing & Split", page_icon="🚕", layout="wide")

st.title("🚕 Smart College Cab-Sharing & Expense Split System")
st.markdown("एक ही रूट के छात्रों को खोजें, मैप पर लोकेशन देखें और कैब का किराया बराबर बांटें।")

if 'students' not in st.session_state:
    st.session_state.students = [
        {"Name": "Anant", "Phone": "9876543210", "Location": "Thane West", "lat": 19.2183, "lon": 72.9781},
        {"Name": "Harsh", "Phone": "9123456780", "Location": "Manpada, Thane", "lat": 19.2372, "lon": 72.9735},
        {"Name": "Riya", "Phone": "9988776655", "Location": "Waghbil, Thane", "lat": 19.2591, "lon": 72.9756}
    ]

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def get_coordinates(address, api_key):
    if api_key:
        try:
            url = f"https://geoapify.com{address}&apiKey={api_key}"
            res = requests.get(url).json()
            if res.get("features"):
                coords = res["features"][0]["geometry"]["coordinates"]
                return coords[1], coords[0]
        except:
            pass
    return 19.2250, 72.9800

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Geoapify API Key (वैकल्पिक)", type="password")
    radius_km = st.slider("मैचिंग दायरा (Radius in KM)", 1.0, 10.0, 3.0)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ नया छात्र जोड़ें (Add Student)")
    with st.form("add_student_form"):
        name = st.text_input("छात्र का नाम (Name)", placeholder="जैसे: Ananya")
        phone = st.text_input("मोबाइल नंबर (Phone)", placeholder="जैसे: 9876500000")
        location = st.text_input("पता / पिकअप लोकेशन", placeholder="जैसे: Thane West")
        submitted = st.form_submit_button("कनेक्ट करें और साथी खोजें 🔍")

        if submitted and name and location:
            lat, lon = get_coordinates(location, api_key)
            new_student = {"Name": name, "Phone": phone, "Location": location, "lat": lat, "lon": lon}
            st.session_state.students.append(new_student)
            st.success(f"✅ {name} को सफलतापूर्वक जोड़ दिया गया है!")

            st.markdown(f"### 🎯 {radius_km} km के अंदर उपलब्ध साथी:")
            matches = []
            for s in st.session_state.students:
                if s["Name"] != name:
                    dist = calculate_distance(lat, lon, s["lat"], s["lon"])
                    if dist <= radius_km:
                        matches.append({"Name": s["Name"], "Location": s["Location"], "Distance (KM)": dist, "Phone": s["Phone"]})
            
            if matches:
                st.table(pd.DataFrame(matches))
            else:
                st.warning("इस दायरे में अभी कोई और छात्र नहीं मिला।")

with col2:
    st.subheader("2️⃣ लाइव लोकेशन मैप (Live Map)")
    df_map = pd.DataFrame(st.session_state.students)
    st.map(df_map[['lat', 'lon']])

    st.subheader("3️⃣ कैब किराया बांटें (Cab Expense Split)")
    total_fare = st.number_input("कुल कैब किराया + टोल (₹ में)", min_value=0, value=400, step=50)
    selected_riders = st.multiselect(
        "कैब में कौन-कौन जा रहा है? (चुनें)",
        options=[s["Name"] for s in st.session_state.students],
        default=[s["Name"] for s in st.session_state.students[:3]]
    )

    if len(selected_riders) > 0:
        per_person = round(total_fare / len(selected_riders), 2)
        st.info(f"👥 कुल यात्री: **{len(selected_riders)}** | प्रति व्यक्ति हिस्सा: **₹{per_person}**")
    else:
        st.warning("कृपया कम से कम 1 यात्री चुनें।")

st.divider()
st.subheader("📋 सभी रजिस्टर्ड छात्रों की सूची")
st.dataframe(pd.DataFrame(st.session_state.students)[["Name", "Phone", "Location"]], use_container_width=True)
