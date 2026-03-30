import streamlit as st
import pandas as pd
from datetime import datetime
import pytz  # เพิ่มตัวนี้เพื่อจัดการ timezone

st.set_page_config(page_title="AI Betting Agent - พี่เอก", layout="centered", page_icon="🤖")
st.title("🤖 AI Betting Agent 1-3-2-6 & Paroli")
st.caption("พี่เอกดูแล | แผน 10,000 → 250,000 | Banker 100% | เวลาไทย UTC+7")

# สร้าง timezone ไทย
thai_tz = pytz.timezone('Asia/Bangkok')

# Sidebar (เหมือนเดิม)
st.sidebar.header("⚙️ ตั้งค่าตัวแทน")
capital = st.sidebar.number_input("💰 ทุนปัจจุบัน (บาท)", value=10000, step=100)
base_unit = st.sidebar.number_input("Base Unit", value=200, step=50)
daily_target = st.sidebar.number_input("Daily Target Win", value=3000, step=100)
daily_stop = st.sidebar.number_input("Daily Stop Loss", value=-1000, step=100)
session_time_limit = st.sidebar.number_input("จำกัดเวลาเซสชั่น (นาที)", value=60, step=5)

system_choice = st.sidebar.radio("เลือกสูตรเดินเงิน", 
                                 ["Paroli 3 ขั้น (1-2-4)", "1-3-2-6"])

# Session state (เหมือนเดิม)
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'daily_profit' not in st.session_state:
    st.session_state.daily_profit = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'consecutive_loss' not in st.session_state:
    st.session_state.consecutive_loss = 0
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = datetime.now(thai_tz)

if 'system' not in st.session_state or system_choice != st.session_state.system:
    st.session_state.step = 0
    st.session_state.system = system_choice

# กำหนด sequence (เหมือนเดิม)
if system_choice == "Paroli 3 ขั้น (1-2-4)":
    sequence = [1, 2, 4]
    max_steps = 3
    system_name = "Paroli 3 ขั้น"
else:
    sequence = [1, 3, 2, 6]
    max_steps = 4
    system_name = "1-3-2-6"

# คำนวณเวลาเซสชั่น (ใช้ timezone ไทย)
elapsed = datetime.now(thai_tz) - st.session_state.session_start_time
minutes_passed = int(elapsed.total_seconds() / 60)
time_remaining = max(0, session_time_limit - minutes_passed)

# ... (ส่วนอื่น ๆ ด้านบนเหมือนเดิมจนถึงปุ่มเล่น) ...

# ปุ่มเล่น - แก้การบันทึกเวลาให้เป็น timezone ไทย
if colA.button("✅ ชนะ (W)", use_container_width=True, type="primary"):
    bet = base_unit * sequence[st.session_state.step]
    capital += bet
    st.session_state.daily_profit += bet
    st.session_state.consecutive_loss = 0
    
    current_step = st.session_state.step + 1
    is_completing_set = (current_step == max_steps)
    
    st.session_state.history.append({
        "เวลา": datetime.now(thai_tz).strftime("%H:%M:%S"),   # แก้ตรงนี้
        "สูตร": system_name,
        "ขั้น": current_step,
        "แทง": bet,
        "ผล": "ชนะ",
        "กำไร": bet,
        "ครบเซต": is_completing_set
    })
    
    st.session_state.step += 1
    if st.session_state.step >= max_steps:
        st.session_state.step = 0
        st.balloons()

if colB.button("❌ แพ้ (L)", use_container_width=True, type="secondary"):
    bet = base_unit * sequence[st.session_state.step]
    capital -= bet
    st.session_state.daily_profit -= bet
    st.session_state.consecutive_loss += 1
    
    st.session_state.history.append({
        "เวลา": datetime.now(thai_tz).strftime("%H:%M:%S"),   # แก้ตรงนี้
        "สูตร": system_name,
        "ขั้น": st.session_state.step + 1,
        "แทง": bet,
        "ผล": "แพ้",
        "กำไร": -bet,
        "ครบเซต": False
    })
    
    st.session_state.step = 0

# ... (ส่วนแมวโกรธ, Mindfulness, ตารางสี ไว้เหมือนเดิม) ...

# กราฟทุนสะสม (ล่างสุด) - แก้ให้แสดงเวลาไทยชัดเจน
if st.session_state.history:
    df_graph = pd.DataFrame(st.session_state.history)
    cumulative = [capital]
    for gain in df_graph['กำไร']:
        cumulative.append(cumulative[-1] + gain)
    df_graph['ทุนสะสม'] = cumulative[1:]
    
    st.subheader("📈 กราฟทุนสะสมวันนี้")
    # ใช้เวลาเป็น index เพื่อให้แสดงถูกต้อง
    chart_df = df_graph.set_index('เวลา')['ทุนสะสม']
    st.line_chart(chart_df, use_container_width=True)

# รีเซ็ต (เหมือนเดิม)
if st.button("🔄 รีเซ็ตเซสชั่นใหม่"):
    st.session_state.daily_profit = 0
    st.session_state.step = 0
    st.session_state.consecutive_loss = 0
    st.session_state.history = []
    st.session_state.session_start_time = datetime.now(thai_tz)
    st.success("รีเซ็ตเซสชั่นใหม่เรียบร้อย!")

st.caption("💡 เวลาทั้งหมดปรับให้เป็นโซนกรุงเทพฯ (UTC+7) แล้ว")
