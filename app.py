import streamlit as st
import pandas as pd
import os

# 1. จัดการฐานข้อมูล
DATA_FILE = "my_shopping_list.csv"

def load_data():
    cols = ["ชื่อสินค้า", "หมวดหมู่", "ราคาขาย", "ลิงก์สินค้า", "ภาพสินค้า"]
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = 0.0 if col == "ราคาขาย" else ""
        return df[cols]
    else:
        return pd.DataFrame(columns=cols)

# 2. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Smart Shopping List", layout="wide")
st.title("📦 ระบบจัดการสินค้า (ค้นหาและเรียงลำดับ)")

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
        link = st.text_input("ลิงก์หน้าสินค้า (Lazada/Shopee)")
    
    if st.button("บันทึกรายการใหม่", use_container_width=True):
        if name and link:
            new_row = pd.DataFrame([{"ชื่อสินค้า": name, "หมวดหมู่": cat, "ราคาขาย": price, "ลิงก์สินค้า": link, "ภาพสินค้า": img}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("บันทึกสำเร็จ!")
            st.rerun()

st.divider()

# --- ส่วนที่ 2: การเรียงลำดับและการจัดการข้อมูล ---
st.subheader("📝 รายการสินค้าทั้งหมด")

# เพิ่มตัวเลือกการเรียงลำดับ
col_sort1, col_sort2 = st.columns([1, 2])
with col_sort1:
    sort_option = st.selectbox(
        "🔃 เรียงลำดับตาม:",
        ["ไม่เรียง (ตามลำดับที่เพิ่ม)", "ชื่อสินค้า (ก-ฮ)", "หมวดหมู่ (ก-ฮ)", "ราคา (น้อยไปมาก)", "ราคา (มากไปน้อย)"]
    )

# ตรรกะการเรียงลำดับ
display_df = st.session_state.df.copy()
if sort_option == "ชื่อสินค้า (ก-ฮ)":
    display_df = display_df.sort_values(by="ชื่อสินค้า")
elif sort_option == "หมวดหมู่ (ก-ฮ)":
    display_df = display_df.sort_values(by="หมวดหมู่")
elif sort_option == "ราคา (น้อยไปมาก)":
    display_df = display_df.sort_values(by="ราคาขาย", ascending=True)
elif sort_option == "ราคา (มากไปน้อย)":
    display_df = display_df.sort_values(by="ราคาขาย", ascending=False)

# ตารางแก้ไขข้อมูล
edited_df = st.data_editor(
    display_df,
    column_config={
        "ภาพสินค้า": st.column_config.ImageColumn("Preview"),
        "ลิงก์สินค้า": st.column_config.LinkColumn("ไปที่ร้าน"),
        "ราคาขาย": st.column_config.NumberColumn("ราคา (฿)", format="%.2f"),
    },
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)

if st.button("💾 บันทึกการเปลี่ยนแปลงทั้งหมด", type="primary", use_container_width=True):
    st.session_state.df = edited_df
    st.session_state.df.to_csv(DATA_FILE, index=False)
    st.success("อัปเดตข้อมูลแล้ว!")
    st.rerun()

# --- ส่วนที่ 3: ระบบค้นหา (ปรับปรุงใหม่ให้แม่นยำขึ้น) ---
st.divider()
st.subheader("🔍 ค้นหาด่วน")
search = st.text_input("พิมพ์เพื่อค้นหา (ชื่อสินค้า, หมวดหมู่ หรือราคา)...")

if search:
    # ค้นหาจากข้อมูลล่าสุดในตาราง
    # ใช้ .astype(str) เพื่อให้ค้นหาตัวเลขราคาได้ด้วย
    mask = (
        st.session_state.df['ชื่อสินค้า'].astype(str).str.contains(search, case=False, na=False) |
        st.session_state.df['หมวดหมู่'].astype(str).str.contains(search, case=False, na=False) |
        st.session_state.df['ราคาขาย'].astype(str).str.contains(search, na=False)
    )
    search_result = st.session_state.df[mask]

    if not search_result.empty:
        st.write(f"🔎 พบ {len(search_result)} รายการ:")
        # เปลี่ยนจาก st.table เป็น st.dataframe เพื่อให้คลิกหัวตารางเรียงลำดับในผลค้นหาได้ด้วย
        st.dataframe(
            search_result,
            column_config={
                "ภาพสินค้า": st.column_config.ImageColumn("Preview"),
                "ลิงก์สินค้า": st.column_config.LinkColumn("ไปที่ร้าน"),
                "ราคาขาย": st.column_config.NumberColumn("ราคา (฿)", format="%.2f"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning(f"ไม่พบข้อมูลที่ตรงกับ '{search}'")