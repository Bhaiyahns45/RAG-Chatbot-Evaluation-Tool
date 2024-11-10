import streamlit as st
import pandas as pd
import numpy as np
import time


#<--------------------------------------- Streamlit Page ---------------------------------------------------->

st.set_page_config(
    page_title='Dashboard',
    layout="wide",
    initial_sidebar_state="expanded",
)

html_temp = """
<div style="background-color:#2F396F;padding:0.7px">
<h3 style="color:white;text-align:center;" >RAG ChatBot Evaluation Dashboard</h3>
</div><br>"""

st.markdown(html_temp,unsafe_allow_html=True)

st.sidebar.image('https://imgur.com/wHe7wfS.png', width=180)

# Function to load and initialize the Excel file
@st.cache_data
def load_excel(file):
    df = pd.read_excel(file)
    if 'Score' not in df.columns:
        df['Score'] = None  # Initialize the Score column if not present
    return df

# Check if 'uploaded_file' is not in session state, to initialize it
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None  # Initialize the session state for 'uploaded_file'

# Show file uploader if the file hasn't been uploaded yet
if st.session_state['uploaded_file'] is None:
    uploaded_file = st.file_uploader("**Choose File (Excel)**", type=["xlsx", "xls"])

    # If a file is uploaded, store it in session state
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file

# Process uploaded file if it exists in session state
if st.session_state['uploaded_file'] is not None:
    # File has been uploaded, you can now process it
    st.write("File has been uploaded!")

    # Load Excel file and display in DataFrame format
    df = load_excel(st.session_state['uploaded_file'])
    df.index = np.arange(1, len(df)+1)

    with st.expander("Uploaded Data Preview"):
        st.write(df)  # Display all data for reference


    # st.markdown("<h6 style='text-align: center;'></h6>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

    # Initialize current row index and scores in session state
    if 'current_row' not in st.session_state:
        st.session_state.current_row = 0
    if 'scores' not in st.session_state:
        st.session_state.scores = df['Score'].tolist()  # Load existing scores into session state

    # Get the current row's data
    current_index = st.session_state.current_row
    current_data = df.iloc[current_index]

    # Display in chatbot-style format
    # st.write("## Chatbot Conversation View")
    # st.write(f"**Question**: {current_data.get('question', 'N/A')}")
    # st.write(f"**Answer**: {current_data.get('answer', 'N/A')}")

    with st.chat_message("user"):
        st.markdown(f"{current_index + 1}. {current_data.get('question', 'N/A')}")

    with st.chat_message("assistant"):
        response = st.write(current_data.get('answer', 'N/A'))


    st.sidebar.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

    # Show previously submitted score if available
    current_score = st.session_state.scores[current_index]
    if pd.notna(current_score):
        st.sidebar.write(f"#### Submitted Score: {int(current_score)}")
    else:
        st.sidebar.write("#### No score")

    # Slider for scoring
    score = st.sidebar.slider("Rate the answer(%)", min_value=1, max_value=100, value=int(current_score) if pd.notna(current_score) else 1)
    # st.sidebar.write("Score:", score)

    # Update the score in session state and DataFrame for the current row
    if st.sidebar.button("Submit Score"):
        st.session_state.scores[current_index] = score
        df.at[current_index, 'Score'] = score  # Update DataFrame immediately
        st.sidebar.success("Score recorded!")
        # Refresh the score display for the current row
        st.rerun()

    st.sidebar.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)
    

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Prev") and st.session_state.current_row > 0:
        st.session_state.current_row -= 1
        st.rerun()  # Rerun app to display the new row
    if col2.button("Next") and st.session_state.current_row < len(df) - 1:
        st.session_state.current_row += 1
        st.rerun()  # Rerun app to display the new row

    st.sidebar.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

    # Display other columns in an expander
    with st.expander("Additional Details"):
        for col in df.columns:
            if col not in ['question', 'answer', 'Score']:
                st.write(f"**{col.capitalize()}**: {current_data.get(col, 'N/A')}")

    # Sidebar - Export Excel file
    if st.sidebar.button("Export Scored Data"):
        # Update DataFrame with scores from session state
        df['Score'] = st.session_state.scores
        df.to_excel("Scored_Data.xlsx", index=False)
        st.sidebar.success("Excel file exported with scores!")


    if st.sidebar.button("New Upload"):
        st.session_state['uploaded_file'] = None
        st.rerun()

