import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from backend.db import create_connection
from utils.auth import login, check_auth
from fpdf import FPDF
import base64

# Connect to database
conn, cur = create_connection()

# Page config
st.set_page_config(page_title="College Fees Admin System", layout="wide")

# Login Section
if "auth" not in st.session_state:
    st.session_state.auth = None

if st.session_state.auth is None:
    st.title("\U0001F512 College Fees Admin System - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = login(username, password)
        if role:
            st.session_state.auth = {"username": username, "role": role}
            st.success(f"Welcome, {username} ({role})!")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# Main App
st.sidebar.title("\U0001F4CB Navigation")
menu = st.sidebar.radio("Select Action", [
    "Add Student Fees", "View All Records", "Export to Excel", "Fee Charts", "Generate PDF Receipt", "Logout"
])

if menu == "Add Student Fees":
    st.header("\u2795 Add Student Fee Record")
    with st.form("fee_form"):
        col1, col2 = st.columns(2)
        with col1:
            spr_no = st.text_input("SPR No")
            name = st.text_input("Student Name")
            dept = st.selectbox("Department", ["CSE", "ECE", "EEE", "MECH", "CIVIL", "IT"])
            phone = st.text_input("Phone Number")
            year = st.selectbox("Year", ["I", "II", "III", "IV"])
        with col2:
            tuition = st.number_input("Tuition Fee", 0.0)
            bus = st.number_input("Bus Fee", 0.0)
            hostel = st.number_input("Hostel Fee", 0.0)
            food = st.number_input("Food Fee", 0.0)
            maintenance = st.number_input("Maintenance Fee", 0.0)
            exam = st.number_input("Exam Fee", 0.0)
        paid = st.number_input("Paid Amount", 0.0)
        submitted = st.form_submit_button("Add Record")

    if submitted:
        total = tuition + bus + hostel + food + maintenance + exam
        pending = total - paid
        try:
            cur.execute("""
                INSERT INTO student_fees
                (spr_no, student_name, department, phone_no, year_of_study,
                tuition_fee, bus_fee, hostel_fee, food_fee, maintenance_fee,
                exam_fee, total_fee, paid_fee, pending_fee)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (spr_no, name, dept, phone, year,
                  tuition, bus, hostel, food, maintenance, exam,
                  total, paid, pending))
            conn.commit()
            st.success("\u2705 Record added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

elif menu == "View All Records":
    st.header("\U0001F4DA All Student Records")
    cur.execute("SELECT * FROM student_fees")
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    st.dataframe(df)

elif menu == "Export to Excel":
    st.header("\U0001F4A4 Export Student Fees to Excel")
    cur.execute("SELECT * FROM student_fees")
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Student Fees")
        writer.save()
    st.download_button("Download Excel", data=buffer.getvalue(), file_name="student_fees.xlsx")

elif menu == "Fee Charts":
    st.header("\U0001F4CA Fee Chart by Department")
    cur.execute("SELECT department, SUM(paid_fee) as paid FROM student_fees GROUP BY department")
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=["Department", "Paid Fees"])

    fig, ax = plt.subplots()
    ax.bar(df["Department"], df["Paid Fees"], color='teal')
    ax.set_ylabel("Paid Fees")
    ax.set_title("Paid Fees by Department")
    st.pyplot(fig)

elif menu == "Generate PDF Receipt":
    st.header("\U0001F9FE Generate Student Fee Receipt")
    spr = st.text_input("Enter SPR No")
    if st.button("Generate Receipt"):
        cur.execute("SELECT * FROM student_fees WHERE spr_no = %s", (spr,))
        row = cur.fetchone()
        if row:
            col_names = [desc[0] for desc in cur.description]
            data = dict(zip(col_names, row))

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="College Fee Receipt", ln=True, align='C')
            pdf.ln(10)
            for k, v in data.items():
                pdf.cell(200, 10, txt=f"{k.replace('_', ' ').title()}: {v}", ln=True)

            pdf_output = pdf.output(dest='S').encode('latin-1')
            b64 = base64.b64encode(pdf_output).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="receipt_{spr}.pdf">\U0001F4E5 Download Receipt PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.error("SPR No not found.")

elif menu == "Logout":
    st.session_state.auth = None
    st.success("You have been logged out. Please refresh.")
    st.stop()
