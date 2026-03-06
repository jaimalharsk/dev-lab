import pandas as pd
import streamlit as st
from sqlalchemy import text
from db import engine


st.title("Remote Job Auto-Apply Tracker")

jobs_df = pd.read_sql(text("SELECT id, source, company, title, location, relevance_score, date_found FROM jobs ORDER BY date_found DESC"), engine)
apps_df = pd.read_sql(text("SELECT job_id, date_applied, status FROM applications ORDER BY date_applied DESC"), engine)

st.subheader("Jobs")
st.dataframe(jobs_df, use_container_width=True)

st.subheader("Applications")
st.dataframe(apps_df, use_container_width=True)
