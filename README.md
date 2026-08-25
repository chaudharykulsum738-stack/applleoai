🧕 AI Hijab & Indian Outfit Stylist — Streamlit App
A complete AI-powered modest fashion recommendation platform built with Streamlit, OpenCV, MediaPipe, and scikit-learn.
🎓 Perfect For
•B.Sc. Data Science Final Year Project
•AI/ML Portfolio Demonstration
•Modest Fashion Tech Startup MVP
✨ Features (15+ AI Modules)
#	Feature	AI/ML Technology
1	AI Outfit Recommendations	Content-Based Filtering + Rule Engine
2	Virtual Hijab Try-On	OpenCV Alpha Blending + MediaPipe Face Detection
3	Skin Tone Analysis	K-Means Clustering on Forehead Region
4	Face Shape Detection	MediaPipe Face Mesh + Geometric Analysis
5	Weather-Based Styling	OpenWeatherMap API + Rule-Based ML
6	Digital Wardrobe	Session-based Inventory + Analytics
7	Festival Planner	Occasion-Aware Recommendation Engine
8	Body Shape Stylist	Rule-Based Expert System
9	Mood-Based Styling	Sentiment-to-Fashion Mapping
10	Makeup & Jewelry Matcher	Color Harmony Theory
11	Instagram Caption Generator	Template-based NLP
12	Admin Analytics Dashboard	Plotly Interactive Charts
13	Outfit Scoring System	Multi-Attribute Weighted Scoring
14	Capsule Wardrobe Generator	Combinatorial Optimization
15	Regional Fashion Explorer	Knowledge Base
🚀 Quick Start
1. Install Dependencies
pip install -r requirements.txt
2. Run the App
streamlit run app.py
3. Open in Browser
The app will open automatically at http://localhost:8501
📁 Project Structure
hijab-stylist-streamlit/
├── app.py              # Main Streamlit application (all features)
├── requirements.txt    # Python dependencies
└── README.md           # This file
🔧 Configuration
OpenWeatherMap API (Optional)
For live weather data, add your API key in the Weather Styling page: 1. Get free API key from openweathermap.org 2. Paste it in the app sidebar field
Admin Dashboard
•Password: admin123
•View user engagement, popular colors, ML module accuracy
🧠 AI/ML Architecture
User Input (Photo/Preferences/Location)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│  MediaPipe      │  OpenCV         │  scikit-learn   │
│  Face Detection │  Image Overlay  │  K-Means        │
│  Face Mesh      │  Alpha Blend    │  Clustering     │
└─────────────────┴─────────────────┴─────────────────┘
    ↓
Recommendation Engine (Weighted Scoring)
    ↓
Personalized Outfit + Makeup + Accessories
📊 Scoring Algorithm
The AI recommendation engine scores outfits on: - Color Preference Match (0-25 pts) - Fabric Preference Match (0-20 pts) - Weather Suitability (0-20 pts) - Budget Match (0-10 pts) - Body Shape Match (0-15 pts) - Skin Tone Harmony (0-10 pts)
Base Score: 50 → Max Score: 100
🎨 Color Theory
Skin Tone	Best Hijab Colors	Best Metals
Warm	Peach, Coral, Gold, Olive	Gold
Cool	Blue, Purple, Pink, Silver	Silver/Rose Gold
Neutral	Beige, Taupe, Grey, White	Both
Olive	Burgundy, Plum, Forest Green	Gold
🌦️ Weather Rules
Temperature	Fabrics	Colors	Layering
>35°C	Cotton, Linen, Modal	White, Beige, Pastel	Minimal
25-35°C	Cotton, Georgette, Chanderi	Peach, Mint, Lavender	Light
15-25°C	Silk, Rayon, Light Wool	Olive, Rust, Mustard	Medium
<15°C	Wool, Velvet, Pashmina	Navy, Black, Maroon	Heavy
🚀 Deployment
Streamlit Cloud (Free)
1.Push code to GitHub
2.Connect repo at share.streamlit.io
3.App deploys automatically
Docker
docker build -t hijab-stylist .
docker run -p 8501:8501 hijab-stylist
📸 Screenshots
The app includes: - 🏠 Home — Feature overview with metrics - 👤 Profile Setup — Age, body shape, skin tone, style preferences - 🎯 AI Recommendations — Scored outfit cards with complete look details - 🧕 Virtual Try-On — Upload selfie + AI hijab overlay with color matching - 🎨 Skin Tone Analysis — K-Means forehead analysis + color palette - 🌤️ Weather Styling — Live weather + fabric/color recommendations - 👗 Digital Wardrobe — Upload items + analytics dashboard - 🎊 Festival Planner — Eid, Diwali, Wedding, Nikah styling - 📐 Body Shape Stylist — Pear, Apple, Hourglass, Rectangle, Inverted Triangle - 🎭 Mood Stylist — Sad, Calm, Happy, Confident, Energetic, Elegant - 📊 Admin Dashboard — Plotly charts, ML module accuracy, trends
📝 Citation
If you use this project for academic purposes:
AI Hijab & Indian Outfit Recommendation System
B.Sc. Data Science Final Year Project
Technologies: Python, Streamlit, OpenCV, MediaPipe, scikit-learn, Plotly
📄 License
MIT License — Free for academic and commercial use.
