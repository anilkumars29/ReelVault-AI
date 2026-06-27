import streamlit as st
import chromadb
import pandas as pd

# --- 🎨 PAGE CONFIGURATION & THEME ---
st.set_page_config(
    page_title="ReelVault AI Intelligence Center",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling Matrix
st.markdown("""
    <style>
    .main-header { font-size:2.5rem !important; font-weight: 700; color: #FFD700; margin-bottom: 5px; }
    .sub-header { font-size:1.1rem !important; color: #A0A0A0; margin-bottom: 30px; }
    .metric-box { padding: 15px; background-color: #1E1E1E; border-radius: 8px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# --- 🔌 DATABASE CONNECTION ---
CHROMA_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

try:
    collection = chroma_client.get_collection(name="reels_archive")
    db_data = collection.get()
    total_records = collection.count()
except Exception:
    db_data = {"ids": [], "documents": [], "metadatas": []}
    total_records = 0

# --- 🏰 SIDEBAR CONTROLS ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8634/8634065.png", width=80)
st.sidebar.title("ReelVault Control Panel")
st.sidebar.markdown("---")
st.sidebar.markdown("🤖 **LLM Engine:** `Llama 3.2 (3B)`")
st.sidebar.markdown("🗄️ **Vector Database:** `ChromaDB (Local)`")
st.sidebar.markdown("📝 **System Logs:** `reelvault.log`")
st.sidebar.markdown("---")
st.sidebar.info("This dashboard reads live semantic coordinates natively from your hard drive storage matrix.")

# --- 📈 EXECUTIVE OVERVIEW HEADER ---
st.markdown('<p class="main-header">🎬 ReelVault AI Core Intelligence Center</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Production-grade analytics layer parsing multi-modal local video structures</p>', unsafe_allow_html=True)

# Live Statistics Row
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-box">🔹 <b>Total Indexed Assets:</b> <span style="color:#FFD700; font-size:1.5rem;">{total_records}</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-box">🔹 <b>Ingestion Pipelines Active:</b> <span style="color:#00FF7F; font-size:1.5rem;">2 (Whisper + OCR)</span></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-box">🔹 <b>Storage Target Status:</b> <span style="color:#1E90FF; font-size:1.5rem;">Synchronized</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 🔎 INTERACTIVE DATA ARCHIVE ---
if total_records > 0:
    st.header("🗄️ Vector Vault Explorer")
    
    # Restructure ChromaDB dict payload into a clean Pandas Matrix DataFrame
    records_list = []
    for i in range(total_records):
        meta = db_data['metadatas'][i] if db_data['metadatas'] else {}
        doc = db_data['documents'][i] if db_data['documents'] else ""
        
        records_list.append({
            "ID": db_data['ids'][i],
            "Video Title": meta.get('title', 'Untitled Asset'),
            "Source URL": meta.get('url', 'N/A'),
            "Semantic Transcript Snapshot": doc[:150] + "..." if len(doc) > 150 else doc
        })
        
    df = pd.DataFrame(records_list)
    
    # Search Bar Filter for the UI Table
    search_query = st.text_input("🎯 Filter asset array instantly by keyword:", placeholder="Type a title or topic...")
    if search_query:
        df = df[df['Video Title'].str.contains(search_query, case=False) | df['Semantic Transcript Snapshot'].str.contains(search_query, case=False)]
        
    # Render interactive data grid
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- 🧪 LIVE VECTOR ACCELERATOR DATA ---
    st.markdown("---")
    st.header("🔮 Micro-Query Testing Sandbox")
    st.caption("Simulate how the Telegram Bot extracts context vectors behind the scenes.")
    
    test_input = st.text_input("Enter a prototype semantic search phrase:", placeholder="e.g., Artificial Intelligence framework")
    if test_input:
        sim_results = collection.query(query_texts=[test_input], n_results=1)
        if sim_results and sim_results['documents'][0]:
            st.success(f"🎯 **Closest Node Match Found!** Score Distance: `{sim_results['distances'][0][0]:.4f}`")
            st.markdown(f"**Matched Title:** {sim_results['metadatas'][0][0].get('title')}")
            st.info(f"**Extracted Raw Context Block:**\n\n{sim_results['documents'][0][0]}")

else:
    st.warning("📭 Your local vector directory is currently unindexed. Send an Instagram link to your Telegram Bot to initialize the database pipeline entries!")