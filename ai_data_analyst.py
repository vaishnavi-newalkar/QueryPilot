import tempfile
import csv
import streamlit as st
import pandas as pd
import numpy as np
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools
from agno.db.sqlite import SqliteDb
import os
from dotenv import load_dotenv
load_dotenv()   
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize SQLite database for session persistence
db = SqliteDb(db_file="./agent_sessions.db")

# Import EDA helper
from eda_helpers import perform_full_analysis    

# Function to preprocess and save the uploaded file with large dataset awareness
def preprocess_and_save(file):
    try:
        # Get file size in MB
        file.seek(0, 2)  # Seek to end
        file_size_mb = file.tell() / (1024 * 1024)
        file.seek(0)  # Reset to beginning
        
        is_large = file_size_mb > 50  # Consider >50MB as large
        
        if is_large:
            st.warning(f"⚠️ Large dataset detected ({file_size_mb:.2f} MB). Using optimized processing...")
        
        # Read the uploaded file into a DataFrame
        if file.name.endswith('.csv'):
            # For large files, use chunked reading to get schema only
            if is_large:
                df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'], nrows=1000)
                st.info("📊 Loaded sample of 1000 rows for schema detection. Full data will be queried via DuckDB.")
            else:
                df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
            if len(df) > 10000:
                is_large = True
                st.warning("⚠️ Large Excel file detected. Consider converting to CSV for better performance.")
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None, None
        
        # Lightweight preprocessing - only schema normalization
        # Avoid expensive transformations on large datasets
        if not is_large:
            # Only do deep preprocessing for smaller datasets
            for col in df.select_dtypes(include=['object']):
                df[col] = df[col].astype(str).replace({r'\"': '\"\"'}, regex=True)
            
            # Parse dates and numeric columns
            for col in df.columns:
                if 'date' in col.lower():
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except (ValueError, TypeError):
                        pass
        
        # Create a temporary file to save the preprocessed data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_path = temp_file.name
            df.to_csv(temp_path, index=False, quoting=csv.QUOTE_ALL)
        
        # Calculate dataset metadata
        row_count = len(df)
        col_count = len(df.columns)
        
        dataset_info = {
            'row_count': row_count,
            'col_count': col_count,
            'file_size_mb': file_size_mb,
            'is_large': is_large
        }
        
        return temp_path, df.columns.tolist(), df, dataset_info
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None, None, None

# Streamlit app
st.title("📊 Data Analyst Agent")

