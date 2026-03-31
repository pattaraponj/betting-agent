import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="AI Betting Agent - พี่เอก", layout="centered", page_icon="🤖")
st.title("🤖 AI Betting Agent")
st.caption("พี่เอกดูแล | แผน 10,000 → 250,000 | Banker 100% | เวลาไทย UTC+7")

thai_tz = pytz.timezone('Asia/Bangkok')

# Sidebar
st.sidebar.header("⚙️ ตั้งค่าตัวแทน")
capital = st.sidebar.number_input("💰 ทุนปัจจุบัน (บาท)", value=10000, step=100)
base_unit = st.sidebar.number_input("Base Unit", value=200, step=50)
daily_target = st.sidebar.number_input("Daily Target Win", value=3000, step=100)
daily_stop = st.sidebar.number_input("Daily Stop Loss", value=-1000, step=100)
session_time_limit = st.sidebar.number_input("จำกัดเวลาเซสชั่น (นาที)", value=60, step=5)

system_choice = st.sidebar.radio("เลือกสูตรเดินเงิน", 
    ["1-2 (Paroli 2 ขั้น)", 
     "1-3", 
     "Paroli 3 ขั้น (1-2-4)", 
     "1-3-2-6", 
     "Oscar’s Grind"])

# Session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'daily_profit' not in st.session_state:
    st.session_state.daily_profit = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'consecutive_loss' not in st.session_state:
    st.session_state.consecutive_loss = 0
if 'current_bet' not in st.session_state:
    st.session_state.current_bet = 1
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = datetime.now(thai_tz)

if 'system' not in st.session_state or system_choice != st.session_state.system:
    st.session_state.step = 0
    st.session_state.current_bet = 1
    st.session_state.system = system_choice

# กำหนดสูตร
if system_choice == "1-2 (Paroli 2 ขั้น)":
    sequence = [1, 2]
    max_steps = 2
    system_name = "1-2"
elif system_choice == "1-3":
    sequence = [1, 3]
    max_steps = 2
    system_name = "1-3"
elif system_choice == "Paroli 3 ขั้น (1-2-4)":
    sequence = [1, 2, 4]
    max_steps = 3
    system_name = "Paroli 3 ขั้น"
elif system_choice == "1-3-2-6":
    sequence = [1, 3, 2, 6]
    max_steps = 4
    system_name = "1-3-2-6"
else:  # Oscar’s Grind
    system_name = "Oscar’s Grind"
    max_steps = 999

# คำนวณเวลา
elapsed = datetime.now(thai_tz) - st.session_state.session_start_time
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
    st.metric("แพ้ติด", f"{st.session_state.consecutive_loss} ไม้")

# นาฬิกา
st.progress(min(minutes_passed / session_time_limit, 1.0))
st.write(f"⏱️ เวลาที่ใช้ไป: **{minutes_passed} นาที** | เหลือ: **{time_remaining} นาที**")

if time_remaining <= 5 and time_remaining > 0:
    st.warning(f"⚠️ เหลือเวลาเพียง {time_remaining} นาที!")
elif time_remaining <= 0:
    st.error("⏰ ครบเวลา 60 นาทีแล้ว! หยุดเล่นทันที")

# ==================== คำนวณเดิมพัน (ปรับให้แสดงปัจจุบันทันที) ====================
if system_name == "Oscar’s Grind":
    bet_amount = base_unit * st.session_state.current_bet
else:
    bet_amount = base_unit * sequence[st.session_state.step]

st.success(f"🔥 Agent แนะนำแทง **{bet_amount:,} บาท** (Banker) - ขั้นปัจจุบัน")

# ปุ่มเล่น
colA, colB = st.columns(2)

