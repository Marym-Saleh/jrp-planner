import streamlit as st
import json
import pandas as pd
from fpdf import FPDF
from jrp_solver import Item, JRPInstance, find_optimal_policy, generate_visuals

# --- COLOR PALETTE ---
P_NAVY = "#1d3557"
P_BLUE = "#457b9d"
P_LIGHT = "#a8dadc"
P_BG = "#f1faee"
P_RED = "#e63946"

# --- STYLING ---
st.set_page_config(page_title="JRP Cockpit", page_icon="📦", layout="wide")

st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{ background-color: {P_BG}; }}
    
    /* Bold Titles */
    h1, h2, h3 {{ 
        color: {P_NAVY} !important; 
        font-weight: 800 !important; 
    }}
    
    /* FIX FOR BROWSE FILE READABILITY */
    /* Target the text inside the uploader */
    [data-testid="stFileUploader"] section {{
        background-color: white !important;
        border: 2px dashed {P_BLUE} !important;
        border-radius: 10px;
        color: {P_NAVY} !important;
    }}
    
    /* Target the 'Browse files' button text */
    [data-testid="stFileUploader"] button {{
        color: white !important;
        background-color: {P_BLUE} !important;
        border-radius: 5px;
    }}

    /* Target the uploaded filename text */
    [data-testid="stFileUploaderFileName"] {{
        color: {P_NAVY} !important;
        font-weight: bold !important;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {P_NAVY};
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {{
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid {P_BLUE};
        box-shadow: 4px 4px 15px rgba(0,0,0,0.05);
    }}
    div[data-testid="stMetricValue"] > div {{
        color: {P_NAVY};
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DOWNLOAD HELPERS ---
def create_pdf(instance, T_star, total_cost, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Joint Replenishment Report: {instance.instance_name}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"System T*: {T_star:.5f}", ln=True)
    pdf.cell(0, 10, f"Total Annual Cost: ${total_cost:.2f}", ln=True)
    pdf.ln(5)
    
    # Detailed Table
    pdf.set_font("Arial", 'B', 8)
    cols = df.columns.tolist()
    for col in cols:
        pdf.cell(32, 10, str(col), 1)
    pdf.ln()
    
    pdf.set_font("Arial", size=8)
    for row in df.values:
        for val in row:
            pdf.cell(32, 10, str(val), 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"# **Control Center** ⚙️")
    st.image("https://cdn-icons-png.flaticon.com/512/1541/1541415.png", width=80)
    uploaded_file = st.file_uploader("📤 **Upload JSON Data**", type=['json'])
    st.markdown("---")
    st.write("This tool optimizes **Coordinated Replenishment** to minimize setup and holding costs.")

# --- MAIN UI ---
st.markdown(f"<h1 style='text-align: center;'>📦 **Joint Replenishment Planning Cockpit**</h1>", unsafe_allow_html=True)

if uploaded_file:
    # 1. Logic
    data = json.load(uploaded_file)
    items = [Item(i['id'], i['a'], i['D'], i['v']) for i in data['items']]
    instance = JRPInstance(data.get('instance_name', 'Inventory_Batch'), data['A'], data['r'], items)
    T_star, total_cost, results = find_optimal_policy(instance)
    df = pd.DataFrame(results)

    # 2. Metrics
    st.markdown("### **System Results**")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Optimal T*", f"{T_star:.5f}")
    m2.metric("Total System Cost", f"${total_cost:,.2f}")
    m3.metric("Major Setup (A)", f"${instance.A}")
    m4.metric("Holding Charge (r)", f"{instance.r*100:.0f}%")

    # 3. Content Tabs
    tab1, tab2, tab3 = st.tabs(["📊 **Visual Analytics**", "📋 **Detailed Policy Table**", "📥 **Export Results**"])

    with tab1:
        st.markdown("### **Cost Breakdown Visualization**")
        fig = generate_visuals(results, [P_NAVY, P_BLUE, P_LIGHT])
        st.pyplot(fig)

    with tab2:
        st.markdown("### **Full Item-by-Item Policy**")
        st.dataframe(df.style.background_gradient(subset=['Total Item Cost ($)'], cmap='YlOrRd').format({
            "Individual Cycle (Ti)": "{:.5f}",
            "Setup Cost ($)": "${:.2f}",
            "Holding Cost ($)": "${:.2f}",
            "Total Item Cost ($)": "${:.2f}"
        }), use_container_width=True)

    with tab3:
        st.markdown("### **Download Center**")
        c1, c2, c3 = st.columns(3)
        
        # JSON Export
        c1.download_button("📂 **Download JSON**", df.to_json(orient='records'), "jrp_results.json", "application/json")
        
        # HTML Export
        html_report = f"""
        <div style="font-family:sans-serif; padding:20px; background:{P_BG}">
            <h1 style="color:{P_NAVY}">JRP Optimization Report</h1>
            <p><b>Total Cost:</b> ${total_cost:.2f}</p>
            {df.to_html(index=False)}
        </div>
        """
        c2.download_button("🌐 **Download HTML**", html_report, "jrp_report.html", "text/html")
        
        # PDF Export
        pdf_bytes = create_pdf(instance, T_star, total_cost, df)
        c3.download_button("📕 **Download PDF**", pdf_bytes, "jrp_report.pdf", "application/pdf")

else:
    # Landing State
    st.info("💡 **Welcome! Please upload your JSON instance file in the sidebar to begin.**")
    st.markdown(f"""
    <div style="background-color:white; padding:20px; border-radius:10px; border:1px solid {P_LIGHT}">
    <h3 style="margin-top:0">**How to use:**</h3>
    1. Prepare a JSON file with keys: <b>A</b>, <b>r</b>, and <b>items</b>.<br>
    2. Upload it using the sidebar on the left.<br>
    3. View the optimal <b>T*</b> and <b>m<sub>i</sub></b> values instantly.<br>
    4. Download your professional reports at the bottom.
    </div>
    """, unsafe_allow_html=True)