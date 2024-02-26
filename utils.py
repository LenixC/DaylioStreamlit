import streamlit as st

def add_title():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "Daylio Inspector";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 1.5rem;
                font-weight: 600;
                position: relative;
                top: 50px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
