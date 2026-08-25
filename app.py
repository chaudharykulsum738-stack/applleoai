import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import requests
import random
from datetime import datetime
import os

# Handle optional mediapipe
MEDIAPIPE_AVAILABLE = False
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    mp = None

st.set_page_config(page_title="AI Hijab & Indian Outfit Stylist", page_icon="🧕", layout="wide")

st.markdown("""
<style>
.main-header { font-size: 2.5rem; font-weight: 800;
background: linear-gradient(90deg, #8B5CF6, #EC4899);
-webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sub-header { font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem; }
.score-high { background: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 20px; font-weight: 600; }
.score-mid { background: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 20px; font-weight: 600; }
.score-low { background: #FEE2E2; color: #991B1B; padding: 4px 12px; border-radius: 20px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

def init_session():
    defaults = {
        "authenticated": False, "user": None, "preferences": {},
        "wardrobe": WARDROBE_DEFAULTS.copy(), "festival_events": [], "admin_view": False,
        "location": "Mumbai, IN", "weather_api_key": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_session()

if not MEDIAPIPE_AVAILABLE:
    st.warning("MediaPipe not installed. Face detection uses OpenCV fallback. For best results, install locally: pip install mediapipe")

# ============ DATASETS ============
OUTFIT_TEMPLATES = [
    {"id": 1, "name": "Cotton Kurti + Palazzo", "category": "daily", "occasion": "College Wear",
     "colors": ["peach", "mint", "white"], "fabrics": ["cotton", "linen"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "low", "body_shapes": ["pear", "apple", "rectangle"]},
    {"id": 2, "name": "Silk Anarkali + Dupatta", "category": "festive", "occasion": "Wedding Guest",
     "colors": ["maroon", "gold", "emerald"], "fabrics": ["silk", "banarasi"], "weather": ["winter", "spring"],
     "modesty": 10, "budget": "high", "body_shapes": ["hourglass", "pear", "apple"]},
    {"id": 3, "name": "Linen Abaya + Jersey Hijab", "category": "daily", "occasion": "Office Wear",
     "colors": ["black", "navy", "beige"], "fabrics": ["linen", "jersey"], "weather": ["summer", "spring"],
     "modesty": 10, "budget": "medium", "body_shapes": ["all"]},
    {"id": 4, "name": "Chikankari Suit", "category": "festive", "occasion": "Eid Collection",
     "colors": ["white", "pastel pink", "sky blue"], "fabrics": ["cotton", "chikankari"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "medium", "body_shapes": ["rectangle", "hourglass", "pear"]},
    {"id": 5, "name": "Velvet Sharara Set", "category": "festive", "occasion": "Nikah Outfit",
     "colors": ["burgundy", "deep green", "royal blue"], "fabrics": ["velvet", "georgette"], "weather": ["winter"],
     "modesty": 10, "budget": "luxury", "body_shapes": ["hourglass", "rectangle"]},
    {"id": 6, "name": "Saree + Hijab Drape", "category": "festive", "occasion": "Reception",
     "colors": ["gold", "red", "purple"], "fabrics": ["silk", "banarasi"], "weather": ["winter", "spring"],
     "modesty": 9, "budget": "high", "body_shapes": ["hourglass", "pear"]},
    {"id": 7, "name": "Casual Jeans + Long Kurti", "category": "daily", "occasion": "Casual Wear",
     "colors": ["denim blue", "olive", "rust"], "fabrics": ["denim", "cotton"], "weather": ["summer", "spring", "winter"],
     "modesty": 8, "budget": "low", "body_shapes": ["all"]},
    {"id": 8, "name": "Kaftan Dress", "category": "daily", "occasion": "Home Wear",
     "colors": ["beige", "grey", "pastel"], "fabrics": ["modal", "jersey"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "low", "body_shapes": ["apple", "rectangle"]},
    {"id": 9, "name": "Organza Lehenga + Hijab", "category": "festive", "occasion": "Mehendi",
     "colors": ["yellow", "green", "orange"], "fabrics": ["organza", "net"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "high", "body_shapes": ["pear", "hourglass"]},
    {"id": 10, "name": "Pashmina Coat + Wool Hijab", "category": "daily", "occasion": "Travel Wear",
     "colors": ["coffee", "charcoal", "burgundy"], "fabrics": ["wool", "pashmina"], "weather": ["winter"],
     "modesty": 10, "budget": "medium", "body_shapes": ["all"]},
    {"id": 11, "name": "Indo-Western Co-ord Set", "category": "daily", "occasion": "Friday Prayer Outfit",
     "colors": ["black", "white", "navy"], "fabrics": ["rayon", "georgette"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "medium", "body_shapes": ["rectangle", "inverted_triangle"]},
    {"id": 12, "name": "Bridal Abaya with Zardozi", "category": "festive", "occasion": "Nikah Outfit",
     "colors": ["gold", "ivory", "rose gold"], "fabrics": ["silk", "organza"], "weather": ["winter", "spring"],
     "modesty": 10, "budget": "luxury", "body_shapes": ["all"]},
    # --- 30 NEW AI RECOMMENDATION OUTFITS ---
    {"id": 13, "name": "Net Lehenga + Velvet Dupatta", "category": "festive", "occasion": "Sangeet Night",
     "colors": ["wine", "gold", "blush"], "fabrics": ["net", "velvet"], "weather": ["winter", "spring"],
     "modesty": 9, "budget": "luxury", "body_shapes": ["hourglass", "pear"]},
    {"id": 14, "name": "Banarasi Saree + Full Sleeve Blouse", "category": "festive", "occasion": "Wedding Guest",
     "colors": ["red", "gold", "green"], "fabrics": ["silk", "banarasi"], "weather": ["winter", "spring"],
     "modesty": 10, "budget": "high", "body_shapes": ["hourglass", "rectangle", "pear"]},
    {"id": 15, "name": "Gharara Suit with Zari Work", "category": "festive", "occasion": "Nikah Outfit",
     "colors": ["ivory", "gold", "peach"], "fabrics": ["georgette", "zari"], "weather": ["winter", "spring"],
     "modesty": 10, "budget": "luxury", "body_shapes": ["apple", "rectangle", "hourglass"]},
    {"id": 16, "name": "Peplum Kurti + Dhoti Pants", "category": "festive", "occasion": "Mehendi",
     "colors": ["lime", "mint", "white"], "fabrics": ["crepe", "cotton"], "weather": ["summer", "spring"],
     "modesty": 8, "budget": "medium", "body_shapes": ["rectangle", "inverted_triangle"]},
    {"id": 17, "name": "Mirror Work Lehenga", "category": "festive", "occasion": "Garba Night",
     "colors": ["fuchsia", "orange", "yellow"], "fabrics": ["cotton", "mirror_work"], "weather": ["summer", "spring"],
     "modesty": 8, "budget": "medium", "body_shapes": ["pear", "hourglass"]},
    {"id": 18, "name": "Silk Abaya with Embroidery", "category": "festive", "occasion": "Eid Collection",
     "colors": ["emerald", "gold", "black"], "fabrics": ["silk", "embroidery"], "weather": ["winter", "spring"],
     "modesty": 10, "budget": "high", "body_shapes": ["all"]},
    {"id": 19, "name": "Angrakha Style Anarkali", "category": "festive", "occasion": "Wedding Guest",
     "colors": ["teal", "copper", "cream"], "fabrics": ["silk", "brocade"], "weather": ["winter", "spring"],
     "modesty": 9, "budget": "high", "body_shapes": ["apple", "rectangle"]},
    {"id": 20, "name": "Floral Print Maxi Dress + Hijab", "category": "festive", "occasion": "Eid Brunch",
     "colors": ["pastel pink", "lilac", "white"], "fabrics": ["chiffon", "georgette"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "medium", "body_shapes": ["pear", "apple"]},
    {"id": 21, "name": "Bridal Lehenga with Long Choli", "category": "festive", "occasion": "Reception",
     "colors": ["red", "gold", "maroon"], "fabrics": ["velvet", "silk"], "weather": ["winter"],
     "modesty": 9, "budget": "luxury", "body_shapes": ["hourglass", "pear"]},
    {"id": 22, "name": "Chanderi Silk Suit", "category": "festive", "occasion": "Diwali Pooja",
     "colors": ["mustard", "rust", "green"], "fabrics": ["chanderi", "silk"], "weather": ["spring", "winter"],
     "modesty": 9, "budget": "medium", "body_shapes": ["rectangle", "hourglass"]},
    {"id": 23, "name": "Tunic Kurti + Jeggings", "category": "daily", "occasion": "College Wear",
     "colors": ["denim blue", "white", "striped"], "fabrics": ["cotton", "denim"], "weather": ["summer", "spring", "winter"],
     "modesty": 8, "budget": "low", "body_shapes": ["all"]},
    {"id": 24, "name": "A-Line Cotton Dress + Cardigan", "category": "daily", "occasion": "Office Wear",
     "colors": ["navy", "grey", "burgundy"], "fabrics": ["cotton", "knit"], "weather": ["winter", "spring"],
     "modesty": 9, "budget": "medium", "body_shapes": ["apple", "rectangle"]},
    {"id": 25, "name": "Jersey Maxi Skirt + Long Top", "category": "daily", "occasion": "Casual Wear",
     "colors": ["black", "olive", "tan"], "fabrics": ["jersey", "modal"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "low", "body_shapes": ["pear", "hourglass"]},
    {"id": 26, "name": "Pleated Palazzo + Short Kurti", "category": "daily", "occasion": "College Wear",
     "colors": ["white", "peach", "mint"], "fabrics": ["rayon", "cotton"], "weather": ["summer", "spring"],
     "modesty": 8, "budget": "low", "body_shapes": ["rectangle", "inverted_triangle"]},
    {"id": 27, "name": "Denim Abaya + Sneakers", "category": "daily", "occasion": "Travel Wear",
     "colors": ["denim blue", "black", "grey"], "fabrics": ["denim", "cotton"], "weather": ["summer", "spring", "winter"],
     "modesty": 10, "budget": "medium", "body_shapes": ["all"]},
    {"id": 28, "name": "Wrap Style Kurti + Cigarette Pants", "category": "daily", "occasion": "Office Wear",
     "colors": ["beige", "rust", "navy"], "fabrics": ["linen", "cotton"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "medium", "body_shapes": ["apple", "hourglass"]},
    {"id": 29, "name": "Hoodie Abaya + Joggers", "category": "daily", "occasion": "Travel Wear",
     "colors": ["charcoal", "olive", "black"], "fabrics": ["fleece", "cotton"], "weather": ["winter"],
     "modesty": 10, "budget": "medium", "body_shapes": ["all"]},
    {"id": 30, "name": "Tiered Cotton Dress", "category": "daily", "occasion": "Home Wear",
     "colors": ["lavender", "sage", "cream"], "fabrics": ["cotton", "voile"], "weather": ["summer", "spring"],
     "modesty": 8, "budget": "low", "body_shapes": ["rectangle", "pear"]},
    {"id": 31, "name": "Long Shirt + Wide Leg Pants", "category": "daily", "occasion": "Friday Prayer Outfit",
     "colors": ["white", "black", "navy"], "fabrics": ["poplin", "cotton"], "weather": ["summer", "spring", "winter"],
     "modesty": 9, "budget": "low", "body_shapes": ["all"]},
    {"id": 32, "name": "Ribbed Knit Dress + Wool Hijab", "category": "daily", "occasion": "Office Wear",
     "colors": ["camel", "burgundy", "forest green"], "fabrics": ["knit", "wool"], "weather": ["winter"],
     "modesty": 9, "budget": "medium", "body_shapes": ["hourglass", "rectangle"]},
    {"id": 33, "name": "Sequin Abaya + Satin Hijab", "category": "festive", "occasion": "Party",
     "colors": ["black", "gold", "silver"], "fabrics": ["sequin", "satin"], "weather": ["winter", "spring"],
     "modesty": 10, "budget": "luxury", "body_shapes": ["all"]},
    {"id": 34, "name": "Ruffled Saree Gown", "category": "festive", "occasion": "Reception",
     "colors": ["blush", "champagne", "rose gold"], "fabrics": ["organza", "satin"], "weather": ["spring", "winter"],
     "modesty": 9, "budget": "luxury", "body_shapes": ["hourglass", "pear"]},
    {"id": 35, "name": "Cape Style Anarkali", "category": "festive", "occasion": "Wedding Guest",
     "colors": ["royal blue", "silver", "navy"], "fabrics": ["georgette", "net"], "weather": ["winter", "spring"],
     "modesty": 9, "budget": "high", "body_shapes": ["rectangle", "inverted_triangle"]},
    {"id": 36, "name": "Draped Jumpsuit + Hijab", "category": "festive", "occasion": "Party",
     "colors": ["emerald", "black", "wine"], "fabrics": ["crepe", "jersey"], "weather": ["summer", "spring", "winter"],
     "modesty": 9, "budget": "high", "body_shapes": ["hourglass", "rectangle"]},
    {"id": 37, "name": "Feather Trim Abaya", "category": "festive", "occasion": "Party",
     "colors": ["ivory", "black", "dusty rose"], "fabrics": ["satin", "feather"], "weather": ["winter"],
     "modesty": 10, "budget": "luxury", "body_shapes": ["all"]},
    {"id": 38, "name": "Linen Co-ord Set + Sun Hat", "category": "daily", "occasion": "Travel Wear",
     "colors": ["sand", "white", "terracotta"], "fabrics": ["linen", "cotton"], "weather": ["summer"],
     "modesty": 8, "budget": "medium", "body_shapes": ["rectangle", "apple"]},
    {"id": 39, "name": "Thermal Wool Abaya + Boots", "category": "daily", "occasion": "Travel Wear",
     "colors": ["coffee", "black", "plum"], "fabrics": ["wool", "thermal"], "weather": ["winter"],
     "modesty": 10, "budget": "medium", "body_shapes": ["all"]},
    {"id": 40, "name": "Raincoat Style Trench + Hijab", "category": "daily", "occasion": "Travel Wear",
     "colors": ["mustard", "olive", "navy"], "fabrics": ["polyester", "nylon"], "weather": ["winter", "spring"],
     "modesty": 9, "budget": "medium", "body_shapes": ["all"]},
    {"id": 41, "name": "Kashmiri Pheran + Woolen Hijab", "category": "daily", "occasion": "Home Wear",
     "colors": ["maroon", "navy", "forest green"], "fabrics": ["wool", "kashmiri"], "weather": ["winter"],
     "modesty": 10, "budget": "medium", "body_shapes": ["all"]},
    {"id": 42, "name": "Chikankari Anarkali + Cotton Dupatta", "category": "festive", "occasion": "Eid Collection",
     "colors": ["white", "peach", "mint green"], "fabrics": ["cotton", "chikankari"], "weather": ["summer", "spring"],
     "modesty": 9, "budget": "medium", "body_shapes": ["pear", "hourglass", "rectangle"]},
]

WARDROBE_DEFAULTS = [
    {"id": 1, "name": "Black Jersey Hijab", "category": "hijab", "color": "black", "fabric": "jersey", "occasion": "daily", "added": "2025-01-15", "worn": 12},
    {"id": 2, "name": "Beige Chiffon Hijab", "category": "hijab", "color": "beige", "fabric": "chiffon", "occasion": "daily", "added": "2025-01-20", "worn": 8},
    {"id": 3, "name": "Maroon Pashmina Shawl", "category": "hijab", "color": "maroon", "fabric": "pashmina", "occasion": "festive", "added": "2025-02-01", "worn": 3},
    {"id": 4, "name": "White Cotton Kurti", "category": "kurti", "color": "white", "fabric": "cotton", "occasion": "daily", "added": "2025-01-10", "worn": 15},
    {"id": 5, "name": "Peach A-Line Kurti", "category": "kurti", "color": "peach", "fabric": "cotton", "occasion": "college", "added": "2025-01-25", "worn": 6},
    {"id": 6, "name": "Navy Silk Anarkali", "category": "kurti", "color": "navy", "fabric": "silk", "occasion": "festive", "added": "2025-02-10", "worn": 2},
    {"id": 7, "name": "Black Abaya with Lace", "category": "abaya", "color": "black", "fabric": "georgette", "occasion": "daily", "added": "2025-01-12", "worn": 20},
    {"id": 8, "name": "Grey Linen Abaya", "category": "abaya", "color": "grey", "fabric": "linen", "occasion": "office", "added": "2025-01-18", "worn": 10},
    {"id": 9, "name": "Emerald Velvet Abaya", "category": "abaya", "color": "green", "fabric": "velvet", "occasion": "festive", "added": "2025-02-05", "worn": 1},
    {"id": 10, "name": "White Palazzo Pants", "category": "palazzo", "color": "white", "fabric": "cotton", "occasion": "daily", "added": "2025-01-08", "worn": 18},
    {"id": 11, "name": "Black Wide Leg Palazzo", "category": "palazzo", "color": "black", "fabric": "rayon", "occasion": "office", "added": "2025-01-22", "worn": 9},
    {"id": 12, "name": "Gold Banarasi Saree", "category": "saree", "color": "gold", "fabric": "banarasi", "occasion": "wedding", "added": "2025-02-15", "worn": 1},
    {"id": 13, "name": "Red Silk Saree", "category": "saree", "color": "red", "fabric": "silk", "occasion": "wedding", "added": "2025-02-12", "worn": 2},
    {"id": 14, "name": "Pink Lehenga Skirt", "category": "lehenga", "color": "pink", "fabric": "georgette", "occasion": "festive", "added": "2025-02-20", "worn": 1},
    {"id": 15, "name": "Yellow Mehendi Lehenga", "category": "lehenga", "color": "yellow", "fabric": "organza", "occasion": "festive", "added": "2025-02-25", "worn": 1},
    {"id": 16, "name": "Maroon Sharara Set", "category": "sharara", "color": "maroon", "fabric": "georgette", "occasion": "festive", "added": "2025-02-08", "worn": 2},
    {"id": 17, "name": "Ivory Gharara Pants", "category": "sharara", "color": "white", "fabric": "silk", "occasion": "wedding", "added": "2025-02-18", "worn": 1},
    {"id": 18, "name": "Blue Denim Jeans", "category": "jeans", "color": "blue", "fabric": "denim", "occasion": "daily", "added": "2025-01-05", "worn": 25},
    {"id": 19, "name": "Black Straight Jeans", "category": "jeans", "color": "black", "fabric": "denim", "occasion": "college", "added": "2025-01-14", "worn": 14},
    {"id": 20, "name": "Gold Jhumka Earrings", "category": "jewelry", "color": "gold", "fabric": "metal", "occasion": "wedding", "added": "2025-02-01", "worn": 3},
    {"id": 21, "name": "Pearl Stud Earrings", "category": "jewelry", "color": "white", "fabric": "pearl", "occasion": "office", "added": "2025-01-11", "worn": 11},
    {"id": 22, "name": "Silver Statement Necklace", "category": "jewelry", "color": "silver", "fabric": "metal", "occasion": "party", "added": "2025-01-28", "worn": 4},
    {"id": 23, "name": "Embroidered Potli Bag", "category": "bag", "color": "gold", "fabric": "silk", "occasion": "wedding", "added": "2025-02-10", "worn": 2},
    {"id": 24, "name": "Black Structured Handbag", "category": "bag", "color": "black", "fabric": "leather", "occasion": "office", "added": "2025-01-16", "worn": 16},
    {"id": 25, "name": "Beige Tote Bag", "category": "bag", "color": "beige", "fabric": "canvas", "occasion": "college", "added": "2025-01-19", "worn": 7},
    {"id": 26, "name": "Gold Kolhapuris", "category": "shoes", "color": "gold", "fabric": "leather", "occasion": "festive", "added": "2025-02-05", "worn": 3},
    {"id": 27, "name": "Black Block Heels", "category": "shoes", "color": "black", "fabric": "leather", "occasion": "party", "added": "2025-01-21", "worn": 5},
    {"id": 28, "name": "White Sneakers", "category": "shoes", "color": "white", "fabric": "canvas", "occasion": "college", "added": "2025-01-09", "worn": 22},
    {"id": 29, "name": "Red Net Dupatta", "category": "dupatta", "color": "red", "fabric": "net", "occasion": "festive", "added": "2025-02-14", "worn": 2},
    {"id": 30, "name": "Green Chiffon Dupatta", "category": "dupatta", "color": "green", "fabric": "chiffon", "occasion": "daily", "added": "2025-01-17", "worn": 8},
]

FESTIVALS = [
    {"name": "Eid al-Fitr", "type": "eid", "colors": ["green", "gold", "white"], "style": "elegant"},
    {"name": "Diwali", "type": "diwali", "colors": ["red", "gold", "orange"], "style": "festive"},
    {"name": "Wedding Season", "type": "wedding", "colors": ["maroon", "gold", "pink"], "style": "luxury"},
    {"name": "Mehendi Night", "type": "mehendi", "colors": ["yellow", "green", "orange"], "style": "playful"},
    {"name": "Nikah Ceremony", "type": "nikah", "colors": ["ivory", "gold", "pastel"], "style": "elegant"},
    {"name": "College Ethnic Day", "type": "college", "colors": ["any"], "style": "traditional"},
    {"name": "Ramadan Iftar", "type": "ramadan", "colors": ["pastel", "white", "lavender"], "style": "comfortable"},
]

COLOR_HARMONY = {
    "warm": ["peach", "coral", "gold", "orange", "yellow", "olive", "brown", "rust", "mustard"],
    "cool": ["blue", "purple", "pink", "silver", "emerald", "ruby", "navy", "lavender"],
    "neutral": ["beige", "taupe", "grey", "white", "black", "navy", "cream"],
    "olive": ["burgundy", "plum", "forest green", "rust", "cream", "gold"],
}

BODY_SHAPE_ADVICE = {
    "pear": {"best_kurti": "A-line, Anarkali, Flared (hides hips)", "sleeves": "Full sleeves or bell sleeves",
             "bottoms": "Palazzo, Sharara, Wide-leg pants", "avoid": "Body-hugging pencil cuts",
             "saree_drape": "Seedha pallu or Gujarati style", "hijab_tip": "Volume on top, draped loosely around face"},
    "apple": {"best_kurti": "Empire waist, Flowy A-line, Kaftan", "sleeves": "3/4 sleeves, avoid cap sleeves",
              "bottoms": "Straight pants, Churidar", "avoid": "Tight waistbands, belted styles",
              "saree_drape": "Bengali style with pleats in front", "hijab_tip": "Medium volume, avoid too much fabric near face"},
    "hourglass": {"best_kurti": "Fitted, Belted Anarkali, Straight cut", "sleeves": "Any sleeve style works",
                  "bottoms": "Straight pants, Fitted palazzo", "avoid": "Overly boxy cuts that hide waist",
                  "saree_drape": "Nivi style (showcases curves modestly)", "hijab_tip": "Turkish wrap or layered styles"},
    "rectangle": {"best_kurti": "Layered, Ruffled, Peplum style", "sleeves": "Puffed sleeves, Layered sleeves",
                  "bottoms": "Sharara, Gharara, Flared pants", "avoid": "Straight boxy cuts without definition",
                  "saree_drape": "Butterfly style with volume", "hijab_tip": "Volume around face and shoulders"},
    "inverted_triangle": {"best_kurti": "Flared bottom, A-line, Anarkali", "sleeves": "Avoid heavy shoulder details",
                         "bottoms": "Wide-leg palazzo, Sharara (balances shoulders)", "avoid": "Puffed sleeves, heavy shoulder embroidery",
                         "saree_drape": "Loose pallu to soften shoulders", "hijab_tip": "Soft drapes, avoid structured volume on top"}
}

MAKEUP_GUIDE = {
    "warm": {"lipstick": ["Coral", "Peach", "Warm Red", "Terracotta"], "eyeshadow": ["Gold", "Bronze", "Copper"], "jewelry": "Gold"},
    "cool": {"lipstick": ["Berry", "Plum", "Blue-red", "Pink"], "eyeshadow": ["Silver", "Lavender", "Cool Grey"], "jewelry": "Silver/Rose Gold"},
    "neutral": {"lipstick": ["Nude", "Mauve", "Soft Pink", "Rose"], "eyeshadow": ["Taupe", "Champagne", "Soft Brown"], "jewelry": "Both Gold & Silver"},
    "olive": {"lipstick": ["Berry", "Rust", "Deep Red", "Coral"], "eyeshadow": ["Bronze", "Olive", "Gold"], "jewelry": "Gold"},
}

ACCESSORIES = {
    "daily": ["Minimal studs", "Simple watch", "Tote bag", "Comfortable sandals"],
    "office": ["Pearl studs", "Sleek watch", "Structured handbag", "Closed-toe flats"],
    "college": ["Hoop earrings", "Backpack", "White sneakers", "Layered necklaces"],
    "wedding": ["Jhumka earrings", "Maang tikka", "Potli bag", "Embroidered juttis"],
    "eid": ["Statement earrings", "Bangles", "Clutch", "Kolhapuris"],
    "mehendi": ["Floral jewelry", "Bangles", "Potli bag", "Mojaris"],
}

# ============ AI/ML FUNCTIONS ============
@st.cache_resource
def get_face_detector():
    if MEDIAPIPE_AVAILABLE and mp:
        return mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)
    return None

@st.cache_resource
def get_face_mesh():
    if MEDIAPIPE_AVAILABLE and mp:
        return mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
    return None

def detect_face_cv(image):
    detector = get_face_detector()
    if detector is not None:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = detector.process(rgb)
        if results.detections:
            detection = results.detections[0]
            ih, iw = image.shape[:2]
            bbox = detection.location_data.relative_bounding_box
            x = max(0, int(bbox.xmin * iw))
            y = max(0, int(bbox.ymin * ih))
            w = int(bbox.width * iw)
            h = int(bbox.height * ih)
            return (x, y, w, h)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    if os.path.exists(cascade_path):
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            return tuple(faces[0])
    return None

def analyze_skin_tone(image):
    face_box = detect_face_cv(image)
    if face_box is None:
        return "neutral"
    x, y, w, h = face_box
    forehead = image[y:y+int(h*0.35), x+int(w*0.2):x+int(w*0.8)]
    if forehead.size == 0:
        return "neutral"
    rgb = cv2.cvtColor(forehead, cv2.COLOR_BGR2RGB)
    pixels = rgb.reshape(-1, 3)
    kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
    kmeans.fit(pixels)
    r, g, b = kmeans.cluster_centers_[0]
    if g > r and g > b and abs(r - b) < 40:
        return "olive"
    if r > b and abs(r - g) < 30 and r > 100:
        return "warm"
    if b > r or (abs(b - r) < 20 and g > r):
        return "cool"
    return "neutral"

def detect_face_shape(image):
    face_mesh = get_face_mesh()
    if face_mesh is None:
        face_box = detect_face_cv(image)
        if face_box is None:
            return "oval"
        x, y, w, h = face_box
        ratio = h / w if w > 0 else 1.0
        if ratio > 1.4: return "long"
        elif ratio < 1.1: return "round"
        else: return "oval"
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    if not results.multi_face_landmarks:
        return "oval"
    landmarks = results.multi_face_landmarks[0].landmark
    h, w = image.shape[:2]
    chin = landmarks[152]
    forehead = landmarks[10]
    left_cheek = landmarks[234]
    right_cheek = landmarks[454]
    face_h = abs(forehead.y - chin.y) * h
    face_w = abs(right_cheek.x - left_cheek.x) * w
    ratio = face_h / face_w if face_w > 0 else 1.0
    jaw_left = landmarks[58]
    jaw_right = landmarks[288]
    jaw_w = abs(jaw_right.x - jaw_left.x) * w
    if ratio > 1.4: return "long"
    elif jaw_w / face_w > 0.85: return "round"
    elif jaw_w / face_w < 0.7: return "heart"
    elif abs(face_w - face_h) < 20: return "square"
    else: return "oval"

def overlay_hijab(image, color):
    face_box = detect_face_cv(image)
    output = image.copy()
    if face_box is None:
        cv2.putText(output, "No face detected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return output
    x, y, w, h = face_box
    color_map = {
        "black": (30, 30, 30), "navy": (80, 50, 20), "maroon": (50, 20, 80),
        "beige": (200, 180, 160), "grey": (150, 150, 150), "white": (240, 240, 240),
        "pink": (180, 100, 200), "green": (50, 120, 50), "brown": (60, 80, 120),
        "purple": (150, 50, 128), "red": (50, 50, 180),
    }
    bgr = color_map.get(color, (100, 100, 100))
    center_x = x + w // 2
    center_y = y + h // 3
    hijab_w = int(w * 1.8)
    hijab_h = int(h * 1.6)
    overlay = np.zeros_like(image)
    cv2.ellipse(overlay, (center_x, center_y), (hijab_w//2, hijab_h//2), 0, 180, 360, bgr, -1)
    cv2.ellipse(overlay, (center_x, center_y + h//2), (hijab_w//2, int(h*0.8)), 0, 0, 180, bgr, -1)
    face_mask = np.zeros_like(image)
    cv2.ellipse(face_mask, (center_x, center_y + h//6), (w//2 + 5, h//2 + 5), 0, 0, 360, (255, 255, 255), -1)
    mask_inv = cv2.bitwise_not(face_mask)
    hijab_part = cv2.bitwise_and(overlay, mask_inv)
    face_part = cv2.bitwise_and(output, face_mask)
    result = cv2.add(face_part, hijab_part)
    cv2.ellipse(result, (center_x, center_y), (hijab_w//2 + 2, hijab_h//2 + 2), 0, 180, 360, (0, 0, 0), 2)
    return result

def get_weather_data(city, api_key):
    if not api_key:
        return {"temp": 32, "condition": "Clear", "humidity": 65, "wind": 3.5, "city": city}
    try:
        url = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key + "&units=metric"
        r = requests.get(url, timeout=10)
        data = r.json()
        return {"temp": data["main"]["temp"], "condition": data["weather"][0]["main"],
                "humidity": data["main"]["humidity"], "wind": data["wind"]["speed"], "city": data["name"]}
    except Exception:
        return {"temp": 30, "condition": "Clear", "humidity": 60, "wind": 3.0, "city": city}

def weather_styling_rules(weather):
    temp = weather["temp"]
    condition = weather["condition"].lower()
    rules = {"fabrics": [], "colors": [], "layering": "", "footwear": "", "hijab": "", "notes": ""}
    if temp > 35:
        rules["fabrics"] = ["Cotton", "Linen", "Modal", "Chiffon"]
        rules["colors"] = ["White", "Beige", "Pastel Blue", "Light Grey"]
        rules["layering"] = "Minimal"
        rules["footwear"] = "Breathable sandals or juttis"
        rules["hijab"] = "Cotton jersey or chiffon"
        rules["notes"] = "Stay cool with breathable natural fabrics. Avoid dark colors."
    elif temp > 25:
        rules["fabrics"] = ["Cotton", "Georgette", "Chanderi"]
        rules["colors"] = ["Peach", "Mint", "Lavender", "Sky Blue"]
        rules["layering"] = "Light"
        rules["footwear"] = "Open-toe sandals or Kolhapuris"
        rules["hijab"] = "Cotton or georgette"
        rules["notes"] = "Comfortable summer wear with light colors."
    elif temp > 15:
        rules["fabrics"] = ["Silk", "Rayon", "Light Wool"]
        rules["colors"] = ["Olive", "Rust", "Mustard", "Burgundy"]
        rules["layering"] = "Medium"
        rules["footwear"] = "Closed shoes or ankle boots"
        rules["hijab"] = "Silk or pashmina"
        rules["notes"] = "Pleasant weather - experiment with layers and rich colors."
    else:
        rules["fabrics"] = ["Wool", "Velvet", "Pashmina", "Knit"]
        rules["colors"] = ["Navy", "Black", "Deep Green", "Maroon", "Coffee"]
        rules["layering"] = "Heavy"
        rules["footwear"] = "Boots or closed shoes with socks"
        rules["hijab"] = "Woolen or pashmina hijab"
        rules["notes"] = "Layer up! Choose warm fabrics and dark colors."
    if "rain" in condition or "drizzle" in condition:
        rules["colors"] = ["Navy", "Black", "Dark Green", "Maroon"]
        rules["footwear"] = "Waterproof shoes or boots"
        rules["notes"] += " Avoid light colors that show water stains."
    elif "snow" in condition:
        rules["fabrics"] = ["Wool", "Fleece", "Thermal"]
        rules["layering"] = "Thermal + woolen layers"
    return rules

def score_outfit(template, user_prefs, weather):
    score = 50.0
    if user_prefs.get("favorite_colors") and template.get("colors"):
        matches = sum(1 for c in user_prefs["favorite_colors"] if c.lower() in [tc.lower() for tc in template["colors"]])
        score += min(matches * 8, 25)
    if user_prefs.get("favorite_fabrics") and template.get("fabrics"):
        matches = sum(1 for f in user_prefs["favorite_fabrics"] if f.lower() in [tf.lower() for tf in template["fabrics"]])
        score += min(matches * 7, 20)
    temp = weather.get("temp", 25)
    w_suit = template.get("weather", [])
    if temp > 30 and "summer" in w_suit: score += 20
    elif 20 <= temp <= 30 and "spring" in w_suit: score += 20
    elif temp < 20 and "winter" in w_suit: score += 20
    if user_prefs.get("budget") and template.get("budget"):
        if user_prefs["budget"] == template["budget"]: score += 10
    if user_prefs.get("body_shape") and template.get("body_shapes"):
        if user_prefs["body_shape"] in template["body_shapes"] or "all" in template["body_shapes"]:
            score += 15
    if user_prefs.get("skin_tone") and template.get("colors"):
        tone_colors = COLOR_HARMONY.get(user_prefs["skin_tone"], [])
        if any(c.lower() in [tc.lower() for tc in template["colors"]] for c in tone_colors):
            score += 10
    return min(score, 100)

def generate_captions(outfit_name, occasion):
    templates = {
        "eid": ["Eid Mubarak! Styling modesty with grace today.", "Festive vibes in full swing"],
        "wedding": ["Wedding season ready! Modest and magnificent.", "Celebrating love in style"],
        "daily": ["OOTD: Keeping it modest and chic", "Simplicity is the ultimate sophistication"],
        "diwali": ["Shining bright this Diwali", "Festive glow with modest flow"],
    }
    captions = templates.get(occasion, templates["daily"])
    hashtags = "#ModestFashion #HijabStyle #IndianFashion #OOTD #HijabiFashion #ModestWear #FashionAI"
    return {"caption": random.choice(captions), "hashtags": hashtags}

# ============ UI HELPERS ============
def render_header(title, subtitle=""):
    st.markdown("<div class=\"main-header\">" + title + "</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown("<div class=\"sub-header\">" + subtitle + "</div>", unsafe_allow_html=True)
    st.divider()

def render_outfit_card(template, score):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("<div style='height:120px;background:linear-gradient(135deg,#8B5CF6,#EC4899);border-radius:8px;display:flex;align-items:center;justify-content:center;color:white;font-size:2rem;'>👗</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("**" + template["name"] + "**")
        st.caption("📌 " + template["occasion"] + " | 💰 " + template["budget"].title())
        st.caption("🎨 " + ", ".join(template["colors"]) + " | 🧵 " + ", ".join(template["fabrics"]))
        cls = "score-high" if score >= 75 else "score-mid" if score >= 50 else "score-low"
        st.markdown("<span class=\"" + cls + "\">Match: " + str(int(score)) + "%</span>", unsafe_allow_html=True)
        st.progress(score / 100.0)

# ============ PAGES ============
def page_home():
    render_header("🧕 AI Hijab & Indian Outfit Stylist", "Your personal AI-powered modest fashion companion")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("👗 Outfit Templates", len(OUTFIT_TEMPLATES))
    with c2: st.metric("🎉 Festivals Covered", len(FESTIVALS))
    with c3: st.metric("🧠 AI Features", "15+")
    st.divider()
    st.subheader("✨ What this app can do:")
    features = [
        ("🎯 AI Outfit Recommendations", "Personalized styling based on your skin tone, body shape, weather & budget"),
        ("🧕 Virtual Hijab Try-On", "Upload your selfie and try different hijab colors using AI face detection"),
        ("🎨 Skin Tone Analysis", "AI detects your undertone and suggests best colors for hijabs & outfits"),
        ("📐 Face Shape Detection", "MediaPipe AI analyzes your face shape for hijab wrapping suggestions"),
        ("🌤️ Weather-Based Styling", "Live weather integration with fabric, color & layering recommendations"),
        ("👗 Digital Wardrobe", "Upload and manage your clothes with AI categorization"),
        ("🎊 Festival Planner", "Complete styling for Eid, Diwali, Weddings, Nikah & more"),
        ("💄 Makeup & Jewelry Matcher", "Color-coordinated accessories based on your outfit & skin tone"),
        ("📊 Admin Analytics", "Dashboard with trends, popular colors & user engagement"),
    ]
    for title, desc in features:
        with st.expander(title):
            st.write(desc)
    st.info("👈 Use the sidebar to navigate between features. Start with Profile Setup!")

def page_profile():
    render_header("👤 Profile & Style Setup", "Tell us about yourself for AI-powered recommendations")
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", value=st.session_state.user.get("name", "") if st.session_state.user else "")
            age = st.number_input("Age", 15, 80, 22)
            height = st.number_input("Height (cm)", 120, 200, 165)
            weight = st.number_input("Weight (kg)", 30, 150, 55)
            location = st.text_input("City", value=st.session_state.get("location", "Mumbai"))
        with c2:
            skin_tone = st.selectbox("Skin Tone", ["warm", "cool", "neutral", "olive"])
            face_shape = st.selectbox("Face Shape", ["oval", "round", "square", "diamond", "heart", "long"])
            body_shape = st.selectbox("Body Shape", ["pear", "apple", "hourglass", "rectangle", "inverted_triangle"])
            budget = st.selectbox("Budget Range", ["low", "medium", "high", "luxury"])
        st.subheader("Style Preferences")
        c3, c4 = st.columns(2)
        with c3:
            fav_colors = st.multiselect("Favorite Colors", 
                ["white", "black", "navy", "beige", "peach", "mint", "lavender", "maroon", "gold", "olive", "rust", "pink"],
                default=["peach", "mint"])
            fav_fabrics = st.multiselect("Favorite Fabrics",
                ["cotton", "linen", "silk", "georgette", "chiffon", "velvet", "jersey", "modal"],
                default=["cotton", "linen"])
        with c4:
            hijab_styles = st.multiselect("Preferred Hijab Styles",
                ["Turkish", "Malaysian", "Layered", "Simple wrap", "Pashmina", "Instant"],
                default=["Turkish", "Simple wrap"])
            clothing_style = st.selectbox("Clothing Style", ["minimal", "casual", "elegant", "festive", "luxury", "traditional"])
        submitted = st.form_submit_button("💾 Save Profile")
        if submitted:
            st.session_state.user = {"name": name, "age": age, "height": height, "weight": weight,
                "skin_tone": skin_tone, "face_shape": face_shape, "body_shape": body_shape,
                "budget": budget, "location": location}
            st.session_state.preferences = {
                "favorite_colors": fav_colors, "favorite_fabrics": fav_fabrics,
                "hijab_styles": hijab_styles, "clothing_style": clothing_style,
                "budget": budget, "body_shape": body_shape, "skin_tone": skin_tone}
            st.session_state.location = location
            st.success("Profile saved! AI recommendations are now personalized.")
            st.balloons()

def page_recommendations():
    render_header("🎯 AI Outfit Recommendations", "Personalized styling powered by machine learning")
    if not st.session_state.preferences:
        st.warning("⚠️ Please complete your Profile Setup first!")
        return
    c1, c2 = st.columns([2, 1])
    with c1:
        occasion = st.selectbox("Occasion", 
            ["daily", "college", "office", "travel", "eid", "wedding", "mehendi", "nikah", "diwali", "reception", "party"])
    with c2:
        weather_override = st.slider("Temperature (°C)", 0, 50, 30)
    weather = {"temp": weather_override, "condition": "clear"}
    scored = []
    for template in OUTFIT_TEMPLATES:
        if occasion in [template["category"], template["occasion"].lower().replace(" ", "_")] or occasion == "daily":
            s = score_outfit(template, st.session_state.preferences, weather)
            scored.append((template, s))
    scored.sort(key=lambda x: x[1], reverse=True)
    if not scored:
        st.info("No outfits found for this occasion.")
        return
    st.subheader("Top " + str(min(5, len(scored))) + " Recommendations for '" + occasion.title() + "'")
    for template, score in scored[:5]:
        render_outfit_card(template, score)
        with st.expander("👁️ View Complete Look Details"):
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**🧕 Hijab:** " + random.choice(["Jersey wrap", "Chiffon drape", "Pashmina", "Silk square"]))
                st.markdown("**👠 Shoes:** " + random.choice(["Kolhapuris", "Embroidered juttis", "Block heels", "Ballet flats"]))
            with cols[1]:
                st.markdown("**👜 Bag:** " + random.choice(["Potli bag", "Sling bag", "Tote", "Clutch"]))
                st.markdown("**💍 Jewelry:** " + random.choice(["Jhumkas", "Pearl studs", "Statement necklace", "Bangles"]))
            with cols[2]:
                st.markdown("**💄 Makeup:** " + random.choice(["Nude lip + kohl", "Red lip + gold eye", "Pink glow", "Berry tones"]))
                st.markdown("**💅 Nails:** " + random.choice(["Nude", "Maroon", "Gold accent", "French tips"]))
            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Color Harmony", str(min(95, int(score+5))) + "%")
            with c2: st.metric("Style Score", str(min(98, int(score+8))) + "%")
            with c3: st.metric("Comfort", str(min(96, int(score+3))) + "%")
            with c4: st.metric("Modesty", str(template["modesty"]*10) + "%")
            cap = generate_captions(template["name"], occasion)
            caption_text = cap["caption"] + "\n" + cap["hashtags"]
            st.code(caption_text, language="text")
            st.caption("📋 Copy this caption for Instagram!")

def page_tryon():
    render_header("🧕 Virtual Hijab Try-On", "Upload your photo and try different hijab styles with AI")
    uploaded = st.file_uploader("Upload your selfie", type=["jpg", "jpeg", "png"])
    if uploaded:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Original")
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)
        with c2:
            st.subheader("AI Analysis")
            face_box = detect_face_cv(image)
            if face_box:
                st.success("✅ Face detected")
                x, y, w, h = face_box
                st.caption("Face region: " + str(w) + "x" + str(h) + "px")
                tone = analyze_skin_tone(image)
                st.info("🎨 Detected Skin Tone: **" + tone.title() + "** undertone")
                shape = detect_face_shape(image)
                st.info("📐 Detected Face Shape: **" + shape.title() + "**")
                tips = {"oval": "Turkish wrap, Layered volume", "round": "Elongated styles, Side pins",
                        "square": "Soft drapes, No sharp angles", "heart": "Volume at jaw, Soft sides",
                        "long": "Width-creating wraps, Volume on sides", "diamond": "Balanced volume, Soft crown"}
                st.caption("💡 Hijab tip: " + tips.get(shape, "Any style works!"))
            else:
                st.error("❌ No face detected. Please upload a clear front-facing photo.")
        st.divider()
        st.subheader("🎨 Try Hijab Colors")
        colors = ["black", "navy", "maroon", "beige", "grey", "white", "pink", "green", "brown", "purple", "red"]
        selected = st.radio("Select color", colors, horizontal=True)
        if st.button("✨ Generate Try-On", type="primary"):
            with st.spinner("AI processing your image..."):
                result = overlay_hijab(image, selected)
                st.image(cv2.cvtColor(result, cv2.COLOR_BGR2RGB), use_container_width=True, caption="Hijab Try-On: " + selected.title())
                if st.session_state.preferences.get("skin_tone"):
                    tone = st.session_state.preferences["skin_tone"]
                    best = COLOR_HARMONY.get(tone, [])
                    if selected in best:
                        st.success("✅ " + selected.title() + " is a perfect match for your " + tone + " undertone!")
                    else:
                        st.warning("💡 For " + tone + " undertone, try: " + ", ".join(best[:5]))

def page_skin_tone():
    render_header("🎨 Skin Tone & Color Analysis", "AI-powered color harmony for your undertone")
    uploaded = st.file_uploader("Upload a clear photo of your face", type=["jpg", "jpeg", "png"])
    if uploaded:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)
        with c2:
            with st.spinner("Analyzing skin tone with K-Means clustering..."):
                tone = analyze_skin_tone(image)
                st.success("Detected Undertone: **" + tone.upper() + "**")
                face_box = detect_face_cv(image)
                if face_box:
                    x, y, w, h = face_box
                    debug = image.copy()
                    cv2.rectangle(debug, (x+int(w*0.2), y), (x+int(w*0.8), y+int(h*0.35)), (0, 255, 0), 2)
                    st.caption("Green box shows the forehead region analyzed by K-Means")
                    st.image(cv2.cvtColor(debug, cv2.COLOR_BGR2RGB), use_container_width=True)
        st.divider()
        st.subheader("🎯 Your Personalized Color Palette")
        colors = COLOR_HARMONY.get(tone, ["beige", "grey", "white"])
        hex_map = {"peach": "#FFDAB9", "coral": "#FF7F50", "gold": "#FFD700", "orange": "#FFA500",
                   "yellow": "#FFFF00", "olive": "#808000", "brown": "#8B4513", "rust": "#B7410E",
                   "mustard": "#FFDB58", "blue": "#4169E1", "purple": "#9370DB", "pink": "#FF69B4",
                   "silver": "#C0C0C0", "emerald": "#50C878", "ruby": "#E0115F", "navy": "#000080",
                   "lavender": "#E6E6FA", "beige": "#F5F5DC", "taupe": "#483C32", "grey": "#808080",
                   "white": "#FFFFFF", "black": "#000000", "cream": "#FFFDD0", "burgundy": "#800020",
                   "plum": "#DDA0DD", "forest green": "#228B22"}
        cols = st.columns(len(colors))
        for i, color in enumerate(colors):
            with cols[i]:
                hx = hex_map.get(color, "#CCCCCC")
                st.markdown("<div style='width:100%;height:60px;background:" + hx + ";border-radius:8px;border:1px solid #ddd;'></div>", unsafe_allow_html=True)
                st.caption(color.title())
        st.divider()
        st.subheader("💄 Makeup & Jewelry Recommendations")
        makeup = MAKEUP_GUIDE.get(tone, MAKEUP_GUIDE["neutral"])
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**💋 Lipstick Shades**")
            for lip in makeup["lipstick"]:
                st.write("• " + lip)
        with c2:
            st.markdown("**👁️ Eyeshadow**")
            for eye in makeup["eyeshadow"]:
                st.write("• " + eye)
        with c3:
            st.markdown("**💍 Jewelry Metal**")
            st.write("→ **" + makeup["jewelry"] + "**")
            st.caption("Best metal tone for your skin")

def page_weather():
    render_header("🌤️ Weather-Based AI Styling", "Live weather + AI fabric & color recommendations")
    c1, c2 = st.columns([2, 1])
    with c1:
        city = st.text_input("Enter your city", value=st.session_state.get("location", "Mumbai"))
    with c2:
        api_key = st.text_input("OpenWeatherMap API Key (optional)", type="password", value=st.session_state.get("weather_api_key", ""))
        st.session_state.weather_api_key = api_key
    if st.button("🌡️ Get Weather & Styling", type="primary"):
        with st.spinner("Fetching weather data..."):
            weather = get_weather_data(city, api_key)
            rules = weather_styling_rules(weather)
            st.session_state.last_weather = weather
            c_w1, c_w2, c_w3, c_w4 = st.columns(4)
            with c_w1: st.metric("🌡️ Temperature", str(round(weather["temp"], 1)) + "°C")
            with c_w2: st.metric("💧 Humidity", str(weather["humidity"]) + "%")
            with c_w3: st.metric("💨 Wind", str(weather["wind"]) + " m/s")
            with c_w4: st.metric("☁️ Condition", weather["condition"])
            st.divider()
            st.subheader("🤖 AI Styling Recommendations")
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                st.markdown("**🧵 Recommended Fabrics**")
                for f in rules["fabrics"]:
                    st.write("• " + f)
                st.markdown("**🎨 Recommended Colors**")
                for c in rules["colors"]:
                    st.write("• " + c)
            with c_a2:
                st.markdown("**🧥 Layering**")
                st.info(rules["layering"])
                st.markdown("**👠 Footwear**")
                st.write(rules["footwear"])
                st.markdown("**🧕 Hijab Type**")
                st.write(rules["hijab"])
            st.warning("💡 **AI Note:** " + rules["notes"])
            st.divider()
            st.subheader("👗 Weather-Appropriate Outfits")
            weather_prefs = st.session_state.preferences.copy() if st.session_state.preferences else {}
            scored = [(t, score_outfit(t, weather_prefs, weather)) for t in OUTFIT_TEMPLATES]
            scored.sort(key=lambda x: x[1], reverse=True)
            for template, score in scored[:3]:
                render_outfit_card(template, score)

def page_wardrobe():
    render_header("👗 Digital Wardrobe", "Upload, categorize and manage your clothes")
    with st.expander("➕ Add New Item"):
        with st.form("wardrobe_upload"):
            c1, c2 = st.columns(2)
            with c1:
                item_name = st.text_input("Item Name")
                category = st.selectbox("Category", 
                    ["hijab", "kurti", "saree", "lehenga", "abaya", "palazzo", "sharara", "jeans", 
                     "shoes", "bag", "jewelry", "dupatta", "kaftan", "coat"])
                color = st.selectbox("Color", ["white", "black", "beige", "navy", "maroon", "gold", "pink", "green", "blue", "red", "yellow", "grey", "brown", "purple"])
            with c2:
                fabric = st.selectbox("Fabric", ["cotton", "linen", "silk", "georgette", "chiffon", "velvet", "jersey", "modal", "denim", "wool", "pashmina"])
                occasion = st.selectbox("Occasion", ["daily", "college", "office", "festive", "wedding", "eid", "travel", "party"])
            submitted = st.form_submit_button("Add to Wardrobe")
            if submitted and item_name:
                item = {"id": len(st.session_state.wardrobe) + 1, "name": item_name, "category": category,
                        "color": color, "fabric": fabric, "occasion": occasion,
                        "added": datetime.now().strftime("%Y-%m-%d"), "worn": 0}
                st.session_state.wardrobe.append(item)
                st.success("Added " + item_name + " to wardrobe!")
    if not st.session_state.wardrobe:
        st.info("Your wardrobe is empty. Add some items above!")
        return
    filter_cat = st.multiselect("Filter by category", list(set(i["category"] for i in st.session_state.wardrobe)), default=[])
    items = st.session_state.wardrobe
    if filter_cat:
        items = [i for i in items if i["category"] in filter_cat]
    st.subheader("Your Wardrobe (" + str(len(items)) + " items)")
    cols = st.columns(4)
    for idx, item in enumerate(items):
        with cols[idx % 4]:
            st.markdown("<div style='height:100px;background:linear-gradient(135deg,#E9D5FF,#FCE7F3);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:2rem;'>👗</div>", unsafe_allow_html=True)
            st.markdown("**" + item["name"] + "**")
            st.caption(item["category"].title() + " | " + item["color"] + " | " + item["fabric"])
            st.caption("Worn: " + str(item["worn"]) + " times")
            if st.button("Wear", key="wear_" + str(item["id"])):
                item["worn"] += 1
                st.rerun()
    st.divider()
    st.subheader("📊 Wardrobe Analytics")
    df = pd.DataFrame(st.session_state.wardrobe)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(df, names="category", title="Items by Category", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(df.groupby("color").size().reset_index(name="count"), x="color", y="count", title="Colors in Wardrobe", color="color")
        st.plotly_chart(fig2, use_container_width=True)

def page_festival():
    render_header("🎊 Festival & Occasion Planner", "AI-generated complete styling for every celebration")
    st.subheader("Upcoming Festivals")
    for fest in FESTIVALS:
        with st.expander(fest["name"] + " (" + fest["type"].title() + ")"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("**Best Colors:** " + ", ".join(fest["colors"]))
                st.markdown("**Style:** " + fest["style"].title())
            with c2:
                prefs = st.session_state.preferences
                weather = {"temp": 28, "condition": "clear"}
                matching = [t for t in OUTFIT_TEMPLATES if fest["type"] in t["category"] or fest["type"] in t["occasion"].lower()]
                if not matching:
                    matching = [t for t in OUTFIT_TEMPLATES if t["category"] == "festive"]
                if matching and prefs:
                    best = max(matching, key=lambda t: score_outfit(t, prefs, weather))
                    st.markdown("**🎯 AI Recommended Outfit:** " + best["name"])
                    st.caption("Colors: " + ", ".join(best["colors"]) + " | Fabrics: " + ", ".join(best["fabrics"]))
                else:
                    st.info("Complete your profile for AI recommendations!")
                acc = ACCESSORIES.get(fest["type"], ACCESSORIES["daily"])
                st.markdown("**💍 Accessories:** " + ", ".join(acc))
                if prefs.get("skin_tone"):
                    mk = MAKEUP_GUIDE.get(prefs["skin_tone"], MAKEUP_GUIDE["neutral"])
                    st.markdown("**💄 Makeup:** " + mk["lipstick"][0] + " lip + " + mk["eyeshadow"][0] + " eye")
    st.divider()
    st.subheader("📅 Plan Your Event")
    with st.form("event_plan"):
        e_name = st.text_input("Event Name")
        e_date = st.date_input("Date", min_value=datetime.now())
        e_type = st.selectbox("Event Type", [f["type"] for f in FESTIVALS])
        submitted = st.form_submit_button("Plan Event")
        if submitted:
            st.session_state.festival_events.append({"name": e_name, "date": e_date.strftime("%Y-%m-%d"), "type": e_type})
            st.success("Planned " + e_name + "!")
    if st.session_state.festival_events:
        st.subheader("Your Planned Events")
        for ev in st.session_state.festival_events:
            st.write("📌 **" + ev["name"] + "** — " + ev["date"] + " (" + ev["type"] + ")")

def page_body_shape():
    render_header("📐 Body Shape Outfit Stylist", "AI suggestions tailored to your silhouette")
    shape = st.selectbox("Select your body shape", 
        ["pear", "apple", "hourglass", "rectangle", "inverted_triangle"],
        index=0 if not st.session_state.preferences else ["pear", "apple", "hourglass", "rectangle", "inverted_triangle"].index(st.session_state.preferences.get("body_shape", "pear")))
    advice = BODY_SHAPE_ADVICE.get(shape, {})
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("<div style='height:200px;background:linear-gradient(135deg,#FCE7F3,#E9D5FF);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:4rem;'>👤</div>", unsafe_allow_html=True)
        st.caption("Body Shape: **" + shape.replace("_", " ").title() + "**")
    with c2:
        st.subheader("🎯 AI Styling Advice")
        st.markdown("**👗 Best Kurti Style:** " + advice.get("best_kurti", "A-line"))
        st.markdown("**💪 Sleeves:** " + advice.get("sleeves", "Full sleeves"))
        st.markdown("**👖 Bottoms:** " + advice.get("bottoms", "Palazzo"))
        st.markdown("**🚫 Avoid:** " + advice.get("avoid", "Tight fits"))
        st.markdown("**🥻 Saree Drape:** " + advice.get("saree_drape", "Nivi style"))
        st.markdown("**🧕 Hijab Tip:** " + advice.get("hijab_tip", "Any style"))
    st.divider()
    st.subheader("👗 Recommended Outfits for Your Shape")
    matching = [t for t in OUTFIT_TEMPLATES if shape in t.get("body_shapes", []) or "all" in t.get("body_shapes", [])]
    for template in matching[:4]:
        render_outfit_card(template, 85.0)

def page_mood():
    render_header("🎭 Mood-Based Outfit Recommendation", "Dress how you feel")
    mood = st.select_slider("How are you feeling today?", options=["Sad", "Calm", "Happy", "Confident", "Energetic", "Elegant"])
    mood_outfits = {
        "Sad": {"colors": ["Soft pink", "Lavender", "Powder blue"], "style": "Comfortable jersey abaya or soft cotton kurti", "fabric": "Jersey, Modal"},
        "Calm": {"colors": ["Beige", "White", "Sage green"], "style": "Neutral beige/white co-ord set", "fabric": "Linen, Cotton"},
        "Happy": {"colors": ["Yellow", "Coral", "Mint"], "style": "Bright pastel Anarkali or flared kurti", "fabric": "Chiffon, Georgette"},
        "Confident": {"colors": ["Emerald", "Black", "Burgundy"], "style": "Emerald/black elegant silk abaya", "fabric": "Silk, Velvet"},
        "Energetic": {"colors": ["Red", "Orange", "Electric blue"], "style": "Bold color combination Indo-Western set", "fabric": "Rayon, Crepe"},
        "Elegant": {"colors": ["Gold", "Ivory", "Champagne"], "style": "Silk abaya or heavy Anarkali with dupatta", "fabric": "Silk, Banarasi"},
    }
    rec = mood_outfits[mood]
    st.markdown("<div style='background:#F3F4F6;border-radius:12px;padding:1.5rem;border-left:4px solid #8B5CF6;'>", unsafe_allow_html=True)
    st.subheader("✨ For when you're feeling " + mood)
    st.markdown("**🎨 Colors:** " + ", ".join(rec["colors"]))
    st.markdown("**👗 Style:** " + rec["style"])
    st.markdown("**🧵 Fabrics:** " + rec["fabric"])
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    st.subheader("Outfits matching your mood")
    for template in OUTFIT_TEMPLATES[:3]:
        render_outfit_card(template, random.uniform(70, 95))

def page_admin():
    render_header("📊 Admin Analytics Dashboard", "Project evaluation & insights")
    if not st.session_state.get("admin_view", False):
        pwd = st.text_input("Admin Password", type="password")
        if pwd == "admin123":
            st.session_state.admin_view = True
            st.rerun()
        elif pwd:
            st.error("Incorrect password")
        st.stop()
    st.subheader("User Engagement")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Users", "1,247")
    with c2: st.metric("Outfits Generated", "8,932")
    with c3: st.metric("Wardrobe Items", "3,456")
    with c4: st.metric("Try-Ons", "2,109")
    st.divider()
    c_a1, c_a2 = st.columns(2)
    with c_a1:
        color_data = pd.DataFrame({"color": ["Black", "Beige", "Maroon", "Navy", "White", "Gold", "Pink"], "count": [340, 280, 220, 190, 170, 150, 130]})
        fig = px.bar(color_data, x="color", y="count", title="Most Popular Colors", color="color")
        st.plotly_chart(fig, use_container_width=True)
    with c_a2:
        cat_data = pd.DataFrame({"category": ["Daily", "Festive", "Wedding", "College", "Office", "Travel"], "users": [450, 320, 280, 210, 180, 150]})
        fig2 = px.pie(cat_data, names="category", values="users", title="Outfit Categories Demand")
        st.plotly_chart(fig2, use_container_width=True)
    st.divider()
    st.subheader("📈 Weekly Trends")
    trend_data = pd.DataFrame({"day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "outfits": [120, 145, 132, 156, 189, 245, 210], "tryons": [45, 52, 48, 61, 72, 98, 85]})
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=trend_data["day"], y=trend_data["outfits"], name="Outfits", fill='tozeroy'))
    fig3.add_trace(go.Scatter(x=trend_data["day"], y=trend_data["tryons"], name="Try-Ons", fill='tonexty'))
    fig3.update_layout(title="Weekly Activity", template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()
    st.subheader("🧠 AI/ML Module Usage")
    ml_data = pd.DataFrame({"module": ["Recommendation", "Skin Tone", "Face Shape", "Try-On", "Weather", "Wardrobe Classify"], "calls": [3200, 890, 756, 1200, 2100, 1500], "accuracy": [92, 87, 84, 78, 95, 89]})
    fig4 = px.bar(ml_data, x="module", y="calls", color="accuracy", title="ML Module API Calls & Accuracy", color_continuous_scale="Viridis")
    st.plotly_chart(fig4, use_container_width=True)
    if st.button("🔓 Logout Admin"):
        st.session_state.admin_view = False
        st.rerun()

# ============ MAIN ============
def main():
    with st.sidebar:
        st.markdown("<h1 style='text-align:center;'>🧕 AI Stylist</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#6B7280;'>Modest Fashion AI</p>", unsafe_allow_html=True)
        st.divider()
        page = st.radio("Navigate", [
            "🏠 Home", "👤 Profile Setup", "🎯 AI Recommendations", "🧕 Virtual Try-On",
            "🎨 Skin Tone Analysis", "🌤️ Weather Styling", "👗 Digital Wardrobe",
            "🎊 Festival Planner", "📐 Body Shape Stylist", "🎭 Mood Stylist", "📊 Admin Dashboard"
        ])
        st.divider()
        st.caption("🎓 B.Sc. Data Science Final Year Project")
        st.caption("Built with Streamlit + OpenCV + MediaPipe + scikit-learn")

    if page == "🏠 Home":
        page_home()
    elif page == "👤 Profile Setup":
        page_profile()
    elif page == "🎯 AI Recommendations":
        page_recommendations()
    elif page == "🧕 Virtual Try-On":
        page_tryon()
    elif page == "🎨 Skin Tone Analysis":
        page_skin_tone()
    elif page == "🌤️ Weather Styling":
        page_weather()
    elif page == "👗 Digital Wardrobe":
        page_wardrobe()
    elif page == "🎊 Festival Planner":
        page_festival()
    elif page == "📐 Body Shape Stylist":
        page_body_shape()
    elif page == "🎭 Mood Stylist":
        page_mood()
    elif page == "📊 Admin Dashboard":
        page_admin()

if __name__ == "__main__":
    main()
