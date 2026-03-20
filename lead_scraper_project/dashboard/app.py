import streamlit as st
import asyncio
import io
import pandas as pd
import sys
import threading
from pathlib import Path

# Add project root to sys path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.scraper_engine import ScraperEngine
from core.db_manager import DatabaseManager

db = DatabaseManager()

st.set_page_config(
    page_title="LeadScout SaaS", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM SAAS CSS (DARK THEME) ---
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Gradient Header */
    .gradient-text {
        background: linear-gradient(90deg, #00C853 0%, #2196F3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 2.8rem;
        margin-bottom: 0px;
    }
    
    /* KPI Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-size: 1rem !important;
    }
    
    /* Primary Action Button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #00C853 0%, #009624 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        border-radius: 8px;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.3);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 200, 83, 0.5);
    }
    
    /* Custom Card Design */
    .lead-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .lead-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        border-color: #484f58;
    }
    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        display: inline-block;
        margin-bottom: 10px;
    }
    .contact-btn {
        display: inline-block;
        color: white !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 10px;
        text-align: center;
        transition: opacity 0.2s;
    }
    .contact-btn:hover {
        opacity: 0.85;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.title("Target Parameters")
    
    query = st.text_input("Category", "Yoga studios", help="E.g. Dance, Coaching, Gym")
    city = st.text_input("City", "Hyderabad")
    max_results = st.slider("Max Leads limit", 10, 500, 50, step=10)
    
    st.divider()
    run_btn = st.button("🚀 Extract & Analyze", use_container_width=True, type="primary")
    
    st.markdown("---")
    st.caption("⚡ Powered by **India-Adaptive ML Engine**")

# --- MAIN DASHBOARD ---
st.markdown('<h1 class="gradient-text">Lead Intelligence SaaS</h1>', unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; font-size:1.1rem;'>Smart extraction, cleaning, and prioritization for high-value outreach.</p>", unsafe_allow_html=True)

def run_async_scrape(q: str, c: str, m: int):
    """Runs scraper in background thread for Windows compatibility."""
    result_holder = {"df": pd.DataFrame(), "error": None}
    
    def thread_target():
        if sys.platform == 'win32':
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            engine = ScraperEngine()
            df = loop.run_until_complete(engine.execute_search(q, c, m))
            result_holder["df"] = df
        except Exception as e:
            result_holder["error"] = str(e)
        finally:
            loop.close()

    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join()
    return result_holder["df"], result_holder["error"]

# --- EXECUTION ---
if run_btn:
    with st.status("🔍 Deep Intelligence Scan Running...", expanded=True) as status:
        st.write("🤖 Executing Playwright engine...")
        st.write("🧹 Cleaning real-world data (fixing missing/comma strings)...")
        st.write("⚙️ Applying India-Adaptive Scoring algorithms...")
        df, err = run_async_scrape(query, city, max_results)
        
        if err:
            st.error(f"System Error: {err}")
            status.update(label="❌ Analysis Failed", state="error", expanded=False)
        else:
            status.update(label=f"✅ Analysis Complete", state="complete", expanded=False)

# --- DATA FETCH & SMART PRIORITIZATION ---
raw_df = db.get_leads_by_category_city(query, city)

if not raw_df.empty:
    # 1. Sort descending by absolute score
    df = raw_df.sort_values(by='score', ascending=False).reset_index(drop=True)
    
    n = len(df)
    # Define dynamic boundaries (Top 20%, Next 50%, Last 30%)
    hot_limit = max(1, int(n * 0.20))
    potential_limit = hot_limit + max(1, int(n * 0.50))
    
    # Pre-allocate column spaces
    df['ui_priority'] = ""
    df['ui_action'] = ""
    df['ui_color'] = ""

    # 🔥 Hot Leads (0 to hot_limit)
    df.loc[:hot_limit-1, 'ui_priority'] = '🔥 Hot Lead'
    df.loc[:hot_limit-1, 'ui_action'] = 'Contact Immediately'
    df.loc[:hot_limit-1, 'ui_color'] = '#00C853'
    
    # ⚡ Potential Leads (hot_limit to potential_limit)
    if hot_limit < n:
        df.loc[hot_limit:potential_limit-1, 'ui_priority'] = '⚡ Potential Lead'
        df.loc[hot_limit:potential_limit-1, 'ui_action'] = 'Engage Soon'
        df.loc[hot_limit:potential_limit-1, 'ui_color'] = '#FF9800'
    
    # 📌 Explore Leads (potential_limit to end)
    if potential_limit < n:
        df.loc[potential_limit:, 'ui_priority'] = '📌 Explore Lead'
        df.loc[potential_limit:, 'ui_action'] = 'Monitor / Test Outreach'
        df.loc[potential_limit:, 'ui_color'] = '#2196F3'

    # --- KPI CARDS ---
    st.divider()
    high_count = len(df[df['ui_color'] == '#00C853'])
    med_count = len(df[df['ui_color'] == '#FF9800'])
    low_count = len(df[df['ui_color'] == '#2196F3'])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Extracted", n)
    c2.metric("🔥 Hot Leads", high_count)
    c3.metric("⚡ Potential Leads", med_count)
    c4.metric("📌 Explore Leads", low_count)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- TABS ---
    tab1, tab2 = st.tabs(["🚀 Recommended Targets", "🗃️ Global Directory"])
    
    with tab1:
        st.subheader("High-Conversion Recommendations")
        st.markdown("<span style='color:#8b949e;'>These businesses have been mathematically prioritized based on engagement and adaptive market scoring.</span>", unsafe_allow_html=True)
        
        # Display Top portion (Hot + Potential, or just top N)
        top_view_limit = min(n, 20)  # Show top 20 cards
        top_df = df.head(top_view_limit)
        
        # EXPORT TOP BUTTON
        csv_top = top_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Target List (CSV)", csv_top, f"targets_{query}_{city}.csv", "text/csv")
        
        # CARD RENDERER
        for idx, row in top_df.iterrows():
            badge_html = f"<div class='badge' style='background-color:{row['ui_color']}'>{row['ui_priority']} • {row['score']} Score</div>"
            
            # The Card
            with st.container():
                st.markdown(f"""
                <div class="lead-card" style="border-left: 5px solid {row['ui_color']};">
                    {badge_html}
                    <h3 style="margin-top:0; color:white;">{row['name']}</h3>
                    <p style="color:#aaa; font-size:0.95rem; margin: 5px 0;">
                        ⭐ <b>{row['rating']}</b> Ratings &nbsp; | &nbsp; 📝 <b>{row['reviews']}</b> Reviews
                    </p>
                    <p style="color:#2ea043; font-weight:600; margin: 5px 0;">📍 {row['address'] if pd.notna(row['address']) else 'Address Missing'}</p>
                    <div style="margin-top:12px; padding:10px; background:rgba(0,0,0,0.3); border-radius:6px; border-left:3px solid #FFD700;">
                        <span style="color:#aaa; font-size:0.85rem; display:block;">ML Conversion Probability</span>
                        <strong style="color:#FFD700; font-size:1.2rem;">⚡ {row.get('conversion_prob', 'N/A')}%</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # The Details Panel (Inside Expander directly below the card)
                with st.expander("🔍 View Intelligence & Outreach Strategy"):
                    st.markdown(f"**AI Reasoning:** {row['reason']}")
                    st.markdown(f"**Recommended Action:** **{row['ui_action']}**")
                    
                    st.markdown("**1-Click Outreach Message:**")
                    st.code(row['message'], language="text")
                    
                    if pd.notna(row['phone']) and str(row['phone']).strip():
                        # Generates a clickable TEL link styled as a button
                        st.markdown(f"""
                        <a href="tel:{str(row['phone']).split(',')[0].strip()}" class="contact-btn" style="background-color:{row['ui_color']}">
                            📞 Call {str(row['phone']).split(',')[0].strip()}
                        </a>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Phone number protected or unavailable. Try reaching out via their Google Maps profile.")
                    st.write("") # Spacer

    with tab2:
        st.subheader("Global Discovery Pipeline")
        st.dataframe(
            df[['name', 'phone', 'score', 'ui_priority', 'ui_action', 'rating', 'reviews', 'address']],
            use_container_width=True, 
            height=600,
            hide_index=True
        )
        
        csv_all = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Global Pipeline (CSV)", csv_all, f"pipeline_{query}_{city}.csv", "text/csv")
        
else:
    # Empty State Design
    st.markdown("""
    <div style="text-align:center; padding: 50px; background:#161b22; border-radius:12px; border:1px dashed #30363d;">
        <h3 style="color:#8b949e;">No Local Data Indexed</h3>
        <p style="color:#8b949e;">Configure your parameters in the sidebar and click Extract to build your database.</p>
    </div>
    """, unsafe_allow_html=True)
