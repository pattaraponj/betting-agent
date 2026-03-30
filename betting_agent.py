import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="AI Betting Agent - พี่เอก", layout="centered", page_icon="🤖")
st.title("🤖 AI Betting Agent 1-3-2-6 & Paroli")
st.caption("พี่เอกดูแล | แผน 10,000 → 250,000 | Banker 100%")

# Sidebar
st.sidebar.header("⚙️ ตั้งค่าตัวแทน")
capital = st.sidebar.number_input("💰 ทุนปัจจุบัน (บาท)", value=10000, step=100)
base_unit = st.sidebar.number_input("Base Unit", value=200, step=50)
daily_target = st.sidebar.number_input("Daily Target Win", value=3000, step=100)
daily_stop = st.sidebar.number_input("Daily Stop Loss", value=-1000, step=100)
session_time_limit = st.sidebar.number_input("จำกัดเวลาเซสชั่น (นาที)", value=60, step=5)

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
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = datetime.now()

# เปลี่ยนสูตร
if 'system' not in st.session_state or system_choice != st.session_state.system:
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

# คำนวณเวลาเซสชั่น
elapsed_time = datetime.now() - st.session_state.session_start_time
minutes_passed = int(elapsed_time.total_seconds() / 60)
time_remaining = max(0, session_time_limit - minutes_passed)

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
              delta=None if st.session_state.consecutive_loss < 3 else "⚠️")

# แสดงนาฬิกาจับเวลา
time_col1, time_col2 = st.columns([3, 1])
with time_col1:
    st.progress(min(minutes_passed / session_time_limit, 1.0))
with time_col2:
    st.write(f"⏱️ {time_remaining} นาที")

if time_remaining <= 5 and time_remaining > 0:
    st.warning(f"⚠️ เหลือเวลาเพียง {time_remaining} นาที! เตรียมตัวหยุดเซสชั่น")
elif time_remaining <= 0:
    st.error("⏰ ครบเวลา 1 ชั่วโมงแล้ว! แนะนำให้หยุดเล่นทันที")

# คำนวณเดิมพัน + แสดงสีตามสถานะเซต
is_set_complete = st.session_state.step == 0 and len(st.session_state.history) > 0

bet_amount = base_unit * sequence[st.session_state.step]

if is_set_complete:
    st.success(f"🎉 ครบเซตแล้ว! กำไรดีมาก → รีเซ็ตอัตโนมัติ")
    st.balloons()
else:
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

# การแจ้งเตือน
if st.session_state.consecutive_loss >= 3:
    st.warning("⚠️ แพ้ติด 3 ไม้แล้ว! แนะนำให้หยุดเล่น หรือเปลี่ยนห้องโต๊ะทันที")

if st.session_state.daily_profit >= daily_target:
    st.error("🚨 ถึง Daily Target แล้ว! หยุด + Cash Out ทันที")
elif st.session_state.daily_profit <= daily_stop:
    st.error("🚨 ถึง Stop Loss แล้ว! หยุดเดี๋ยวนี้")

# ==================== Mindfulness ====================
st.subheader("🧘 Mindfulness")
col_m1, col_m2 = st.columns(2)
with col_m1:
    if st.button("🌀 Urge Surfing"):
        st.info("**Urge Surfing**: นึกความอยากเป็นคลื่น → หายใจตามคลื่น → ไม่ต้องสู้ → คลื่นจะลงเอง")
with col_m2:
    if st.button("🧠 Box Breathing"):
        st.info("**Box Breathing**: เข้า 4 วินาที → กลั้น 4 → ออก 4 → กลั้น 4 (ทำ 8-10 รอบ)")

# ==================== กราฟทุนสะสม (ย้ายไปล่างสุด) ====================
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    # คำนวณทุนสะสม
    cumulative = [capital]
    for i in range(len(df)):
        cumulative.append(cumulative[-1] + df.iloc[i]['กำไร'])
    df['ทุนสะสม'] = cumulative[1:]
    
    st.subheader("📈 กราฟทุนสะสมวันนี้")
    st.line_chart(df.set_index('เวลา')['ทุนสะสม'])

# ประวัติการเล่น
if st.session_state.history:
    st.subheader("📊 ประวัติการเล่นวันนี้")
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

# รีเซ็ตเซสชั่น
if st.button("🔄 รีเซ็ตเซสชั่นใหม่ (เริ่มเวลาใหม่)"):
    st.session_state.daily_profit = 0
    st.session_state.step = 0
    st.session_state.consecutive_loss = 0
    st.session_state.history = []
    st.session_state.session_start_time = datetime.now()
    st.success("รีเซ็ตเซสชั่นใหม่เรียบร้อย! เวลาเริ่มนับใหม่")

st.caption("💡 แนะนำให้เล่นไม่เกิน 60 นาทีต่อเซสชั่น + ใช้ร่วมกับตารางชีวิต")
