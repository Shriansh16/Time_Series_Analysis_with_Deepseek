import os
import streamlit as st
import pandas as pd
import numpy as np
from groq import Groq

# Initialize Streamlit page config
st.set_page_config(page_title="Time Series Analysis", layout="wide")

# Initialize API key
st.secrets["GROQ_API_KEY"]

def prepare_time_series_data(df):
    """Prepare time series data by identifying date columns and numerical columns"""
    # Try to identify date column
    date_columns = df.select_dtypes(include=['datetime64']).columns
    if len(date_columns) == 0:
        # Try to convert string columns to datetime
        for col in df.select_dtypes(include=['object']):
            try:
                pd.to_datetime(df[col])
                date_columns = [col]
                df[col] = pd.to_datetime(df[col])
                break
            except:
                continue
    
    # Identify numeric columns
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    
    return df, date_columns, numeric_columns
                          


def generate_response(query,context):    

    client = Groq(api_key=api_key1)
    completion = client.chat.completions.create(
      model="deepseek-r1-distill-llama-70b",
      messages=[
                {
                    "role": "system", 
                    "content": """You are a time series analysis expert. Analyze the provided data and statistics to answer questions asked by the user."""
                },
                {
                    "role": "user", 
                    "content": f"""user query {query}
                                    dataset {context}"""
                }
            ],
      temperature=0.6,
      top_p=0.95
      )
    return completion.choices[0].message.content




st.title("Time Series Analysis with Deepseek R1")
uploaded_file = st.file_uploader("Upload your time series data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Prepare time series data
        df, date_columns, numeric_columns = prepare_time_series_data(df)
        
        if len(date_columns) == 0:
            st.error("No date column found in the data. Please ensure your data includes a date column.")
            st.stop()
            
        # Display data overview
        st.subheader("Data Overview")
        st.dataframe(df.head())
        
        # Date column selection
        date_col = st.selectbox("Select date column", date_columns)
        
        date_info = st.text_input("Enter the year related to your question")
        user_query = st.text_input("Ask about your time series data")
        
        if st.button("Submit"):
            with st.spinner("Analyzing..."):
                if date_info and date_info.isdigit():
                   year = int(date_info)
                   df_filtered = df[df[date_col].dt.year == year]
                else:
                   df_filtered = df
                response = generate_response(user_query,df_filtered)
                st.write(response)
                    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")