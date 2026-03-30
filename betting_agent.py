import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="AI Betting Agent - พี่เอก", layout="centered", page_icon="🤖")
st.title("🤖 AI Betting Agent 1-3-2-6 & Paroli")
st.caption("พี่เอกดูแล | แผน 10,000 → 250,000 | Banker 100%")

# Sidebar ตั้งค่า (ปรับ Default ให้เข้ากับแผน 10K → 250K)
st.sidebar.header("⚙️ ตั้งค่าตัวแทน")
capital = st.sidebar.number_input("💰 ทุนปัจจุบัน (บาท)", value=10000, step=100)
base_unit = st.sidebar.number_input("Base Unit", value=200, step=50)
daily_target = st.sidebar.number_input("Daily Target Win", value=3000, step=100)
daily_stop = st.sidebar.number_input("Daily Stop Loss", value=-1000, step=100)

system_choice = st.sidebar.radio("เลือกสูตรเดินเงิน", 
                                 ["Paroli 3 ขั้น (1-2-4)", "1-3-2-6"])

# Session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'daily_profit' not in st.session_state:
    st.session_state.daily_profit = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'consecutive_loss' not in st.session_state:
    st.session_state.consecutive_loss = 0
if 'capital_history' not in st.session_state:
    st.session_state.capital_history = [capital]  # สำหรับกราฟ

if 'system' not in st.session_state:
    st.session_state.system = system_choice

# เปลี่ยนสูตรเมื่อเลือกใหม่
if system_choice != st.session_state.system:
    st.session_state.step = 0
    st.session_state.system = system_choice

# กำหนด sequence
if system_choice == "Paroli 3 ขั้น (1-2-4)":
    sequence = [1, 2, 4]
    max_steps = 3
    system_name = "Paroli 3 ขั้น"
else:
    sequence = [1, 3, 2, 6]
    max_steps = 4
    system_name = "1-3-2-6"

# แสดงสถานะหลัก
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("ทุนปัจจุบัน", f"{capital:,} บาท")
with col2:
    st.metric("กำไรวันนี้", f"{st.session_state.daily_profit:+,} บาท")
with col3:
    st.metric("สูตรที่ใช้", system_name)
with col4:
    st.metric("แพ้ติด", f"{st.session_state.consecutive_loss} ไม้", 
              delta=None if st.session_state.consecutive_loss < 3 else "⚠️ อันตราย")

# คำนวณเดิมพัน
bet_amount = base_unit * sequence[st.session_state.step]
st.success(f"🔥 Agent แนะนำแทง **{bet_amount:,} บาท** (Banker) - ขั้นที่ {st.session_state.step + 1}")

# ปุ่มผลลัพธ์
colA, colB = st.columns(2)
if colA.button("✅ ชนะ (W)", use_container_width=True, type="primary"):
    bet = base_unit * sequence[st.session_state.step]
    capital += bet
    st.session_state.daily_profit += bet
    st.session_state.consecutive_loss = 0
    
    st.session_state.history.append({
        "เวลา": datetime.now().strftime("%H:%M"),
        "สูตร": system_name,
        "ขั้น": st.session_state.step + 1,
        "แทง": bet,
        "ผล": "ชนะ",
        "กำไร": bet
    })
    
    st.session_state.step += 1
    if st.session_state.step >= max_steps:
        st.balloons()
        st.success(f"🎉 ครบ {max_steps} ไม้! กำไรดีมาก → รีเซ็ต")
        st.session_state.step = 0

if colB.button("❌ แพ้ (L)", use_container_width=True, type="secondary"):
    bet = base_unit * sequence[st.session_state.step]
    capital -= bet
    st.session_state.daily_profit -= bet
    st.session_state.consecutive_loss += 1
    
    st.session_state.history.append({
        "เวลา": datetime.now().strftime("%H:%M"),
        "สูตร": system_name,
        "ขั้น": st.session_state.step + 1,
        "แทง": bet,
        "ผล": "แพ้",
        "กำไร": -bet
    })
    
    st.session_state.step = 0

# การแจ้งเตือนเมื่อแพ้ 3 ไม้ติด
if st.session_state.consecutive_loss >= 3:
    st.warning("⚠️ แพ้ติด 3 ไม้แล้ว! แนะนำให้หยุดเล่นวันนี้ หรือเปลี่ยนห้องโต๊ะทันที")
    st.info("💡 ลองทำ Urge Surfing หรือ Box Breathing 5 นาทีก่อนเล่นต่อ")

# เตือน Target / Stop Loss
if st.session_state.daily_profit >= daily_target:
    st.error("🚨 ถึง Daily Target แล้ว! หยุดเล่น + Cash Out ทันที")
elif st.session_state.daily_profit <= daily_stop:
    st.error("🚨 ถึง Stop Loss แล้ว! ปิดเว็บและหยุดเดี๋ยวนี้")

# ==================== กราฟทุนสะสม ====================
if len(st.session_state.history) > 0:
    # สร้างข้อมูลสำหรับกราฟ
    df_graph = pd.DataFrame(st.session_state.history)
    df_graph['ทุนสะสม'] = capital - df_graph['กำไร'].cumsum() + df_graph['กำไร'].cumsum()
    
    fig = px.line(df_graph, x=df_graph.index, y='ทุนสะสม', 
                  title="กราฟทุนสะสมวันนี้",
                  labels={"index": "ลำดับไม้", "ทุนสะสม": "ทุน (บาท)"},
                  markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ==================== Mindfulness Button ====================
st.subheader("🧘 Mindfulness")
if st.button("🌀 ทำ Urge Surfing (เมื่ออยากเล่นต่อ)"):
    st.info(""" 
    **Urge Surfing Technique**  
    1. นึกถึงความอยากเล่นเป็น “คลื่น”  
    2. หายใจเข้าลึก ๆ ตามจังหวะคลื่น  
    3. รู้ว่าคลื่นจะขึ้นและลงเอง  
    4. ไม่ต้องต่อต้าน แค่ “นั่งบนกระดานเซิร์ฟ”  
    → ความอยากจะลดลงภายใน 1-2 นาที
    """)

if st.button("🧠 ทำ Box Breathing (สงบสมอง)"):
    st.info("""
    **Box Breathing**  
    หายใจเข้า 4 วินาที → กลั้น 4 วินาที → หายใจออก 4 วินาที → กลั้น 4 วินาที  
    ทำซ้ำ 6-10 รอบ จะช่วยลดความโลภและ tilt ได้ดี
    """)

# ประวัติการเล่น
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.subheader("📊 ประวัติการเล่นวันนี้")
    st.dataframe(df, use_container_width=True)

# รีเซ็ตวันใหม่
if st.button("🔄 รีเซ็ตวันใหม่ (เริ่มเซสชั่นใหม่)"):
    st.session_state.daily_profit = 0
    st.session_state.step = 0
    st.session_state.consecutive_loss = 0
    st.session_state.history = []
    st.session_state.capital_history = [capital]
    st.success("รีเซ็ตวันใหม่เรียบร้อย!")

st.caption("💡 ใช้ร่วมกับตารางชีวิตและแผน 10K → 250K ที่เราคุยกันนะครับ")
