import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AI Agent 1-3-2-6", layout="centered", page_icon="🤖")
st.title("🤖 AI Betting Agent 1-3-2-6")
st.caption("พี่เอกดูแล | ทุน 10,000 → เป้า 250,000 | Banker 100%")

# Sidebar ตั้งค่า
st.sidebar.header("⚙️ ตั้งค่าตัวแทน")
capital = st.sidebar.number_input("💰 ทุนปัจจุบัน (บาท)", value=10000, step=100)
base_unit = st.sidebar.number_input("Base Unit", value=200, step=50)
daily_target = st.sidebar.number_input("Daily Target Win", value=3000, step=100)
daily_stop = st.sidebar.number_input("Daily Stop Loss", value=-1000, step=100)

# Session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'daily_profit' not in st.session_state:
    st.session_state.daily_profit = 0
if 'history' not in st.session_state:
    st.session_state.history = []

sequence = [1, 3, 2, 6]

# แสดงสถานะ
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("ทุนปัจจุบัน", f"{capital:,} บาท")
with col2:
    st.metric("กำไรวันนี้", f"{st.session_state.daily_profit:+,} บาท", 
              "✅ ถึง Target" if st.session_state.daily_profit >= daily_target else 
              "❌ ถึง Stop" if st.session_state.daily_profit <= daily_stop else "")
with col3:
    st.metric("ขั้นตอน", f"ไม้ที่ {st.session_state.step + 1}", f"{sequence[st.session_state.step]}x")

bet_amount = base_unit * sequence[st.session_state.step]
st.success(f"🔥 Agent แนะนำแทง **{bet_amount:,} บาท** (Banker)")

# ปุ่มแทง
colA, colB = st.columns(2)
if colA.button("✅ ชนะ (W)", use_container_width=True, type="primary"):
    bet = base_unit * sequence[st.session_state.step]
    capital += bet
    st.session_state.daily_profit += bet
    st.session_state.history.append({
        "เวลา": datetime.now().strftime("%H:%M"),
        "ขั้น": st.session_state.step + 1,
        "แทง": bet,
        "ผล": "ชนะ",
        "กำไร": bet
    })
    st.session_state.step = (st.session_state.step + 1) % 4
    if st.session_state.step == 0:
        st.balloons()
        st.success("🎉 ครบ 4 ไม้! กำไร +12 units → รีเซ็ต")

if colB.button("❌ แพ้ (L)", use_container_width=True, type="secondary"):
    bet = base_unit * sequence[st.session_state.step]
    capital -= bet
    st.session_state.daily_profit -= bet
    st.session_state.history.append({
        "เวลา": datetime.now().strftime("%H:%M"),
        "ขั้น": st.session_state.step + 1,
        "แทง": bet,
        "ผล": "แพ้",
        "กำไร": -bet
    })
    st.session_state.step = 0

# เตือน
if st.session_state.daily_profit >= daily_target:
    st.error("🚨 ถึง Daily Target แล้ว! หยุด + Cash Out ทันที")
elif st.session_state.daily_profit <= daily_stop:
    st.error("🚨 ถึง Stop Loss แล้ว! ปิดเว็บเดี๋ยวนี้")

# ประวัติ
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.subheader("📊 ประวัติวันนี้")
    st.dataframe(df, use_container_width=True)

# ปุ่มรีเซ็ตวันใหม่
if st.button("🔄 รีเซ็ตวันใหม่ (เริ่มเซสชั่นใหม่)"):
    st.session_state.daily_profit = 0
    st.session_state.step = 0
    st.session_state.history = []
    st.success("รีเซ็ตเรียบร้อย!")

st.caption("ทำตามแผน 10K → 250K + ตารางชีวิตที่เราคุยกันนะครับ")