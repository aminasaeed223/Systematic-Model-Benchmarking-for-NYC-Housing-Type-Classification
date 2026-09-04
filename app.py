import joblib
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NYC Airbnb Room Type Predictor",
    page_icon="🗽",
    layout="wide",
)

BG_IMAGE_URL = "https://images.unsplash.com/photo-1417632993443-302f4897cf67?fm=jpg&q=80&w=1920&auto=format&fit=crop"

ORANGE = "#FF6B1A"
ORANGE_DIM = "#B84E12"

# Room types color-coded like real NYC subway lines
ROOM_STYLE = {
    "Entire home/apt": {"color": "#00933C", "line": "4 · 5 · 6"},        # Lexington Ave green
    "Private room":    {"color": "#FF6B1A", "line": "B · D · F · M"},    # 6th Ave orange
    "Shared room":     {"color": "#0039A6", "line": "A · C · E"},        # 8th Ave blue
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background:
            linear-gradient(180deg, rgba(5,5,7,0.88) 0%, rgba(5,5,7,0.72) 45%, rgba(5,5,7,0.92) 100%),
            url('{BG_IMAGE_URL}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {{
        background: #0B0B0D;
        border-right: 1px solid rgba(255,107,26,0.25);
        min-width: 380px !important;
        max-width: 420px !important;
        width: 380px !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        width: 380px !important;
        overflow-y: auto !important;
        scrollbar-width: auto;
        scrollbar-color: {ORANGE} #1B1B1F;
    }}
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {{
        width: 10px;
    }}
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track {{
        background: #1B1B1F;
    }}
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {{
        background-color: {ORANGE};
        border-radius: 8px;
        border: 2px solid #1B1B1F;
    }}
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb:hover {{
        background-color: {ORANGE_DIM};
    }}
    [data-testid="stSidebar"] * {{
        color: #F2F2F0 !important;
    }}
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: {ORANGE} !important;
    }}
    [data-testid="stSidebar"] .section-label {{
        color: {ORANGE} !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 0.82rem;
        text-transform: none;
        margin: 1.1rem 0 0.3rem 0;
    }}

    /* ---------- Inputs: solid dark, orange border, white bold text ---------- */
    [data-testid="stSidebar"] input,
    [data-testid="stMain"] input {{
        background-color: #1B1B1F !important;
        color: #FFFFFF !important;
        font-weight: 600;
        border: 1.5px solid rgba(255,107,26,0.35) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSidebar"] input:focus,
    [data-testid="stMain"] input:focus {{
        border-color: {ORANGE} !important;
        box-shadow: 0 0 0 1px {ORANGE} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stMain"] [data-baseweb="select"] > div {{
        background-color: #1B1B1F !important;
        border: 1.5px solid rgba(255,107,26,0.35) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stMain"] [data-baseweb="select"] span {{
        color: #FFFFFF !important;
        font-weight: 600;
    }}
    [data-testid="stSidebar"] svg,
    [data-testid="stMain"] svg {{
        fill: {ORANGE} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stNumberInputStepUp"],
    [data-testid="stSidebar"] [data-testid="stNumberInputStepDown"],
    [data-testid="stMain"] [data-testid="stNumberInputStepUp"],
    [data-testid="stMain"] [data-testid="stNumberInputStepDown"] {{
        background-color: #1B1B1F !important;
        border-color: rgba(255,107,26,0.35) !important;
    }}

    /* Even, consistent spacing between every sidebar field */
    [data-testid="stSidebar"] .stNumberInput,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider {{
        margin-bottom: 1.1rem;
    }}
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{
        margin-bottom: 0.25rem;
    }}

    /* Slider track/thumb in orange */
    [data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {{
        background-color: {ORANGE} !important;
        border-color: {ORANGE} !important;
    }}

    /* ---------- Hero ---------- */
    .hero-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin-bottom: 0.1rem;
    }}
    .hero-title span {{ color: {ORANGE}; }}

    .hero-subtitle {{
        color: #D8D8DC;
        font-size: 1.02rem;
        margin-bottom: 1.4rem;
    }}

    /* ---------- Main-panel cards (same dark treatment as sidebar) ---------- */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #121214;
        border: 1px solid rgba(255,107,26,0.20);
        border-radius: 18px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    }}
    [data-testid="stVerticalBlockBorderWrapper"] > div > div {{
        padding: 1.4rem 1.6rem;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] label,
    [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stVerticalBlockBorderWrapper"] span {{
        color: #F2F2F0 !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] h3,
    [data-testid="stVerticalBlockBorderWrapper"] h4 {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: {ORANGE} !important;
    }}

    .stButton > button {{
        background: {ORANGE};
        color: #0B0B0D;
        font-weight: 700;
        font-family: 'Poppins', sans-serif;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        width: 100%;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(255,107,26,0.45);
        color: #0B0B0D;
    }}

    .result-badge {{
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        color: white;
        font-family: 'Poppins', sans-serif;
        border: 1px solid rgba(255,255,255,0.15);
    }}
    .result-badge .label {{
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 500;
    }}
    .result-badge .value {{
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 0.1rem;
    }}
    .result-badge .line {{
        font-size: 0.8rem;
        opacity: 0.9;
        margin-top: 0.3rem;
    }}

    .placeholder-box {{
        border: 1.5px dashed rgba(255,107,26,0.35);
        border-radius: 14px;
        padding: 2.2rem 1.5rem;
        text-align: center;
        color: #C9C9CE;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_pipeline():
    return joblib.load("Model_Pipeline.pkl")


@st.cache_data
def load_meta():
    df = pd.read_csv("nyc_dataset.csv")
    neighbourhood_groups = sorted(df["neighbourhood_group"].dropna().unique().tolist())
    neighbourhood_by_group = {
        g: sorted(df[df["neighbourhood_group"] == g]["neighbourhood"].dropna().unique().tolist())
        for g in neighbourhood_groups
    }
    # Average coordinates per neighbourhood, so picking one can center the map correctly
    neighbourhood_coords = (
        df.groupby("neighbourhood")[["latitude", "longitude"]].mean().to_dict("index")
    )
    price_max = float(df["price"].quantile(0.99))
    nights_max = float(df["minimum_nights"].quantile(0.99))
    return neighbourhood_groups, neighbourhood_by_group, neighbourhood_coords, price_max, nights_max


pipeline = load_pipeline()
neighbourhood_groups, neighbourhood_by_group, neighbourhood_coords, price_max, nights_max = load_meta()


def _sync_coords_to_neighbourhood():
    nb = st.session_state.get("neighbourhood_select")
    coords = neighbourhood_coords.get(nb)
    if coords:
        st.session_state.lat_input = round(coords["latitude"], 5)
        st.session_state.lon_input = round(coords["longitude"], 5)


def _reset_neighbourhood_for_borough():
    opts = neighbourhood_by_group[st.session_state.borough_select]
    st.session_state.neighbourhood_select = opts[0]
    _sync_coords_to_neighbourhood()


# ---------------- Sidebar: all inputs ----------------
with st.sidebar:
    st.markdown("### Listing details")

    st.markdown('<div class="section-label">Location</div>', unsafe_allow_html=True)
    neighbourhood_group = st.selectbox(
        "Borough", neighbourhood_groups, key="borough_select", on_change=_reset_neighbourhood_for_borough
    )

    neighbourhood_options = neighbourhood_by_group[neighbourhood_group]
    if st.session_state.get("neighbourhood_select") not in neighbourhood_options:
        st.session_state.neighbourhood_select = neighbourhood_options[0]

    neighbourhood = st.selectbox(
        "Neighbourhood", neighbourhood_options, key="neighbourhood_select", on_change=_sync_coords_to_neighbourhood
    )

    if "lat_input" not in st.session_state:
        _sync_coords_to_neighbourhood()

    latitude = st.number_input("Latitude", key="lat_input", format="%.5f")
    longitude = st.number_input("Longitude", key="lon_input", format="%.5f")
    st.caption("Latitude/Longitude auto-fill from the neighbourhood — edit them for an exact spot.")

    st.markdown('<div class="section-label">Pricing & stay</div>', unsafe_allow_html=True)
    price = st.number_input("Price per night ($)", min_value=0, max_value=int(price_max), value=100)
    minimum_nights = st.number_input("Minimum nights", min_value=1, max_value=int(nights_max), value=2)

    st.markdown('<div class="section-label">Activity</div>', unsafe_allow_html=True)
    number_of_reviews = st.number_input("Number of reviews", min_value=0, value=10)
    reviews_per_month = st.number_input("Reviews per month", min_value=0.0, value=1.0, step=0.1)
    calculated_host_listings_count = st.number_input("Host's total listings", min_value=1, value=1)
    availability_365 = st.slider("Availability (days/year)", 0, 365, 180)

    st.markdown("")
    predict_clicked = st.button("Predict room type")

# ---------------- Main panel ----------------
st.markdown(
    '<div class="hero-title">NYC Airbnb <span>Room Type</span> Predictor</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-subtitle">Filter out your desired room type by choosing different '
    "parameters in the sidebar.</div>",
    unsafe_allow_html=True,
)

map_col, result_col = st.columns([1.1, 1], gap="medium")

with map_col:
    with st.container(border=True):
        st.markdown("#### Location")
        st.map(
            pd.DataFrame({"lat": [latitude], "lon": [longitude]}),
            zoom=13,
            size=200,
            color="#FF6B1A",
        )

with result_col:
    with st.container(border=True):
        st.markdown("#### Prediction")

        if not predict_clicked:
            st.markdown(
                '<div class="placeholder-box">Click <b>Predict room type</b> in the sidebar '
                "to see a result here.</div>",
                unsafe_allow_html=True,
            )
        else:
            input_df = pd.DataFrame([{
                "neighbourhood_group": neighbourhood_group,
                "neighbourhood": neighbourhood,
                "latitude": latitude,
                "longitude": longitude,
                "price": price,
                "minimum_nights": minimum_nights,
                "number_of_reviews": number_of_reviews,
                "reviews_per_month": reviews_per_month,
                "calculated_host_listings_count": calculated_host_listings_count,
                "availability_365": availability_365,
            }])

            prediction = pipeline.predict(input_df)[0]
            proba = pipeline.predict_proba(input_df)[0]
            classes = pipeline.classes_
            style = ROOM_STYLE.get(prediction, {"color": "#0B0B0D", "line": ""})

            st.markdown(
                f"""
                <div class="result-badge" style="background:{style['color']};">
                    <div class="label">Predicted room type</div>
                    <div class="value">{prediction}</div>
                    <div class="line">🚇 Color-coded like the {style['line']} train</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            proba_df = pd.DataFrame({"Room type": classes, "Probability": proba}).sort_values(
                "Probability", ascending=False
            )
            st.bar_chart(proba_df.set_index("Room type"))

            with st.expander("Debug: inputs sent to the model"):
                st.dataframe(input_df, use_container_width=True)
                st.write("Probabilities:", {c: round(float(p), 4) for c, p in zip(classes, proba)})

st.markdown(
    f'<div style="text-align:center; color:#8A8A90; font-size:0.8rem; margin-top:1rem;">'
    "Random Forest classifier · scikit-learn pipeline</div>",
    unsafe_allow_html=True,
)