import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
from io import BytesIO

# ============================================================
# APP CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="AI Hijab & Indian Outfit Studio",
    page_icon="🧕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS — Premium Fashion Dark Theme
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Poppins:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; color: #e0e0e0; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif; letter-spacing: 0.5px; }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(212, 175, 55, 0.15);
        border-color: rgba(212, 175, 55, 0.3);
    }
    
    /* Gold Accent Cards */
    .gold-accent {
        border-left: 4px solid #d4af37;
        background: linear-gradient(90deg, rgba(212,175,55,0.1), transparent);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #c59d5f);
        color: #0f0c29;
        border: none;
        border-radius: 30px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(212,175,55,0.4);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #1a1a2e);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #e0e0e0 !important;
        font-size: 0.9rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.03);
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #888;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #d4af37, #c59d5f) !important;
        color: #0f0c29 !important;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-weight: 700; }
    [data-testid="stMetricDelta"] { color: #e0b0a0 !important; }
    
    /* Progress bars */
    .stProgress > div > div { 
        background: linear-gradient(90deg, #d4af37, #e0b0a0) !important; 
        border-radius: 10px;
    }
    
    /* File uploader */
    .stFileUploader { background: rgba(255,255,255,0.03); border-radius: 15px; padding: 1rem; }
    
    /* Dataframes */
    .stDataFrame { background: rgba(255,255,255,0.02) !important; }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
defaults = {
    'profile': {},
    'wardrobe': [],
    'favorites': [],
    'journal': [],
    'quiz_step': 0,
    'quiz_result': None,
    'calendar_events': {},
    'tryon_history': [],
    'packing_list': [],
    'admin_stats': {'users': 1247, 'outfits': 15432, 'photos': 8921}
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def save_image(uploaded_file):
    if uploaded_file is not None:
        return Image.open(BytesIO(uploaded_file.getvalue()))
    return None

def apply_hijab_overlay(image, color_hex, style="Turkish", intensity=0.35):
    """Simulate hijab overlay on uploaded photo using PIL"""
    img = image.convert("RGBA")
    w, h = img.size
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    # Parse hex to RGB
    color_hex = color_hex.lstrip('#')
    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    alpha = int(255 * intensity)
    
    y_end = int(h * 0.48)
    
    if style == "Turkish":
        draw.ellipse([(w*0.18, -h*0.15), (w*0.82, y_end)], fill=rgb+(alpha,))
        draw.rectangle([(w*0.25, y_end*0.6), (w*0.35, y_end*1.2)], fill=rgb+(alpha,))
    elif style == "Simple Wrap":
        draw.rounded_rectangle([(w*0.15, -10), (w*0.85, y_end)], radius=40, fill=rgb+(alpha-20,))
    elif style == "Layered":
        draw.pieslice([(w*0.08, -h*0.2), (w*0.92, y_end*1.3)], 0, 180, fill=rgb+(alpha,))
        draw.arc([(w*0.12, -h*0.1), (w*0.88, y_end*1.1)], 0, 180, fill=rgb+(alpha+40,), width=20)
    else:  # Side Drape
        draw.ellipse([(w*0.2, -h*0.1), (w*0.8, y_end)], fill=rgb+(alpha,))
        draw.rectangle([(w*0.65, y_end*0.3), (w*0.9, y_end*1.4)], fill=rgb+(alpha-30,))
    
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=12))
    result = Image.alpha_composite(img, overlay)
    return result.convert("RGB")

def get_ai_recommendation(profile, occasion, mood, weather, body_shape):
    """Rule-based recommendation engine"""
    base = {
        "outfit": "Classic Anarkali", "hijab": "Chiffon Drape", "color": "Midnight Blue",
        "jewelry": "Silver Earrings", "shoes": "Embroidered Juttis", "bag": "Clutch",
        "makeup": "Soft Smokey Eye", "fabric": "Georgette", "confidence": 92
    }
    
    # Mood logic
    mood_map = {
        "Happy": {"color": "Pastel Pink & Mint", "outfit": "Floral Printed Kurti + Palazzo", "makeup": "Peach Glow"},
        "Calm": {"color": "Sand & Ivory", "outfit": "Linen Abaya", "makeup": "Nude Brown"},
        "Confident": {"color": "Emerald & Black", "outfit": "Silk Kaftan", "makeup": "Bold Red Lip"},
        "Elegant": {"color": "Wine & Gold", "outfit": "Banarasi Saree", "makeup": "Gold Shimmer"},
        "Energetic": {"color": "Coral & Yellow", "outfit": "Co-ord Set", "makeup": "Orange Blush"}
    }
    if mood in mood_map:
        base.update(mood_map[mood])
    
    # Occasion logic
    occasion_map = {
        "Nikah": {"outfit": "Heavy Lehenga + Hijab", "jewelry": "Bridal Set + Maang Tikka", "shoes": "Golden Heels"},
        "Eid": {"outfit": "Chikankari Anarkali", "jewelry": "Jhumkas", "bag": "Potli"},
        "Office Wear": {"outfit": "Straight Kurti + Trousers", "jewelry": "Watch", "shoes": "Block Heels"},
        "College Wear": {"outfit": "Denim Kurti + Jeans", "hijab": "Jersey Wrap", "bag": "Backpack"},
        "Gym/Walking": {"outfit": "Modest Activewear", "hijab": "Sports Hijab", "shoes": "Sneakers"}
    }
    if occasion in occasion_map:
        base.update(occasion_map[occasion])
    
    # Weather logic
    weather_map = {
        "Sunny 40°C": {"fabric": "Cotton/Linen", "color": base["color"] + " (Breathable)", "shoes": "Kolhapuris"},
        "Rainy": {"fabric": "Quick-Dry Jersey", "color": "Dark " + base["color"], "shoes": "Waterproof Loafers"},
        "Winter 10°C": {"fabric": "Wool/Kashmir", "color": base["color"], "shoes": "Ankle Boots", "outfit": "Layered " + base["outfit"]}
    }
    if weather in weather_map:
        base.update(weather_map[weather])
    
    # Body shape logic
    body_map = {
        "Pear": {"outfit": "A-Line " + base["outfit"], "tip": "Adds volume to upper body"},
        "Apple": {"outfit": "Empire Waist " + base["outfit"], "tip": "Draws attention upward"},
        "Hourglass": {"outfit": "Fitted " + base["outfit"], "tip": "Accentuates waist"},
        "Rectangle": {"outfit": "Layered " + base["outfit"], "tip": "Creates curves"},
        "Inverted Triangle": {"outfit": "Flared " + base["outfit"], "tip": "Balances proportions"}
    }
    if body_shape in body_map:
        base["outfit"] = body_map[body_shape]["outfit"]
        base["body_tip"] = body_map[body_shape]["tip"]
    
    return base

def generate_caption(occasion, outfit, mood):
    templates = [
        f"✨ Embracing elegance in this {outfit} for {occasion}. Feeling absolutely {mood.lower()}! #ModestFashion #HijabStyle",
        f"🌸 {mood} vibes only! Styled my favorite {outfit} for {occasion}. #IndianFashion #HijabiOutfit",
        f"🧕 When tradition meets AI — this {outfit} was made for {occasion}! #{occasion.replace(' ', '')}Look"
    ]
    hashtags = "#ModestFashion #HijabStyle #IndianWear #OOTD #AIStylist #HijabFashion #ModestStreetStyle"
    return random.choice(templates) + "\n\n" + hashtags

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #d4af37; font-family: Playfair Display;">AI Style Studio</h2>
        <p style="color: #888; font-size: 0.8rem; margin-top: -10px;">Modest Fashion Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    nav = st.radio("Navigate", [
        "🏠 Home",
        "🧬 AI Profile & Style Quiz",
        "✨ Smart Recommender",
        "🌸 Indian Traditional",
        "🧕 Virtual Try-On",
        "🌦️ Weather Stylist",
        "🎨 Color & Face Analysis",
        "👗 Wardrobe & Calendar",
        "🎉 Festival Planner",
        "💎 Accessories & Makeup",
        "📊 Analytics Dashboard",
        "📔 Journal & Admin"
    ], label_visibility="collapsed")
    
    st.markdown("---")
    
    # Mini profile widget
    if st.session_state['profile']:
        st.markdown("### 👤 Style Snapshot")
        st.caption(f"Body: {st.session_state['profile'].get('body_shape', 'N/A')}")
        st.caption(f"Tone: {st.session_state['profile'].get('undertone', 'N/A')}")
        st.progress(78, text="Style Score")
    else:
        st.info("Complete your AI Profile to unlock recommendations!")
    
    st.markdown("---")
    st.caption("© 2026 AI Hijab Studio | TY Project")

# ============================================================
# PAGE ROUTING
# ============================================================

# ------------------- HOME -------------------
if nav == "🏠 Home":
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem;">
        <h1 style="font-size: 3.5rem; background: linear-gradient(90deg, #d4af37, #e0b0a0, #d4af37); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   animation: shine 3s infinite;">
            AI Hijab & Indian Outfit Studio
        </h1>
        <p style="font-size: 1.15rem; color: #a0a0a0; max-width: 650px; margin: 1rem auto 2rem;">
            The world's first comprehensive AI stylist for modest fashion. 
            From virtual hijab try-ons to Indian ethnic wear recommendations powered by weather, 
            skin tone, and body shape analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero metrics
    m1, m2, m3, m4 = st.columns(4)
    metrics = [("🧕", "Try-Ons", "15K+"), ("🌦️", "Weather AI", "Live"), ("📊", "Outfits", "60+"), ("🌍", "Regions", "12")]
    for col, (icon, label, val) in zip([m1,m2,m3,m4], metrics):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 2rem;">{icon}</div>
                <h3 style="color: #d4af37; margin: 0;">{val}</h3>
                <p style="color: #888; font-size: 0.85rem;">{label}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feature Grid
    st.subheader("✨ Explore Modules")
    feats = [
        ("🧬 AI Profile", "Skin tone, body shape & style quiz"),
        ("✨ Recommender", "Occasion + mood + weather engine"),
        ("🧕 Virtual Try-On", "Upload selfie & preview hijabs"),
        ("🌸 Indian Wear", "Saree, Lehenga, Anarkali guides"),
        ("👗 Wardrobe", "Digital closet & capsule generator"),
        ("📊 Analytics", "Wardrobe insights & trend dashboards")
    ]
    cols = st.columns(3)
    for i, (title, desc) in enumerate(feats):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="height: 140px;">
                <h4 style="color: #e0b0a0;">{title}</h4>
                <p style="color: #aaa; font-size: 0.9rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ------------------- AI PROFILE -------------------
elif nav == "🧬 AI Profile & Style Quiz":
    st.title("🧬 AI Personal Profile & Style Setup")
    
    tabs = st.tabs(["📝 Profile Setup", "🎮 AI Style Quiz", "📋 My Analysis"])
    
    with tabs[0]:
        with st.form("profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Physical Attributes")
                age = st.slider("Age", 15, 70, 21)
                height = st.select_slider("Height", ["4'8\"", "5'0\"", "5'2\"", "5'4\"", "5'6\"", "5'8\"", "5'10\"", "6'0\""])
                weight = st.number_input("Weight (kg) [Optional]", 30, 120, 55)
                body = st.selectbox("Body Shape", ["Pear", "Apple", "Hourglass", "Rectangle", "Inverted Triangle"])
                face = st.selectbox("Face Shape", ["Oval", "Round", "Square", "Diamond", "Heart", "Long"])
                
                st.subheader("Skin Analysis")
                skin = st.radio("Skin Tone", ["Very Fair", "Fair", "Medium", "Olive", "Brown", "Dark"], horizontal=True)
                undertone = st.radio("Undertone", ["Warm", "Cool", "Neutral", "Olive"], horizontal=True)
            
            with c2:
                st.subheader("Style Preferences")
                styles = st.multiselect("Style Aesthetic", 
                    ["Minimal", "Luxury", "Casual", "Festive", "Streetwear", "Traditional", "Indo-Western", "Soft Girl", "Korean Modest"])
                colors = st.multiselect("Favorite Colors", 
                    ["Black", "White", "Beige", "Pastel Pink", "Dusty Rose", "Emerald", "Navy", "Maroon", "Mustard", "Gold"])
                fabrics = st.multiselect("Preferred Fabrics", 
                    ["Cotton", "Linen", "Silk", "Chiffon", "Jersey", "Velvet", "Banarasi", "Georgette", "Organza", "Modal"])
                budget = st.select_slider("Monthly Budget (₹)", 
                    ["<1000", "1000-3000", "3000-5000", "5000-10000", "10000-20000", "20000+"])
                hijab_styles = st.multiselect("Preferred Hijab Styles", 
                    ["Turkish", "Simple Wrap", "Layered", "Side Drape", "Bridal", "Sports", "Jersey"])
            
            if st.form_submit_button("💾 Save My AI Profile", use_container_width=True):
                st.session_state['profile'] = {
                    'age': age, 'height': height, 'weight': weight,
                    'body_shape': body, 'face_shape': face,
                    'skin_tone': skin, 'undertone': undertone,
                    'styles': styles, 'colors': colors, 'fabrics': fabrics,
                    'budget': budget, 'hijab_styles': hijab_styles
                }
                st.success("Profile saved! AI model is training on your preferences...")
                st.balloons()
    
    with tabs[1]:
        st.subheader("🎮 Discover Your Style Archetype")
        
        if st.session_state['quiz_step'] == 0:
            st.markdown("### Question 1 of 4")
            q1 = st.radio("Pick your ideal weekend activity:", 
                ["Museum & Coffee", "Wedding Shopping", "Gym & Hiking", "Netflix at Home"])
            if st.button("Next ➡️"):
                st.session_state['quiz_q1'] = q1
                st.session_state['quiz_step'] = 1
                st.rerun()
        
        elif st.session_state['quiz_step'] == 1:
            st.markdown("### Question 2 of 4")
            q2 = st.radio("Choose a color palette:", 
                ["Neutrals & Beige", "Bold Reds & Golds", "Pastels & Whites", "Blacks & Metallics"])
            if st.button("Next ➡️"):
                st.session_state['quiz_q2'] = q2
                st.session_state['quiz_step'] = 2
                st.rerun()
        
        elif st.session_state['quiz_step'] == 2:
            st.markdown("### Question 3 of 4")
            q3 = st.radio("Your go-to accessory:", 
                ["Minimal Watch", "Statement Earrings", "Sneakers", "Designer Bag"])
            if st.button("Next ➡️"):
                st.session_state['quiz_q3'] = q3
                st.session_state['quiz_step'] = 3
                st.rerun()
        
        elif st.session_state['quiz_step'] == 3:
            st.markdown("### Question 4 of 4")
            q4 = st.radio("Dream vacation wardrobe:", 
                ["Linen Abayas", "Heavy Lehengas", "Modest Activewear", "Basic Kurtis"])
            if st.button("Reveal My Style ✨"):
                # Simple scoring
                archetypes = {
                    "Elegant Traditional": "You gravitate toward timeless pieces, rich fabrics, and classic silhouettes.",
                    "Minimalist Modest": "Clean lines, neutral palettes, and investment pieces define your wardrobe.",
                    "Festive Maximalist": "You love color, embroidery, and making an entrance at every celebration.",
                    "Casual Comfort": "Practical, breathable, and effortlessly stylish — you prioritize comfort."
                }
                result = random.choice(list(archetypes.keys()))
                st.session_state['quiz_result'] = result
                st.session_state['quiz_desc'] = archetypes[result]
                st.session_state['quiz_step'] = 4
                st.rerun()
        
        else:
            st.balloons()
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; border: 2px solid #d4af37;">
                <h2 style="color: #d4af37;">Your Archetype: {st.session_state['quiz_result']}</h2>
                <p style="font-size: 1.1rem;">{st.session_state['quiz_desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Retake Quiz"):
                st.session_state['quiz_step'] = 0
                st.rerun()
    
    with tabs[2]:
        if st.session_state['profile']:
            p = st.session_state['profile']
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Face Shape", p['face_shape'])
            c2.metric("Body Type", p['body_shape'])
            c3.metric("Undertone", p['undertone'])
            c4.metric("Budget", p['budget'])
            
            st.markdown("---")
            st.subheader("🎯 AI Personalized Insights")
            
            insights = []
            if p['undertone'] == "Warm":
                insights.append("💛 **Gold jewelry** will complement your skin beautifully. Opt for earthy hijab tones like mustard, rust, and olive.")
            elif p['undertone'] == "Cool":
                insights.append("🤍 **Silver/platinum jewelry** suits you best. Try jewel-toned hijabs: emerald, sapphire, and ruby.")
            
            if p['body_shape'] == "Pear":
                insights.append("👗 **A-line Kurtis** and **empire waist Anarkalis** balance your proportions. Avoid clingy fabrics on the lower half.")
            elif p['body_shape'] == "Apple":
                insights.append("🧥 **Straight-cut Abayas** and **V-neckline Kurtis** elongate your torso. Darker colors on top are flattering.")
            
            if "Festive" in p['styles']:
                insights.append("✨ You have a celebratory spirit! Banarasi dupattas and organza hijabs will elevate your wardrobe.")
            
            for insight in insights:
                st.markdown(f"""
                <div class="glass-card gold-accent">
                    <p style="margin: 0;">{insight}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Complete the Profile Setup to see your AI analysis.")

# ------------------- RECOMMENDER -------------------
elif nav == "✨ Smart Recommender":
    st.title("✨ AI Outfit Recommendation Engine")
    
    if not st.session_state['profile']:
        st.warning("⚠️ Please complete your AI Profile first for personalized results!")
    else:
        # Filters
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                occasion = st.selectbox("Occasion", 
                    ["Daily Wear", "College Wear", "Office Wear", "Casual Wear", "Travel Wear",
                     "Gym/Walking", "Eid", "Wedding Guest", "Reception", "Mehendi", "Nikah", "Birthday Party", "Friday Prayer"])
            with c2:
                mood = st.selectbox("Mood", ["Happy", "Calm", "Confident", "Elegant", "Energetic", "Romantic", "Spiritual"])
            with c3:
                weather = st.selectbox("Weather", ["Sunny 40°C", "Rainy", "Winter 10°C", "Humid", "Windy", "Pleasant 25°C"])
            with c4:
                hijab_pref = st.selectbox("Hijab Style", ["Turkish", "Layered", "Simple Wrap", "Side Drape", "Bridal", "Sports"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Prayer-friendly toggle
        prayer_friendly = st.toggle("🕌 Prayer-Friendly Outfit (Wudu-friendly sleeves, breathable fabric)", value=False)
        
        if st.button("🚀 Generate AI Outfit", use_container_width=True):
            with st.spinner("Analyzing profile + weather + occasion + mood..."):
                import time
                time.sleep(1.2)
                
                rec = get_ai_recommendation(st.session_state['profile'], occasion, mood, weather, 
                                          st.session_state['profile'].get('body_shape', 'Rectangle'))
                
                if prayer_friendly:
                    rec['outfit'] = "Prayer-Friendly " + rec['outfit']
                    rec['fabric'] = "Breathable " + rec['fabric']
                    rec['sleeves'] = "Elastic Wudu-Friendly Sleeves"
                
                st.markdown("---")
                st.subheader("🎯 Your AI-Curated Look")
                
                left, right = st.columns([1, 2])
                
                with left:
                    # Visual card
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a2e, #0f0c29); 
                                border-radius: 20px; padding: 2rem; text-align: center;
                                border: 2px solid #d4af37; box-shadow: 0 0 30px rgba(212,175,55,0.2);">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">👗</div>
                        <h3 style="color: #e0b0a0; margin-bottom: 0.5rem;">{rec['outfit']}</h3>
                        <div style="background: rgba(212,175,55,0.15); border-radius: 20px; padding: 0.5rem 1rem; display: inline-block;">
                            <span style="color: #d4af37; font-weight: 600;">{rec['color']}</span>
                        </div>
                        <div style="margin-top: 1.5rem;">
                            <span style="font-size: 1.5rem;">🧕</span>
                            <p style="color: #ccc; margin: 0;">{rec['hijab']}</p>
                        </div>
                        <div style="margin-top: 1rem; font-size: 0.85rem; color: #888;">
                            Fabric: {rec['fabric']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("❤️ Save to Favorites"):
                        st.session_state['favorites'].append({
                            'outfit': rec['outfit'], 'color': rec['color'], 'occasion': occasion,
                            'date': datetime.datetime.now(), 'mood': mood
                        })
                        st.toast("Saved to favorites!")
                
                with right:
                    detail_tabs = st.tabs(["Complete Look", "Accessories", "Makeup & Hair", "AI Scores", "Shop"])
                    
                    with detail_tabs[0]:
                        items = [
                            ("👗 Primary Outfit", rec['outfit']),
                            ("🧕 Hijab Style", rec['hijab']),
                            ("👠 Footwear", rec['shoes']),
                            ("🎒 Bag", rec['bag']),
                            ("🧵 Fabric", rec['fabric'])
                        ]
                        if prayer_friendly:
                            items.append(("🕌 Special Feature", rec.get('sleeves', 'Full Coverage')))
                        for icon_item, val in items:
                            st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <span style="color: #888;">{icon_item}</span>
                                <span style="color: #e0e0e0; font-weight: 500;">{val}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        if 'body_tip' in rec:
                            st.caption(f"💡 Body Shape Tip: {rec['body_tip']}")
                    
                    with detail_tabs[1]:
                        acc = {
                            "💎 Jewelry": rec['jewelry'],
                            "📿 Additional": "Layered Necklace" if "Wedding" in occasion else "Minimal Pendant",
                            "🧷 Hijab Pins": "Crystal Pins" if "Elegant" in mood else "Basic Pins",
                            "⌚ Watch": "Rose Gold Minimalist"
                        }
                        for k, v in acc.items():
                            st.write(f"**{k}:** {v}")
                    
                    with detail_tabs[2]:
                        makeup = {
                            "💄 Lipstick": rec['makeup'],
                            "👁️ Eyeshadow": "Gold Shimmer" if "Wedding" in occasion else "Neutral Brown",
                            "🌸 Blush": "Soft Peach",
                            "💅 Nail Color": rec['color'].split()[0]
                        }
                        for k, v in makeup.items():
                            st.write(f"**{k}:** {v}")
                    
                    with detail_tabs[3]:
                        sc1, sc2, sc3 = st.columns(3)
                        style_score = random.randint(85, 98)
                        modesty_score = random.randint(90, 100)
                        weather_score = random.randint(80, 95)
                        sc1.metric("Style Score", f"{style_score}/100")
                        sc2.metric("Modesty Score", f"{modesty_score}/100")
                        sc3.metric("Weather Match", f"{weather_score}/100")
                        
                        conf = random.randint(82, 96)
                        st.progress(conf/100, text=f"AI Confidence: {conf}%")
                        
                        # Confidence & Comfort Prediction
                        st.caption("🧠 Predicted Metrics")
                        st.write(f"• **Confidence Boost:** +{random.randint(15,35)}%")
                        st.write(f"• **Comfort Level:** {random.choice(['All Day Wear', 'Luxury Feel', 'Cloud Comfort'])}")
                        st.write(f"• **Rewear Probability:** {random.randint(70,95)}%")
                    
                    with detail_tabs[4]:
                        st.write("Similar items under your budget:")
                        st.button(f"🔍 Search {rec['outfit']} on Myntra", use_container_width=True)
                        st.button(f"🔍 Search {rec['fabric']} Fabric", use_container_width=True)
                        st.button("🔔 Set Price Alert", use_container_width=True)

# ------------------- INDIAN TRADITIONAL -------------------
                        # INDIAN TRADITIONAL CONTINUED
                        st.title("🌸 Indian Traditional Outfit Studio")
                        
                        st.markdown("""
                        <div style="text-align: center; margin-bottom: 2rem;">
                            <p style="color: #aaa; font-size: 1.05rem;">
                                Explore regional crafts, silhouettes, and modest styling for every celebration.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Category Explorer
                        cat_cols = st.columns(4)
                        categories = [
                            ("Kurti + Palazzo", "Daily elegance", "🥻"),
                            ("Anarkali", "Regal flow", "👗"),
                            ("Sharara/Gharara", "Festive flare", "💃"),
                            ("Saree + Hijab", "Timeless drape", "🧣"),
                            ("Lehenga + Hijab", "Bridal dreams", "👑"),
                            ("Abaya + Embroidery", "Modest luxury", "🪡"),
                            ("Kaftan", "Resort chic", "🏖️"),
                            ("Co-ord Set", "Modern match", "🎯")
                        ]
                        
                        selected_cat = None
                        for idx, (name, desc, icon) in enumerate(categories):
                            with cat_cols[idx % 4]:
                                if st.button(f"{icon} {name}", key=f"cat_{idx}", use_container_width=True):
                                    selected_cat = name
                                st.caption(f"<p style='text-align: center; color: #888;'>{desc}</p>", unsafe_allow_html=True)
                        
                        if selected_cat:
                            st.markdown("---")
                            st.subheader(f"✨ {selected_cat} Styling Guide")
                            
                            guide_data = {
                                "Kurti + Palazzo": {
                                    "best_for": "College, Office, Daily Wear",
                                    "hijab_style": "Simple Wrap or Jersey",
                                    "fabric": "Cotton, Rayon, Linen",
                                    "tips": "Choose A-line kurtis for pear shapes. Pair with straight palazzos to elongate legs.",
                                    "colors": "Pastel Pink, Mint, Ivory, Dusty Rose"
                                },
                                "Anarkali": {
                                    "best_for": "Eid, Family Functions, Reception",
                                    "hijab_style": "Layered or Turkish",
                                    "fabric": "Georgette, Silk, Net",
                                    "tips": "Floor-length Anarkalis suit all body types. Add a belt for hourglass emphasis.",
                                    "colors": "Wine, Emerald, Midnight Blue, Gold"
                                },
                                "Sharara/Gharara": {
                                    "best_for": "Mehendi, Sangeet, Nikah",
                                    "hijab_style": "Bridal Drape with Dupatta",
                                    "fabric": "Silk, Brocade, Velvet",
                                    "tips": "Keep hijab volume balanced with flared bottoms. Heavy earrings complete the look.",
                                    "colors": "Rani Pink, Mustard, Teal, Maroon"
                                },
                                "Saree + Hijab": {
                                    "best_for": "Wedding Guest, Reception, Ethnic Day",
                                    "hijab_style": "Turkish with Pleated Pallu",
                                    "fabric": "Banarasi, Kanjeevaram, Chiffon",
                                    "tips": "Pin hijab under the blouse line. Use a matching inner cap. Drape pallu over hijab for seamless look.",
                                    "colors": "Classic Red, Peacock Blue, Forest Green"
                                },
                                "Lehenga + Hijab": {
                                    "best_for": "Bridal, Reception, Photoshoot",
                                    "hijab_style": "Bridal Turban or Layered Net",
                                    "fabric": "Velvet, Silk, Organza",
                                    "tips": "Opt for full-sleeve blouses. Hijab can be draped like a dupatta over one shoulder.",
                                    "colors": "Bridal Red, Champagne, Sage Green"
                                },
                                "Abaya + Embroidery": {
                                    "best_for": "Friday Prayer, Ramadan, Travel",
                                    "hijab_style": "Matching Closed Abaya Hijab",
                                    "fabric": "Nida, Kashibo, Crepe",
                                    "tips": "Indian embroidery (Chikankari, Zardozi) on abayas creates Indo-Arabic fusion.",
                                    "colors": "Black with Gold, Navy with Silver, Beige"
                                },
                                "Kaftan": {
                                    "best_for": "Resort, Travel, Home Wear",
                                    "hijab_style": "Loose Jersey Wrap",
                                    "fabric": "Cotton, Satin, Chiffon",
                                    "tips": "Belted kaftans define waist. Perfect for rectangle body shapes.",
                                    "colors": "White, Coral, Turquoise, Sand"
                                },
                                "Co-ord Set": {
                                    "best_for": "Casual Outings, College, Travel",
                                    "hijab_style": "Sports or Simple Wrap",
                                    "fabric": "Cotton Blend, Linen, Knit",
                                    "tips": "Matching top-bottom sets create vertical lines. Great for petite frames.",
                                    "colors": "Sage, Lavender, Rust, Charcoal"
                                }
                            }
                            
                            info = guide_data.get(selected_cat, {})
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.markdown(f"""
                                <div class="glass-card gold-accent">
                                    <h4 style="color: #d4af37;">{selected_cat}</h4>
                                    <p><strong>Best For:</strong> {info.get('best_for', '')}</p>
                                    <p><strong>Recommended Hijab:</strong> {info.get('hijab_style', '')}</p>
                                    <p><strong>Fabric:</strong> {info.get('fabric', '')}</p>
                                    <p><strong>Colors:</strong> {info.get('colors', '')}</p>
                                    <div style="background: rgba(212,175,55,0.1); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                                        <p style="margin: 0; color: #e0b0a0;">💡 <strong>Stylist Tip:</strong> {info.get('tips', '')}</p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            with c2:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #1a1a2e, #302b63); 
                                            border-radius: 20px; height: 250px; display: flex; 
                                            align-items: center; justify-content: center;
                                            border: 1px solid rgba(212,175,55,0.3);">
                                    <div style="text-align: center;">
                                        <div style="font-size: 4rem;">🧕</div>
                                        <p style="color: #888;">Visual Preview</p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.button("🧕 Try This Look Virtually", use_container_width=True)
                        
                        # Regional Explorer
                        st.markdown("---")
                        st.subheader("🗺️ Regional Indian Fashion Explorer")
                        
                        regions = {
                            "Lucknow": ["Chikankari Kurta", "Pastel Shades", "Cotton/Viscose"],
                            "Hyderabad": ["Pearl Work Lehenga", "Royal Colors", "Silk"],
                            "Kashmir": ["Pashmina Shawl Hijab", "Earth Tones", "Wool"],
                            "Rajasthan": ["Bandhani Print", "Vibrant Red/Yellow", "Cotton"],
                            "Bengal": "Kantha Stitch Saree",
                            "Gujarat": "Patola Dupatta",
                            "Punjab": "Phulkari Embroidery",
                            "Kerala": "Kasavu Mundu",
                            "Pakistani": "Long Shirt + Gharara",
                            "Turkish": "Hijab + Long Coat",
                            "Indonesian": "Lace Kebaya",
                            "Arabic": "Black Abaya + Gold"
                        }
                        
                        reg_cols = st.columns(3)
                        for idx, (region, specialty) in enumerate(list(regions.items())[:6]):
                            with reg_cols[idx % 3]:
                                st.markdown(f"""
                                <div class="glass-card" style="text-align: center; padding: 1rem;">
                                    <h4 style="color: #e0b0a0;">{region}</h4>
                                    <p style="color: #aaa; font-size: 0.85rem;">{specialty if isinstance(specialty, str) else specialty[0]}</p>
                                </div>
                                """, unsafe_allow_html=True)

# ------------------- VIRTUAL TRY-ON -------------------
elif nav == "🧕 Virtual Try-On":
    st.title("🧕 AI Virtual Try-On Studio")
    
    tabs = st.tabs(["Hijab Try-On", "Outfit Try-On", "Dupatta + Hijab Guide"])
    
    with tabs[0]:
        st.markdown("""
        <div class="glass-card">
            <p>Upload your selfie and instantly try 30+ hijab colors, textures, and wrapping styles using our AI overlay engine.</p>
        </div>
        """, unsafe_allow_html=True)
        
        up1, up2 = st.columns([1, 2])
        with up1:
            selfie = st.file_uploader("📤 Upload Selfie", type=['jpg', 'jpeg', 'png'], key="hijab_selfie")
            if selfie:
                img = save_image(selfie)
                st.image(img, use_container_width=True, caption="Original")
        
        with up2:
            if selfie:
                st.subheader("🎨 Customize Your Hijab")
                hijab_color = st.color_picker("Hijab Color", "#D4AF37")
                texture = st.select_slider("Texture", ["Matte Cotton", "Satin Sheen", "Chiffon Flow", "Jersey Soft", "Velvet Rich"])
                wrap_style = st.selectbox("Wrapping Style", ["Turkish", "Simple Wrap", "Layered", "Side Drape", "Bridal"])
                opacity = st.slider("Overlay Intensity", 0.1, 0.8, 0.35, 0.05)
                
                if st.button("✨ Generate AI Try-On", use_container_width=True):
                    with st.spinner("AI is rendering your hijab overlay..."):
                        result = apply_hijab_overlay(img, hijab_color, wrap_style, opacity)
                        st.session_state['tryon_history'].append({
                            'image': result, 'style': wrap_style, 'color': hijab_color, 'time': datetime.datetime.now()
                        })
                    
                    st.success("Try-On Generated!")
                    st.image(result, use_container_width=True, caption=f"{wrap_style} Style | {texture}")
                    
                    # Comparison
                    comp = st.columns(2)
                    with comp[0]:
                        st.image(img, use_container_width=True, caption="Before")
                    with comp[1]:
                        st.image(result, use_container_width=True, caption="After")
                    
                    st.download_button("💾 Download Look", data=BytesIO(), file_name="my_hijab_look.png", mime="image/png")
            else:
                st.info("Upload a selfie to begin the virtual try-on experience.")
    
    with tabs[1]:
        st.subheader("👗 Traditional Outfit Overlay")
        st.markdown("""
        <div class="glass-card">
            <p>Visualize sarees, lehengas, and kurtis on your photo. (Simulated with color/fabric overlay)</p>
        </div>
        """, unsafe_allow_html=True)
        
        outfit_selfie = st.file_uploader("Upload Full Body Photo", type=['jpg', 'jpeg', 'png'], key="outfit_selfie")
        if outfit_selfie:
            o_img = save_image(outfit_selfie)
            o1, o2 = st.columns(2)
            with o1:
                outfit_type = st.selectbox("Outfit to Try", ["Saree Drape", "Anarkali", "Lehenga", "Kurti", "Sharara", "Abaya"])
                outfit_color = st.color_picker("Outfit Color", "#800020")
                if st.button("Generate Outfit Overlay"):
                    # Simulate outfit overlay with color tint
                    tinted = o_img.convert("RGBA")
                    overlay = Image.new('RGBA', tinted.size, outfit_color + (60,))
                    blended = Image.alpha_composite(tinted, overlay).convert("RGB")
                    st.image(blended, caption=f"AI Preview: {outfit_type}")
            with o2:
                st.image(o_img, caption="Your Photo")
    
    with tabs[2]:
        st.subheader("🧣 Dupatta + Hijab Styling Tutorials")
        tutorials = {
            "One-Side Drape": "Drape dupatta over one shoulder, secure with hijab pin at shoulder. Let it flow behind.",
            "Turkish Style": "Wrap hijab fully, then layer dupatta over head like a crown. Secure with decorative pins.",
            "Layered Style": "Wear inner cap, jersey hijab, then sheer dupatta on top for dimension.",
            "Bridal Style": "Use heavily embroidered dupatta as veil. Pin to hijab cap. Add fresh flowers or tiara.",
            "Casual Style": "Simply throw dupatta over one shoulder, no pinning. Pair with loose jersey hijab."
        }
        for name, desc in tutorials.items():
            with st.expander(name):
                st.write(desc)
                st.button(f"🎬 Watch {name} Video", key=f"vid_{name}")

# ------------------- WEATHER STYLIST -------------------
elif nav == "🌦️ Weather Stylist":
    st.title("🌦️ Weather-Based AI Styling")
    
    # Simulated weather widget
    w1, w2, w3, w4 = st.columns(4)
    weather_options = ["Sunny 40°C", "Rainy", "Winter 10°C", "Humid 35°C", "Windy", "Pleasant 25°C"]
    current_weather = w1.selectbox("Current Weather", weather_options)
    location = w2.text_input("Location", "Mumbai, India")
    uv_index = w3.slider("UV Index", 0, 11, 7)
    humidity = w4.slider("Humidity %", 20, 100, 65)
    
    st.markdown("---")
    
    # Weather-based recommendation card
    weather_recs = {
        "Sunny 40°C": {
            "icon": "☀️", "fabric": "Cotton, Linen, Modal", "colors": "White, Beige, Pastel Blue, Mint",
            "hijab": "Breathable Cotton Jersey", "footwear": "Kolhapuris, Open Sandals",
            "layering": "None - keep minimal", "accessories": "Sunglasses, Cap under hijab"
        },
        "Rainy": {
            "icon": "🌧️", "fabric": "Quick-dry Jersey, Synthetic Blends", "colors": "Navy, Black, Dark Green, Rust",
            "hijab": "Synthetic Chiffon (dries fast)", "footwear": "Waterproof Loafers, Rubber Sole Shoes",
            "layering": "Light waterproof trench", "accessories": "Compact umbrella, Waterproof bag"
        },
        "Winter 10°C": {
            "icon": "❄️", "fabric": "Wool, Pashmina, Velvet, Knit", "colors": "Burgundy, Camel, Forest Green, Charcoal",
            "hijab": "Wool Hijab or Pashmina Shawl", "footwear": "Ankle Boots, Closed Shoes",
            "layering": "Thermal inner + Cardigan + Coat", "accessories": "Gloves, Woolen socks, Ear warmers"
        },
        "Humid 35°C": {
            "icon": "💧", "fabric": "Cotton, Linen, Chambray", "colors": "Light Grey, Lavender, Sky Blue",
            "hijab": "Super-light Chiffon or Voile", "footwear": "Breathable Juttis",
            "layering": "Avoid layers", "accessories": "Face mist, Hair ties"
        },
        "Windy": {
            "icon": "💨", "fabric": "Heavier Cotton, Jersey", "colors": "Earthy tones",
            "hijab": "Secure Jersey Wrap with pins", "footwear": "Closed shoes",
            "layering": "Light jacket", "accessories": "Extra safety pins"
        },
        "Pleasant 25°C": {
            "icon": "🌤️", "fabric": "All fabrics suitable", "colors": "Any seasonal palette",
            "hijab": "Any style works", "footwear": "Any",
            "layering": "Optional light shrug", "accessories": "Statement jewelry"
        }
    }
    
    rec = weather_recs.get(current_weather, weather_recs["Pleasant 25°C"])
    
    st.markdown(f"""
    <div class="glass-card" style="border: 2px solid rgba(212,175,55,0.3);">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <span style="font-size: 3rem;">{rec['icon']}</span>
            <div>
                <h3 style="margin: 0; color: #d4af37;">AI Weather Recommendation</h3>
                <p style="margin: 0; color: #888;">{location} • {current_weather}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    wc1, wc2 = st.columns(2)
    with wc1:
        st.metric("Recommended Fabric", rec['fabric'])
        st.metric("Best Colors", rec['colors'])
        st.metric("Hijab Type", rec['hijab'])
    with wc2:
        st.metric("Footwear", rec['footwear'])
        st.metric("Layering", rec['layering'])
        st.metric("Accessories", rec['accessories'])
    
    # Dynamic outfit suggestion based on weather
    st.markdown("---")
    st.subheader("🎯 Auto-Generated Weather Outfit")
    
    if current_weather == "Sunny 40°C":
        st.markdown("""
        <div class="glass-card">
            <h4>☀️ Heatwave Modest Look</h4>
            <p><strong>Outfit:</strong> White cotton palazzo suit with short sleeves (wear arm coverage if preferred)</p>
            <p><strong>Hijab:</strong> Beige cotton jersey wrap — breathable and sweat-wicking</p>
            <p><strong>Why:</strong> Light colors reflect heat. Cotton absorbs sweat. Loose fit allows air circulation.</p>
        </div>
        """, unsafe_allow_html=True)
    elif current_weather == "Winter 10°C":
        st.markdown("""
        <div class="glass-card">
            <h4>❄️ Cozy Modest Look</h4>
            <p><strong>Outfit:</strong> Wool Anarkali + Thermal leggings + Long coat</p>
            <p><strong>Hijab:</strong> Kashmiri Pashmina shawl wrapped as hijab</p>
            <p><strong>Why:</strong> Layering traps heat. Pashmina provides insulation without bulk.</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------- COLOR & FACE ANALYSIS -------------------
elif nav == "🎨 Color & Face Analysis":
    st.title("🎨 Skin Tone & Face Shape AI")
    
    c_tabs = st.tabs(["Skin Tone Analysis", "Face Shape Detection", "Body Shape Stylist"])
    
    with c_tabs[0]:
        st.subheader("AI Skin Tone & Undertone Detection")
        
        upload_skin = st.file_uploader("Upload wrist/face photo for analysis", type=['jpg', 'png'])
        if upload_skin:
            simg = save_image(upload_skin)
            st.image(simg, width=300)
            
            if st.button("🔬 Analyze Skin Tone"):
                with st.spinner("Running K-Means color clustering..."):
                    import time
                    time.sleep(1.5)
                    
                    # Simulated analysis
                    undertone = random.choice(["Warm", "Cool", "Neutral", "Olive"])
                    skin_depth = random.choice(["Fair", "Medium", "Tan", "Deep"])
                    
                    st.success(f"Detected: **{skin_depth}** with **{undertone}** undertone")
                    
                    if undertone == "Warm":
                        st.markdown("""
                        <div class="glass-card gold-accent">
                            <h4 style="color: #d4af37;">Warm Undertone Palette</h4>
                            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 1rem 0;">
                                <div style="width: 60px; height: 60px; background: #D4AF37; border-radius: 50%;" title="Gold"></div>
                                <div style="width: 60px; height: 60px; background: #FF8C00; border-radius: 50%;" title="Orange"></div>
                                <div style="width: 60px; height: 60px; background: #8B4513; border-radius: 50%;" title="Brown"></div>
                                <div style="width: 60px; height: 60px; background: #556B2F; border-radius: 50%;" title="Olive"></div>
                                <div style="width: 60px; height: 60px; background: #DC143C; border-radius: 50%;" title="Crimson"></div>
                            </div>
                            <p><strong>Best Hijab Colors:</strong> Mustard, Rust, Olive, Coral, Peach, Gold, Copper</p>
                            <p><strong>Jewelry:</strong> Gold, Rose Gold, Copper, Bronze</p>
                            <p><strong>Lipstick:</strong> Warm reds, Orange-red, Coral, Peachy nude</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif undertone == "Cool":
                        st.markdown("""
                        <div class="glass-card gold-accent">
                            <h4 style="color: #d4af37;">Cool Undertone Palette</h4>
                            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 1rem 0;">
                                <div style="width: 60px; height: 60px; background: #C0C0C0; border-radius: 50%;"></div>
                                <div style="width: 60px; height: 60px; background: #4169E1; border-radius: 50%;"></div>
                                <div style="width: 60px; height: 60px; background: #800080; border-radius: 50%;"></div>
                                <div style="width: 60px; height: 60px; background: #FF69B4; border-radius: 50%;"></div>
                                <div style="width: 60px; height: 60px; background: #2E8B57; border-radius: 50%;"></div>
                            </div>
                            <p><strong>Best Hijab Colors:</strong> Silver, Sapphire, Emerald, Lavender, Rose, Berry</p>
                            <p><strong>Jewelry:</strong> Silver, Platinum, White Gold</p>
                            <p><strong>Lipstick:</strong> Berry, Plum, Blue-red, Mauve</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    with c_tabs[1]:
        st.subheader("Face Shape Detection")
        face_shape = st.selectbox("Select your face shape (or upload photo for AI detection)", 
                                   ["Oval", "Round", "Square", "Diamond", "Heart", "Long"])
        
        face_tips = {
            "Oval": {"hijab": "Any style works! Turkish wrap adds volume.", "volume": "Medium", "pins": "Side pins"},
            "Round": {"hijab": "Height on top, elongate with side drapes", "volume": "High crown", "pins": "Forehead center"},
            "Square": {"hijab": "Soften jaw with loose sides", "volume": "Low side volume", "pins": "Under chin"},
            "Diamond": {"hijab": "Balance narrow chin with forehead volume", "volume": "Top heavy", "pins": "Temple pins"},
            "Heart": {"hijab": "Minimize forehead, add volume at jaw", "volume": "Low volume", "pins": "Side jaw pins"},
            "Long": {"hijab": "Avoid height, wrap close to head", "volume": "Flat top", "pins": "Even distribution"}
        }
        
        tip = face_tips[face_shape]
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color: #e0b0a0;">{face_shape} Face Analysis</h4>
            <p><strong>Recommended Hijab Style:</strong> {tip['hijab']}</p>
            <p><strong>Volume Strategy:</strong> {tip['volume']}</p>
            <p><strong>Pin Placement:</strong> {tip['pins']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Visual guide
        st.caption("Visual Pin Placement Guide")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0.5], y=[0.8], mode='markers', marker=dict(size=30, color='#d4af37'), name="Forehead"))
        fig.add_trace(go.Scatter(x=[0.2, 0.8], y=[0.5, 0.5], mode='markers', marker=dict(size=20, color='#e0b0a0'), name="Sides"))
        fig.add_trace(go.Scatter(x=[0.5], y=[0.2], mode='markers', marker=dict(size=25, color='#888'), name="Chin"))
        fig.update_layout(
            title="Hijab Pin Placement Map",
            xaxis=dict(range=[0, 1], showgrid=False, zeroline=False),
            yaxis=dict(range=[0, 1], showgrid=False, zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'), height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with c_tabs[2]:
        st.subheader("Body Shape Outfit Stylist")
        body = st.selectbox("Your Body Shape", ["Pear", "Apple", "Hourglass", "Rectangle", "Inverted Triangle"])
        
        body_guide = {
            "Pear": {
                "kurti": "A-Line / Anarkali (adds upper volume)",
                "pants": "Straight Palazzo (balances hips)",
                "saree": "Seedha Pallu (draws eye up)",
                "avoid": "Bodycon bottoms, heavy lower embroidery",
                "abaya": "Flared cut with shoulder details"
            },
            "Apple": {
                "kurti": "Empire waist, A-line (skips midsection)",
                "pants": "Straight cut, dark colors",
                "saree": "Ulta Pallu, light fabrics",
                "avoid": "Clingy fabrics around waist, heavy belts",
                "abaya": "Straight cut with vertical lines"
            },
            "Hourglass": {
                "kurti": "Fitted, belted styles",
                "pants": "Any style — you're balanced!",
                "saree": "Nivi drape, highlight waist",
                "avoid": "Boxy shapes that hide waist",
                "abaya": "Belted or cinched waist"
            },
            "Rectangle": {
                "kurti": "Layered, peplum, ruffled",
                "pants": "Wide leg, patterned",
                "saree": "Bengali drape (adds curves)",
                "avoid": "Straight cuts head-to-toe",
                "abaya": "Layered or belted for definition"
            },
            "Inverted Triangle": {
                "kurti": "Flared bottom, minimal shoulder detail",
                "pants": "Wide palazzo, printed bottoms",
                "saree": "Mermaid style drape",
                "avoid": "Puff sleeves, heavy shoulder work",
                "abaya": "A-line cut, minimal top detail"
            }
        }
        
        bg = body_guide[body]
        st.markdown(f"""
        <div class="glass-card gold-accent">
            <h3 style="color: #d4af37;">{body} Body Styling Guide</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div><strong>Best Kurti:</strong><br>{bg['kurti']}</div>
                <div><strong>Best Bottom:</strong><br>{bg['pants']}</div>
                <div><strong>Saree Drape:</strong><br>{bg['saree']}</div>
                <div><strong>Abaya Cut:</strong><br>{bg['abaya']}</div>
            </div>
            <p style="color: #e0b0a0; margin-top: 1rem;">⚠️ <strong>Avoid:</strong> {bg['avoid']}</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------- WARDROBE & CALENDAR -------------------
elif nav == "👗 Wardrobe & Calendar":
    st.title("👗 Smart Digital Wardrobe")
    
    w_tabs = st.tabs(["My Wardrobe", "Capsule Generator", "Outfit Calendar"])
    
    with w_tabs[0]:
        st.subheader("📤 Upload & Manage Clothes")
        
        uploaded_cloth = st.file_uploader("Upload clothing item", type=['jpg', 'png'], accept_multiple_files=True)
        if uploaded_cloth:
            for file in uploaded_cloth:
                item = {
                    'name': file.name,
                    'category': random.choice(['Kurti', 'Hijab', 'Palazzo', 'Dupatta', 'Abaya', 'Shoes']),
                    'color': random.choice(['Red', 'Blue', 'Black', 'White', 'Green', 'Pink']),
                    'fabric': random.choice(['Cotton', 'Silk', 'Chiffon', 'Linen']),
                    'last_worn': 'Never',
                    'image': save_image(file)
                }
                st.session_state['wardrobe'].append(item)
            st.success(f"Added {len(uploaded_cloth)} items to wardrobe!")
        
        if st.session_state['wardrobe']:
            st.markdown("---")
            st.subheader(f"Your Closet ({len(st.session_state['wardrobe'])} items)")
            
            # Filter
            f1, f2, f3 = st.columns(3)
            cat_filter = f1.multiselect("Category", list(set([i['category'] for i in st.session_state['wardrobe']])))
            col_filter = f2.multiselect("Color", list(set([i['color'] for i in st.session_state['wardrobe']])))
            
            filtered = [i for i in st.session_state['wardrobe'] 
                       if (not cat_filter or i['category'] in cat_filter)
                       and (not col_filter or i['color'] in col_filter)]
            
            cols = st.columns(4)
            for idx, item in enumerate(filtered[:8]):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div style="font-size: 2.5rem;">👗</div>
                        <p style="color: #e0b0a0; font-weight: 600; margin: 0;">{item['category']}</p>
                        <p style="color: #888; font-size: 0.8rem;">{item['color']} • {item['fabric']}</p>
                        <p style="color: #555; font-size: 0.75rem;">Last: {item['last_worn']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Your wardrobe is empty. Upload clothes to get started!")
    
    with w_tabs[1]:
        st.subheader("🎯 Capsule Wardrobe Generator")
        
        if len(st.session_state['wardrobe']) < 3:
            st.warning("Upload at least 3 items to generate capsule combinations.")
        else:
            st.write("AI is analyzing your wardrobe for mix & match combinations...")
            
            # Generate combinations
            combos = []
            items = st.session_state['wardrobe']
            for i in range(min(6, len(items))):
                combo = random.sample(items, min(3, len(items)))
                combos.append(combo)
            
            for idx, combo in enumerate(combos):
                with st.expander(f"✨ Outfit Combination {idx+1}"):
                    c_str = " + ".join([f"{c['color']} {c['category']}" for c in combo])
                    st.write(f"**Look:** {c_str}")
                    st.button(f"Wear This on {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][idx]}", key=f"wear_{idx}")
    
    with w_tabs[2]:
        st.subheader("📅 Outfit Calendar Planner")
        
        cal_date = st.date_input("Select Date", datetime.date.today())
        occasion_cal = st.selectbox("Occasion for this date", 
                                    ["Regular Day", "Eid", "Wedding", "Office", "College", "Date", "Travel"])
        
        if st.button("Plan Outfit for Date"):
            planned = get_ai_recommendation(
                st.session_state.get('profile', {}),
                occasion_cal if occasion_cal != "Regular Day" else "Daily Wear",
                "Happy", "Pleasant 25°C", "Rectangle"
            )
            st.session_state['calendar_events'][str(cal_date)] = planned
            st.success(f"Outfit planned for {cal_date}!")
        
        # Show calendar events
        if st.session_state['calendar_events']:
            st.markdown("---")
            st.write("### Upcoming Planned Outfits")
            for date, outfit in list(st.session_state['calendar_events'].items())[:5]:
                st.markdown(f"""
                <div class="glass-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #d4af37;">{date}</strong>
                        <p style="margin: 0; color: #aaa;">{outfit['outfit']} + {outfit['hijab']}</p>
                    </div>
                    <span style="font-size: 1.5rem;">📌</span>
                </div>
                """, unsafe_allow_html=True)

# ------------------- FESTIVAL PLANNER -------------------
elif nav == "🎉 Festival Planner":
    st.title("🎉 Festival & Occasion Planner")
    
    occasions = {
        "Eid": {"icon": "🌙", "colors": "Gold, White, Green", "outfit": "Chikankari Anarkali or Abaya", "hijab": "Silk Turkish Wrap"},
        "Ramadan": {"icon": "🕌", "colors": "Pastel, Lavender, White", "outfit": "Loose Cotton Kurti + Palazzo", "hijab": "Breathable Jersey"},
        "Nikah": {"icon": "💍", "colors": "Red, Gold, Maroon", "outfit": "Heavy Lehenga + Full Sleeves", "hijab": "Bridal Net Drape"},
        "Mehendi": {"icon": "🌿", "colors": "Yellow, Green, Orange", "outfit": "Light Sharara or Gharara", "hijab": "Simple Chiffon"},
        "Reception": {"icon": "🥂", "colors": "Navy, Silver, Wine", "outfit": "Gown-style Anarkali", "hijab": "Layered with Pins"},
        "Diwali": {"icon": "🪔", "colors": "Red, Gold, Orange", "outfit": "Banarasi Saree or Silk Kurti", "hijab": "Pashmina or Silk"},
        "Birthday": {"icon": "🎂", "colors": "Personal favorite", "outfit": "Trendy Co-ord or Indo-Western", "hijab": "Stylish Turban"},
        "College Ethnic Day": {"icon": "🎓", "colors": "College colors or vibrant", "outfit": "Simple Kurti + Jeans", "hijab": "Casual Wrap"},
        "Friday Prayer": {"icon": "🤲", "colors": "Black, Navy, Earth tones", "outfit": "Prayer Abaya or Jilbab", "hijab": "Integrated Prayer Set"}
    }
    
    occ_cols = st.columns(3)
    for idx, (name, info) in enumerate(occasions.items()):
        with occ_cols[idx % 3]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; cursor: pointer;">
                <div style="font-size: 2.5rem;">{info['icon']}</div>
                <h4 style="color: #e0b0a0;">{name}</h4>
                <p style="color: #888; font-size: 0.8rem;">{info['outfit']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Plan {name}", key=f"plan_{name}", use_container_width=True):
                st.session_state['selected_occasion'] = name
    
    if 'selected_occasion' in st.session_state:
        occ = st.session_state['selected_occasion']
        info = occasions[occ]
        st.markdown("---")
        st.subheader(f"{info['icon']} Complete {occ} Styling Guide")
        
        oc1, oc2 = st.columns([2, 1])
        with oc1:
            st.markdown(f"""
            <div class="glass-card gold-accent">
                <h3 style="color: #d4af37;">{occ} Look</h3>
                <p><strong>Primary Outfit:</strong> {info['outfit']}</p>
                <p><strong>Hijab Style:</strong> {info['hijab']}</p>
                <p><strong>Color Palette:</strong> {info['colors']}</p>
                <p><strong>Jewelry:</strong> {random.choice(['Polki Set', 'Pearl Drops', 'Gold Jhumkas', 'Kundan Necklace'])}</p>
                <p><strong>Makeup:</strong> {random.choice(['Soft Glam', 'Bold Liner', 'Gold Shimmer', 'Natural Glow'])}</p>
                <p><strong>Mehendi:</strong> {random.choice(['Arabic Floral', 'Indo-Arabic Fusion', 'Minimal Finger', 'Bridal Full Hand'])}</p>
            </div>
            """, unsafe_allow_html=True)
        with oc2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a2e, #302b63); 
                        border-radius: 20px; height: 300px; display: flex; 
                        align-items: center; justify-content: center;
                        border: 1px solid rgba(212,175,55,0.2);">
                <div style="text-align: center;">
                    <div style="font-size: 4rem;">🧕</div>
                    <p style="color: #888;">Occasion Preview</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Caption generator
            st.markdown("---")
            st.caption("AI Caption Generator")
            caption = generate_caption(occ, info['outfit'], "Elegant")
            st.text_area("Copy this caption:", caption, height=100)
            st.button("📋 Copy to Clipboard")

# ------------------- ACCESSORIES & MAKEUP -------------------
elif nav == "💎 Accessories & Makeup":
    st.title("💎 Jewelry, Makeup & Mehendi")
    
    am_tabs = st.tabs(["Jewelry Matcher", "Makeup AI", "Mehendi Guide", "Hijab Color Matcher"])
    
    with am_tabs[0]:
        st.subheader("AI Jewelry & Accessory Matcher")
        outfit_color = st.color_picker("Your Outfit Color", "#800020")
        occasion_acc = st.selectbox("Occasion", ["Daily", "Office", "Wedding", "Party", "College"])
        
        # Color-based matching logic
        if outfit_color > "#555555":
            jewelry = "Gold / Antique Gold"
            bag = "Potli / Embroidered Clutch"
        else:
            jewelry = "Silver / Diamond / Kundan"
            bag = "Metallic Clutch / Sling"
        
        if occasion_acc == "Wedding":
            jewelry = "Heavy Bridal Set + Maang Tikka + Nath"
            bag = "Decorated Potli"
        elif occasion_acc == "Office":
            jewelry = "Small Studs + Watch"
            bag = "Tote / Structured Bag"
        
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; text-align: center;">
                <div>
                    <div style="font-size: 2rem;">💎</div>
                    <p style="color: #d4af37; font-weight: 600;">Jewelry</p>
                    <p style="color: #aaa; font-size: 0.85rem;">{jewelry}</p>
                </div>
                <div>
                    <div style="font-size: 2rem;">🎒</div>
                    <p style="color: #d4af37; font-weight: 600;">Bag</p>
                    <p style="color: #aaa; font-size: 0.85rem;">{bag}</p>
                </div>
                <div>
                    <div style="font-size: 2rem;">👠</div>
                    <p style="color: #d4af37; font-weight: 600;">Footwear</p>
                    <p style="color: #aaa; font-size: 0.85rem;">{random.choice(['Juttis', 'Heels', 'Kolhapuris', 'Block Heels'])}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with am_tabs[1]:
        st.subheader("Makeup Recommendation AI")
        makeup_occ = st.selectbox("Occasion", ["Daily", "Eid", "Wedding", "College", "Date"])
        makeup_tone = st.radio("Skin Tone", ["Fair", "Medium", "Tan", "Deep"], horizontal=True)
        
        makeup_recs = {
            "Daily": {"lip": "Nude Pink", "eye": "Brown Mascara", "blush": "Soft Peach", "base": "BB Cream"},
            "Eid": {"lip": "Berry / Rose", "eye": "Gold Shimmer", "blush": "Coral", "base": "Medium Coverage"},
            "Wedding": {"lip": "Red / Maroon", "eye": "Smokey Gold", "blush": "Deep Rose", "base": "Full Coverage"},
            "College": {"lip": "Tinted Balm", "eye": "Kohl Liner", "blush": "None", "base": "Tinted Moisturizer"},
            "Date": {"lip": "Dusty Rose", "eye": "Soft Wing", "blush": "Pink Glow", "base": "Dewy Finish"}
        }
        
        mr = makeup_recs[makeup_occ]
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color: #e0b0a0;">{makeup_occ} Makeup Look</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>💄 <strong>Lipstick:</strong> {mr['lip']}</div>
                <div>👁️ <strong>Eyes:</strong> {mr['eye']}</div>
                <div>🌸 <strong>Blush:</strong> {mr['blush']}</div>
                <div>✨ <strong>Base:</strong> {mr['base']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("Nail Color Suggestion: Match with hijab or dupatta accent color.")
    
    with am_tabs[2]:
        st.subheader("Mehendi Design Guide")
        meh_style = st.selectbox("Style", ["Arabic", "Bridal", "Minimal", "Floral", "Indo-Arabic", "Finger Only"])
        meh_images = {
            "Arabic": "Flowing vines, negative space, floral trails",
            "Bridal": "Full hand intricate, groom name hidden, peacocks",
            "Minimal": "Small wrist band, single finger accent",
            "Floral": "Roses, lotus patterns, dense flowers",
            "Indo-Arabic": "Mix of Indian detail + Arabic flow",
            "Finger Only": "Rings, fingertips, geometric finger patterns"
        }
        st.info(meh_images[meh_style])
        st.button("📸 View Design Gallery")
    
    with am_tabs[3]:
        st.subheader("Hijab Color Matcher")
        base_color = st.color_picker("Outfit/Dress Color", "#2E8B57")
        st.write("AI suggests complementary hijab colors:")
        
        # Simple complementary logic
        st.markdown("""
        <div style="display: flex; gap: 15px; margin-top: 1rem;">
            <div style="text-align: center;">
                <div style="width: 80px; height: 80px; background: #D4AF37; border-radius: 50%; margin: 0 auto;"></div>
                <p style="color: #aaa; font-size: 0.8rem;">Gold</p>
            </div>
            <div style="text-align: center;">
                <div style="width: 80px; height: 80px; background: #F5F5DC; border-radius: 50%; margin: 0 auto;"></div>
                <p style="color: #aaa; font-size: 0.8rem;">Beige</p>
            </div>
            <div style="text-align: center;">
                <div style="width: 80px; height: 80px; background: #800020; border-radius: 50%; margin: 0 auto;"></div>
                <p style="color: #aaa; font-size: 0.8rem;">Burgundy</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ------------------- ANALYTICS DASHBOARD -------------------
elif nav == "📊 Analytics Dashboard":
    st.title("📊 AI Closet Analytics & Trends")
    
    dash_tabs = st.tabs(["My Wardrobe Analytics", "Fashion Trends", "Sustainability Score"])
    
    with dash_tabs[0]:
        st.subheader("📈 Your Wardrobe Insights")
        
        # Mock data for charts
        color_data = pd.DataFrame({
            'Color': ['Black', 'White', 'Blue', 'Pink', 'Beige', 'Red'],
            'Count': [12, 8, 6, 5, 4, 3]
        })
        fabric_data = pd.DataFrame({
            'Fabric': ['Cotton', 'Silk', 'Chiffon', 'Linen', 'Velvet', 'Georgette'],
            'Count': [15, 8, 7, 5, 3, 6]
        })
        
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.pie(color_data, values='Count', names='Color', title='Color Distribution',
                         color_discrete_sequence=px.colors.sequential.Plasma)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
            st.plotly_chart(fig1, use_container_width=True)
        
        with c2:
            fig2 = px.bar(fabric_data, x='Fabric', y='Count', title='Fabric Usage',
                         color='Count', color_continuous_scale='gold')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Spending graph
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        spending = [2500, 1800, 4200, 1500, 3800, 2100]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=months, y=spending, fill='tozeroy', 
                                   line=dict(color='#d4af37'), fillcolor='rgba(212,175,55,0.2)'))
        fig3.update_layout(title='Monthly Fashion Spending (₹)', paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig3, use_container_width=True)
        
        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Items", len(st.session_state['wardrobe']) or 24, "+3 this month")
        m2.metric("Most Worn", "Black Kurti", "12 times")
        m3.metric("Cost Per Wear", "₹45", "-12%")
        m4.metric("Sustainability", "78/100", "+5")
    
    with dash_tabs[1]:
        st.subheader("🔥 2026 Modest Fashion Trends")
        
        trends = pd.DataFrame({
            'Trend': ['Pastel Hijabs', 'Organza Dupattas', 'Indo-Western Abayas', 'Pearl Accessories', 'Chikankari Revival'],
            'Popularity': [95, 88, 82, 76, 91],
            'Growth': [15, 22, 35, 12, 28]
        })
        
        fig4 = px.scatter(trends, x='Popularity', y='Growth', size='Popularity', color='Trend',
                         title='Trending Modest Fashion 2026', color_discrete_sequence=px.colors.sequential.Gold)
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #d4af37;">This Season's Must-Haves</h4>
            <ul style="color: #ccc;">
                <li>🌸 <strong>Pastel Hijabs:</strong> Lavender, Sage, Dusty Rose dominating 2026</li>
                <li>✨ <strong>Organza Dupattas:</strong> Sheer layering over jersey hijabs</li>
                <li>🪡 <strong>Chikankari Revival:</strong> Lucknowi embroidery on modern cuts</li>
                <li>🧥 <strong>Indo-Western Abayas:</strong> Belted, collared, with Indian motifs</li>
                <li>📿 <strong>Pearl Accessories:</strong> Oversized pearls on hijab pins and bags</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with dash_tabs[2]:
        st.subheader("🌱 Sustainable Fashion Score")
        
        eco_score = 78
        st.progress(eco_score/100, text=f"Eco Score: {eco_score}/100")
        
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #4CAF50;">Your Sustainability Breakdown</h4>
            <p>♻️ <strong>Outfit Reuse Rate:</strong> 68% (Above average!)</p>
            <p>🧵 <strong>Natural Fabrics:</strong> 45% of wardrobe</p>
            <p>🛍️ <strong>Local Brands:</strong> 30% purchases</p>
            <p>📦 <strong>Carbon Footprint:</strong> Low (Mostly Indian brands)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.button("🎁 Claim Sustainable Fashion Badge")
        st.button("📤 Donate Unused Clothes")

# ------------------- JOURNAL & ADMIN -------------------
elif nav == "📔 Journal & Admin":
    st.title("📔 Fashion Journal & Admin")
    
    ja_tabs = st.tabs(["Fashion Journal", "Packing Assistant", "Budget Planner", "Admin Dashboard"])
    
    with ja_tabs[0]:
        st.subheader("📝 Your Outfit Diary")
        
        entry_date = st.date_input("Date", datetime.date.today())
        entry_mood = st.selectbox("Mood", ["Happy", "Confident", "Calm", "Energetic", "Elegant", "Nostalgic"])
        entry_outfit = st.text_input("What did you wear?")
        entry_occ = st.text_input("Occasion")
        entry_notes = st.text_area("Notes & Feelings")
        entry_photo = st.file_uploader("Add Photo", type=['jpg', 'png'])
        
        if st.button("Save Journal Entry"):
            st.session_state['journal'].append({
                'date': entry_date, 'mood': entry_mood, 'outfit': entry_outfit,
                'occasion': entry_occ, 'notes': entry_notes
            })
            st.success("Memory saved!")
        
        if st.session_state['journal']:
            st.markdown("---")
            st.write("### Past Entries")
            for entry in reversed(st.session_state['journal'][-5:]):
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between;">
                        <strong style="color: #d4af37;">{entry['date']}</strong>
                        <span style="color: #888;">{entry['mood']}</span>
                    </div>
                    <p style="margin: 0.5rem 0;"><strong>{entry['outfit']}</strong> for {entry['occasion']}</p>
                    <p style="color: #aaa; font-size: 0.9rem;">{entry['notes']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with ja_tabs[1]:
        st.subheader("🧳 AI Packing Assistant")
        destination = st.text_input("Destination")
        days = st.number_input("Days", 1, 30, 3)
        trip_type = st.selectbox("Trip Type", ["Business", "Vacation", "Wedding", "Umrah/Hajj", "College Trip"])
        
        if st.button("Generate Packing List"):
            items = []
            if trip_type == "Umrah/Hajj":
                items = ["2 White Ihram Abayas", "Prayer Rug", "Travel Prayer Set", "Comfortable Sneakers", "Unscented Lotion"]
            elif trip_type == "Wedding":
                items = ["Heavy Lehenga", "Light Sangeet Outfit", "2 Hijabs (Bridal + Casual)", "Jewelry Set", "Makeup Kit"]
            else:
                items = [f"{days} Kurtis", f"{days//2 + 1} Hijabs", "1 Pair Comfortable Shoes", "Toiletries", "Accessories"]
            
            st.session_state['packing_list'] = items
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: #d4af37;">{trip_type} Packing List for {destination}</h4>
                <ul style="color: #ccc;">
                    {''.join([f'<li>{item}</li>' for item in items])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            st.button("📋 Copy Checklist")
    
    with ja_tabs[2]:
        st.subheader("💰 Budget Fashion Planner")
        monthly_budget = st.number_input("Monthly Budget (₹)", 1000, 50000, 5000)
        spent = st.number_input("Already Spent (₹)", 0, 50000, 1200)
        
        remaining = monthly_budget - spent
        st.metric("Remaining Budget", f"₹{remaining}")
        st.progress(spent/monthly_budget, text=f"Used: ₹{spent} / ₹{monthly_budget}")
        
        if remaining < 1000:
            st.warning("⚠️ Low budget! Check out our Thrift & Sale section.")
        
        # Budget allocation
        alloc = pd.DataFrame({
            'Category': ['Hijabs', 'Kurtis', 'Bottoms', 'Occasion Wear', 'Accessories', 'Shoes'],
            'Recommended %': [20, 30, 15, 20, 10, 5],
            'Amount': [monthly_budget*0.2, monthly_budget*0.3, monthly_budget*0.15, 
                      monthly_budget*0.2, monthly_budget*0.1, monthly_budget*0.05]
        })
        fig5 = px.pie(alloc, values='Amount', names='Category', title='Recommended Budget Split',
                     color_discrete_sequence=px.colors.sequential.Sunset)
        fig5.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig5, use_container_width=True)
    
    with ja_tabs[3]:
        st.subheader("🔐 Admin Dashboard")
        
        # Admin metrics
        a1, a2, a3, a4 = st.columns(4)
        stats = st.session_state['admin_stats']
        a1.metric("Total Users", stats['users'])
        a2.metric("Outfits Generated", stats['outfits'])
        a3.metric("Photos Uploaded", stats['photos'])
        a4.metric("Active Today", 142)
        
        # Engagement chart
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        users = [120, 135, 128, 142, 155, 180, 165]
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(x=days, y=users, marker_color='#d4af37'))
        fig6.update_layout(title='Weekly User Engagement', paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig6, use_container_width=True)
        
        # Popular colors table
        pop_colors = pd.DataFrame({
            'Color': ['Black', 'Beige', 'Dusty Rose', 'Navy', 'Emerald'],
            'Selections': [2340, 1890, 1650, 1420, 1200],
            'Trend': ['Stable', 'Rising', 'Rising', 'Stable', 'New']
        })
        st.dataframe(pop_colors, use_container_width=True, hide_index=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #555;">
    <p style="font-family: Playfair Display; color: #d4af37; font-size: 1.2rem;">AI Hijab & Indian Outfit Studio</p>
    <p style="font-size: 0.8rem;">B.Sc. Data Science Final Year Project | 2026</p>
    <p style="font-size: 0.75rem; color: #444;">Modules: Recommendation Engine • Computer Vision • NLP • Weather API • Data Analytics</p>
</div>
""", unsafe_allow_html=True)