# Initialize session state for session_id
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display session ID (optional, for debugging)
with st.expander("ℹ️ Session Info"):
    st.caption(f"Session ID: {st.session_state.session_id}")
    if st.button("Start New Conversation"):
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# File upload widget
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Preprocess and save the uploaded file
    temp_path, columns, df, dataset_info = preprocess_and_save(uploaded_file)
    
    if temp_path and columns and df is not None and dataset_info is not None:
        # Display dataset info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{dataset_info['row_count']:,}")
        with col2:
            st.metric("Columns", dataset_info['col_count'])
        with col3:
            st.metric("Size", f"{dataset_info['file_size_mb']:.2f} MB")
        
        # Display preview - limit for large datasets
        st.write("Data Preview:")
        if dataset_info['is_large']:
            st.dataframe(df.head(100))  # Show only first 100 rows for large datasets
            st.caption("📝 Showing first 100 rows. Use queries to explore the full dataset.")
        else:
            st.dataframe(df)  # Show full data for small datasets
        
        # Display the columns
        with st.expander("📋 Column Names"):
            st.write(columns)
        
        # Add separator
        st.divider()
        
        # Mode selection: Conversational vs Full Analysis
        st.subheader("🎯 Analysis Mode")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("💬 **Conversational Analytics** - Ask questions in natural language")
        with col2:
            if dataset_info['is_large']:
                st.warning("📊 **Full Dataset Analysis** - May take longer on large datasets")
            else:
                st.success("📊 **Full Dataset Analysis** - Comprehensive EDA report")
        
        # Create tabs for different modes
        tab1, tab2 = st.tabs(["💬 Conversational Analytics", "📊 Full Dataset Analysis"])
        
        with tab2:
            st.markdown("""
            ### Full Dataset Analysis
            This will generate a comprehensive exploratory data analysis (EDA) report including:
            - Dataset overview and statistics
            - Missing values analysis
            - Distribution plots for numeric columns
            - Correlation heatmap
            - Top categories for categorical columns
            - Data quality summary
            """)
            
            if st.button("🚀 Analyze Full Dataset", type="primary", use_container_width=True):
                with st.spinner("📈 Performing comprehensive analysis... This may take a moment for large datasets."):
                    # Initialize DuckDbTools
                    duckdb_tools = DuckDbTools()
                    
                    # Load the CSV file into DuckDB as a table
                    duckdb_tools.load_local_csv_to_table(
                        path=temp_path,
                        table="uploaded_data",
                    )
                    
                    # Perform full analysis
                    perform_full_analysis(duckdb_tools, df, dataset_info)
        
        with tab1:
            st.markdown("### Ask Questions About Your Data")
            st.caption("Use natural language to explore your data safely and efficiently.")
        
        # Initialize DuckDbTools (for conversational mode)
        duckdb_tools = DuckDbTools()
        
        # Load the CSV file into DuckDB as a table
        duckdb_tools.load_local_csv_to_table(
            path=temp_path,
            table="uploaded_data",
        )
        
        # Initialize the Agent with DuckDB and Pandas tools
        data_analyst_agent = Agent(
            model=OpenAIChat(
                id="openai/gpt-oss-20b",
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            ),
            tools=[duckdb_tools, PandasTools()],
            db=db,  # Enable session persistence
            session_id=st.session_state.session_id,  # Track conversation thread
            add_history_to_context=True,  # Include conversation history
            num_history_runs=5,  # Include last 5 interactions
            system_message=f"""You are a senior data analyst AI working inside an interactive analytics application.

Context:
- A dataset has been uploaded and loaded into DuckDB as table `uploaded_data`.
- Dataset size: {dataset_info['row_count']:,} rows × {dataset_info['col_count']} columns ({dataset_info['file_size_mb']:.2f} MB)
- Dataset classification: {'LARGE' if dataset_info['is_large'] else 'SMALL'}
- You have full access to the schema and data through DuckDB tools.
- Users may not know SQL or exact column names.

Your responsibilities:
1. Interpret natural language questions about the data.
2. Translate questions into optimized SQL queries using DuckDB.
3. Execute queries using DuckDB tools — NEVER compute results yourself.
4. Present results clearly in plain English with approach and reasoning.

CRITICAL RULES FOR LARGE DATASETS:
- NEVER use `SELECT *` without LIMIT on large datasets.
- For exploratory queries, automatically add `LIMIT 1000` or use aggregations.
- Prefer COUNT, SUM, AVG, MIN, MAX over returning raw rows.
- For "show me the data" requests on large datasets:
  * Return row count with `SELECT COUNT(*) FROM uploaded_data`
  * Show column list and data types
  * Provide a small sample: `SELECT * FROM uploaded_data LIMIT 10`
  * Suggest aggregated views instead of raw dumps
- If a query would return >10,000 rows, ask user to narrow scope or accept a summary.

Query Safety Rules:
- ALWAYS use SQL via DuckDB for calculations, filtering, aggregation, grouping.
- NEVER guess column names — inspect schema first.
- NEVER fabricate data or results.
- For ambiguous terms ("topper", "best", "high performing"), ask clarification first.
- State assumptions explicitly before executing.
- Prefer minimal queries (select only required columns).
- Add LIMIT clauses by default for safety.

Performance Protection:
- Use WHERE clauses to filter data before aggregations.
- Leverage DuckDB's columnar engine for analytics.
- Avoid operations that scan entire large tables unnecessarily.
- If query seems expensive, warn user and suggest optimization.

User Experience:
- Explain when results are sampled or limited due to dataset size.
- Focus on insights, not raw data dumps.
- Be transparent about query performance trade-offs.
- Guide users toward efficient analytical patterns.

Tone:
- Professional, clear, and helpful.
- Proactive about performance and safety.

Goal:
Enable non-technical users to explore large datasets accurately, safely, and efficiently through natural language.""",
            markdown=True,
        )
        
        # Initialize code storage in session state
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = None
        
        # Use a form to enable Ctrl+Enter keyboard shortcut
        with st.form(key="query_form", clear_on_submit=False):
            # Main query input widget
            user_query = st.text_area(
                "Ask a query about the data:",
                height=100,
                help="Press Ctrl+Enter to submit"
            )
            
            # Submit button
            submit_button = st.form_submit_button("Submit Query", use_container_width=True)
        
        # Add info message about terminal output
        st.info("💡 Check your terminal for a clearer output of the agent's response")
        
        if submit_button:
            if user_query.strip() == "":
                st.warning("Please enter a query.")
            else:
                try:
                    # Show loading spinner while processing
                    with st.spinner('Processing your query...'):
                        # Get the response from the agent
                        response = data_analyst_agent.run(user_query)

                        # Extract the content from the response object
                        if hasattr(response, 'content'):
                            response_content = response.content
                        else:
                            response_content = str(response)

                    # Display the response in Streamlit
                    st.markdown(response_content)
                
                    
                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")