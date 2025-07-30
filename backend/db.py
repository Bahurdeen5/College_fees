import mysql.connector
import streamlit as st

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="2y95ai.h.filess.io",
            user="bahu_enoughcalm",
            password="616c4751af9b69d05bc753e273d11d2f20767603",
            database="bahu_enoughcalm",
            port=3307,
            use_pure=True
        )
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None, None
