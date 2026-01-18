import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Shopping List Permanent", layout="wide")
st.title("📦 ระบบจัดการสินค้า (ข้อมูลถาวรบน Google Sheets)")

# 2. เชื่อมต่อ Google Sheets (ใส่ลิงก์ของคุณที่นี่)
url = "https://docs.google.com/spreadsheets/d/1uAbeRSPblLx2MWjRlXGfrSqfXl8udyniEnrtxn7Qw3Q/edit?usp=sharing" # <-- วางลิงก์ Google Sheets ของคุณที่นี่
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4], ttl="0")

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- ส่วนที่ 1: เพิ่มสินค้าใหม่ ---
with st.expander("➕ เพิ่มรายการสินค้าใหม่"):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อสินค้า")
        cat = st.text_input("หมวดหมู่")
        price = st.number_input("ราคาขาย (บาท)", min_value=0.0, step=1.0)
    with c2:
        img = st.text_input("ลิงก์ภาพสินค้า (URL)")
        link = st.text_input("ลิงก์หน้าสินค้า")
    
    if st.button("บันทึกรายการใหม่", use_container_width=True):
        if name and link:
            new_row = pd.DataFrame([{"ชื่อสินค้า": name, "หมวดหมู่": cat, "ราคาขาย": price, "ลิงก์สินค้า": link, "ภาพสินค้า": img}])
            updated_df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            conn.update(spreadsheet=url, data=updated_df)
            st.success("บันทึกเข้า Google Sheets สำเร็จ!")
            st.session_state.df = updated_df
            st.rerun()

st.divider()

# --- ส่วนที่ 2: การเรียงลำดับและแก้ไข ---
st.subheader("📝 รายการสินค้าทั้งหมด")
sort_option = st.selectbox("🔃 เรียงลำดับตาม:", ["ไม่เรียง", "ชื่อสินค้า (ก-ฮ)", "หมวดหมู่", "ราคา (น้อยไปมาก)", "ราคา (มากไปน้อย)"])

display_df = st.session_state.df.copy()
if sort_option == "ชื่อสินค้า (ก-ฮ)": display_df = display_df.sort_values(by="ชื่อสินค้า")
elif sort_option == "ราคา (น้อยไปมาก)": display_df = display_df.sort_values(by="ราคาขาย")

edited_df = st.data_editor(
    display_df,
    column_config={
        "ภาพสินค้า": st.column_config.ImageColumn("Preview"),
        "ลิงก์สินค้า": st.column_config.LinkColumn("ไปที่ร้าน"),
        "ราคาขาย": st.column_config.NumberColumn("ราคา", format="%.2f ฿"),
    },
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)

if st.button("💾 บันทึกการแก้ไขลง Google Sheets", type="primary", use_container_width=True):
    conn.update(spreadsheet=url, data=edited_df)
    st.session_state.df = edited_df
    st.success("อัปเดตข้อมูลถาวรเรียบร้อยแล้ว!")

# --- ส่วนที่ 3: ค้นหาด่วน ---
st.divider()
search = st.text_input("🔍 ค้นหา (ชื่อ, หมวดหมู่, ราคา)...")
if search:
    mask = st.session_state.df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
    st.dataframe(st.session_state.df[mask], use_container_width=True, hide_index=True)