if colA.button("✅ ชนะ (W)", use_container_width=True, type="primary"):
    bet = bet_amount
    capital += bet
    st.session_state.daily_profit += bet
    st.session_state.consecutive_loss = 0

    if system_name == "Oscar’s Grind":
        st.session_state.current_bet += 1
    else:
        st.session_state.step += 1
        if st.session_state.step >= max_steps:
            st.session_state.step = 0

    # บันทึกประวัติ
    st.session_state.history.append({
        "เวลา": datetime.now(thai_tz).strftime("%H:%M:%S"),
        "สูตร": system_name,
        "ขั้น": st.session_state.step if system_name != "Oscar’s Grind" else st.session_state.current_bet - 1,
        "แทง": bet,
        "ผล": "ชนะ",
        "กำไร": bet,
        "ครบเซต": (st.session_state.step == 0) if system_name != "Oscar’s Grind" else False
    })

    if (st.session_state.step == 0) and system_name != "Oscar’s Grind":
        st.balloons()

    st.rerun()   # ← เพิ่มบรรทัดนี้เพื่อรีเฟรชทันที

if colB.button("❌ แพ้ (L)", use_container_width=True, type="secondary"):
    bet = bet_amount
    capital -= bet
    st.session_state.daily_profit -= bet
    st.session_state.consecutive_loss += 1

    if system_name == "Oscar’s Grind":
        pass
    else:
        st.session_state.step = 0

    st.session_state.history.append({
        "เวลา": datetime.now(thai_tz).strftime("%H:%M:%S"),
        "สูตร": system_name,
        "ขั้น": st.session_state.step if system_name != "Oscar’s Grind" else st.session_state.current_bet,
        "แทง": bet,
        "ผล": "แพ้",
        "กำไร": -bet,
        "ครบเซต": False
    })

    st.rerun()   # ← เพิ่มบรรทัดนี้เพื่อรีเฟรชทันที

# แมวโกรธ
if st.session_state.daily_profit <= daily_stop or st.session_state.consecutive_loss >= 3:
    st.markdown("""
    <div style="text-align: center; font-size: 70px; animation: float 1.8s ease-in-out infinite;">
        😾 😿 🐱
    </div>
    <style>
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-40px); } 100% { transform: translateY(0px); } }
    </style>
    """, unsafe_allow_html=True)
    st.error("🚨 แมวโกรธแล้ว! หยุดเล่นเดี๋ยวนี้")

# Mindfulness
st.subheader("🧘 Mindfulness")
col_m1, col_m2 = st.columns(2)
with col_m1:
    if st.button("🌀 Urge Surfing"):
        st.info("**Urge Surfing**: นึกความอยากเป็นคลื่น → หายใจตามจังหวะ → ปล่อยให้คลื่นลงเอง")
with col_m2:
    if st.button("🧠 Box Breathing"):
        st.info("**Box Breathing**: เข้า 4 วินาที → กลั้น 4 → ออก 4 → กลั้น 4")

# ตารางประวัติ
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    def highlight_row(row):
        if row.get('ครบเซต') == True:
            return ['background-color: #90EE90; color: black'] * len(row)
        elif row['ผล'] == "แพ้":
            return ['background-color: #FFCCCC; color: black'] * len(row)
        else:
            return ['background-color: #FFE6B3; color: black'] * len(row)
    styled_df = df.style.apply(highlight_row, axis=1)
    st.subheader("📊 ประวัติการเล่นวันนี้")
    st.dataframe(styled_df, use_container_width=True)

# กราฟทุนสะสม
if st.session_state.history:
    df_graph = pd.DataFrame(st.session_state.history)
    cumulative = [capital]
    for gain in df_graph['กำไร']:
        cumulative.append(cumulative[-1] + gain)
    df_graph['ทุนสะสม'] = cumulative[1:]
    st.subheader("📈 กราฟทุนสะสมวันนี้")
    st.line_chart(df_graph.set_index('เวลา')['ทุนสะสม'], use_container_width=True)

# รีเซ็ต
if st.button("🔄 รีเซ็ตเซสชั่นใหม่"):
    st.session_state.daily_profit = 0
    st.session_state.step = 0
    st.session_state.consecutive_loss = 0
    st.session_state.current_bet = 1
    st.session_state.history = []
    st.session_state.session_start_time = datetime.now(thai_tz)
    st.success("รีเซ็ตเซสชั่นใหม่เรียบร้อย!")

st.caption("💡 ปรับการแสดงเดิมพันให้เร็วขึ้นแล้ว (ใช้ st.rerun)")
