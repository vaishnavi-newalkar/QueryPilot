import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Function to perform full dataset analysis
def perform_full_analysis(duckdb_tools, df, dataset_info):
    """Generate a comprehensive exploratory data analysis report"""
    analysis_results = {}
    
    try:
        # 1. Basic Statistics
        st.subheader("📊 Dataset Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{dataset_info['row_count']:,}")
        with col2:
            st.metric("Total Columns", dataset_info['col_count'])
        with col3:
            st.metric("File Size", f"{dataset_info['file_size_mb']:.2f} MB")
        with col4:
            memory_usage = df.memory_usage(deep=True).sum() / 1024**2
            st.metric("Memory Usage", f"{memory_usage:.2f} MB")
        
        # 2. Column Information with Data Types
        st.subheader("📋 Column Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.count().values,
            'Null Count': df.isnull().sum().values,
            'Null %': (df.isnull().sum() / len(df) * 100).round(2).values
        })
        st.dataframe(col_info, use_container_width=True)
        
        # 3. Missing Values Visualization
        if df.isnull().sum().sum() > 0:
            st.subheader("🔍 Missing Values Analysis")
            missing_data = df.isnull().sum()[df.isnull().sum() > 0].sort_values(ascending=False)
            
            fig = px.bar(
                x=missing_data.index,
                y=missing_data.values,
                labels={'x': 'Column', 'y': 'Missing Count'},
                title='Missing Values by Column'
           )
            st.plotly_chart(fig, use_container_width=True)
        
        # 4. Numeric Columns Analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.subheader("📈 Numeric Columns Statistics")
            
            # Descriptive statistics
            stats_df = df[numeric_cols].describe().T
            stats_df['skew'] = df[numeric_cols].skew()
            stats_df['kurtosis'] = df[numeric_cols].kurtosis()
            st.dataframe(stats_df, use_container_width=True)
            
            # Distribution plots for numeric columns (max 6)
            st.subheader("📊 Distribution Plots")
            cols_to_plot = numeric_cols[:6]
            
            for i in range(0, len(cols_to_plot), 2):
                cols = st.columns(2)
                for idx, col_name in enumerate(cols_to_plot[i:i+2]):
                    with cols[idx]:
                        fig = px.histogram(
                            df,
                            x=col_name,
                            title=f'Distribution of {col_name}',
                            marginal='box'
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Correlation heatmap
            if len(numeric_cols) > 1:
                st.subheader("🔥 Correlation Heatmap")
                corr_matrix = df[numeric_cols].corr()
                
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale='RdBu_r',
                    title='Correlation Matrix'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 5. Categorical Columns Analysis
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            st.subheader("📝 Categorical Columns Analysis")
            
            # Show top categories for first few categorical columns
            for col_name in categorical_cols[:4]:  # Limit to 4 columns
                st.write(f"**{col_name}** - Top 10 Categories")
                
                value_counts = df[col_name].value_counts().head(10)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(value_counts.to_frame('Count'), use_container_width=True)
                with col2:
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        labels={'x': col_name, 'y': 'Count'},
                        title=f'Top 10 {col_name}'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # 6. Data Quality Summary
        st.subheader("✅ Data Quality Summary")
        quality_metrics = {
            'Total Cells': dataset_info['row_count'] * dataset_info['col_count'],
            'Missing Cells': df.isnull().sum().sum(),
            'Missing %': f"{(df.isnull().sum().sum() / (dataset_info['row_count'] * dataset_info['col_count']) * 100):.2f}%",
            'Duplicate Rows': df.duplicated().sum(),
            'Numeric Columns': len(numeric_cols),
            'Categorical Columns': len(categorical_cols),
        }
        
        quality_df = pd.DataFrame(list(quality_metrics.items()), columns=['Metric', 'Value'])
        st.dataframe(quality_df, use_container_width=True)
        
        st.success("✅ Full dataset analysis complete!")
        
    except Exception as e:
        st.error(f"Error during analysis: {e}")
        import traceback
        st.error(traceback.format_exc())
    
    return analysis_results
