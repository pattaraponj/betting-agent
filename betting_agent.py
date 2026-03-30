import streamlit as st
import pandas as pd
from datetime import datetime
import random

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
elapsed = datetime.now() - st.session_state.session_start_time
minutes_passed = int(elapsed.total_seconds() / 60)
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

# นาฬิกา
st.progress(min(minutes_passed / session_time_limit, 1.0))
st.write(f"⏱️ เวลาที่ใช้ไป: **{minutes_passed} นาที** | เหลือ: **{time_remaining} นาที**")

if time_remaining <= 5 and time_remaining > 0:
    st.warning(f"⚠️ เหลือเวลาเพียง {time_remaining} นาที!")
elif time_remaining <= 0:
    st.error("⏰ ครบเวลา 60 นาทีแล้ว! แนะนำให้หยุดเล่นทันที")

# แสดงเดิมพัน
bet_amount = base_unit * sequence[st.session_state.step]
is_set_complete = (st.session_state.step == 0) and len(st.session_state.history) > 0

if is_set_complete:
    st.success(f"🎉 ครบเซตแล้ว! (ครบ {max_steps} ไม้)")
    st.balloons()
else:
    st.success(f"🔥 Agent แนะนำแทง **{bet_amount:,} บาท** (Banker) - ขั้นที่ {st.session_state.step + 1}")

# ปุ่มเล่น
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
        "กำไร": bet,
        "ครบเซต": (st.session_state.step + 1 == max_steps)
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
        "เวลา": datetime.now().strftime("%H:%M"),
        "สูตร": system_name,
        "ขั้น": st.session_state.step + 1,
        "แทง": bet,
        "ผล": "แพ้",
        "กำไร": -bet,
        "ครบเซต": False
    })
    
    st.session_state.step = 0

# ==================== แมวโกรธ (Angry Cat Effect) ====================
def show_angry_cat():
    st.markdown("""
    <div style="text-align: center; font-size: 60px; animation: float 2s ease-in-out infinite;">
        😾🐱😿
    </div>
    <style>
    @keyframes float {
        0% { transform: translateY(0); }
        50% { transform: translateY(-30px); }
        100% { transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)
    st.error("😾 **แมวโกรธแล้ว!** หยุดเล่นเดี๋ยวนี้!")

# ตรวจสอบเงื่อนไขแสดงแมวโกรธ
show_cat = False
cat_message
