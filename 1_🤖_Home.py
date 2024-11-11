import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Set up the Streamlit page configuration
st.set_page_config(
    page_title='Dashboard',
    layout="wide",
    initial_sidebar_state="expanded",
)

# HTML template for the page header
html_temp = """
<div style="background-color:#2F396F;padding:0.7px">
<h3 style="color:white;text-align:center;" >RAG ChatBot Evaluation Dashboard</h3>
</div><br>"""

# Render the page header
st.markdown(html_temp, unsafe_allow_html=True)

# Sidebar image for branding or identity
st.sidebar.image('https://imgur.com/wHe7wfS.png', width=180)

# Function to load and initialize the Excel file
@st.cache_data
def load_excel(file):
    """Loads the uploaded Excel file and initializes the 'Score' column if not present."""
    df = pd.read_excel(file)
    if 'Score' not in df.columns:
        df['Score'] = None  # Initialize the Score column if not present
    return df

# Initialize session state variables if not already set
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None  # Store the uploaded file

# Show file uploader if the file hasn't been uploaded yet
if st.session_state['uploaded_file'] is None:
    uploaded_file = st.file_uploader("**Choose File (Excel)**", type=["xlsx", "xls"])

    # If a file is uploaded, store it in session state
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file

# Process the uploaded file if it exists in session state
if st.session_state['uploaded_file'] is not None:
    # Display a message confirming file upload
    st.write("File has been uploaded!")

    # Load Excel file and display in DataFrame format
    df = load_excel(st.session_state['uploaded_file'])
    df.index = np.arange(1, len(df)+1)  # Adjust the index for better display

    # Expandable section to preview the uploaded data
    with st.expander("Uploaded Data Preview"):
        st.write(df)  # Display the entire DataFrame

    # Divider between sections
    st.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

    # Initialize current row index and scores in session state if not already set
    if 'current_row' not in st.session_state:
        st.session_state.current_row = 0
    if 'scores' not in st.session_state:
        st.session_state.scores = df['Score'].tolist()  # Load existing scores into session state

    # Get the current row's data for display
    current_index = st.session_state.current_row
    current_data = df.iloc[current_index]

    # Display the current row data in a chatbot-style format
    with st.chat_message("user"):
        st.markdown(f"{current_index + 1}. {current_data.get('question', 'N/A')}")

    with st.chat_message("assistant"):
        st.write(current_data.get('answer', 'N/A'))

    # Sidebar divider for score submission
    st.sidebar.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

    # Show previously submitted score if available
    current_score = st.session_state.scores[current_index]
    if pd.notna(current_score):
        st.sidebar.write(f"#### Submitted Score: {int(current_score)}")
    else:
        st.sidebar.write("#### No score")

    # Slider for scoring the current answer
    score = st.sidebar.slider("Rate the answer(%)", min_value=1, max_value=100, value=int(current_score) if pd.notna(current_score) else 1)

    # Update the score in session state and DataFrame for the current row
    if st.sidebar.button("Submit Score"):
        st.session_state.scores[current_index] = score
        df.at[current_index, 'Score'] = score  # Update DataFrame immediately
        st.sidebar.success("Score recorded!")
        # Refresh the score display for the current row
        st.rerun()

    # Sidebar buttons for navigation (Prev/Next)
    st.sidebar.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)
    col1, col2 = st.sidebar.columns(2)

    # Navigation buttons to move through the rows
    if col1.button("Prev") and st.session_state.current_row > 0:
        st.session_state.current_row -= 1
        st.rerun()  # Rerun the app to display the new row
    if col2.button("Next", disabled=(st.session_state.current_row == len(df) - 1)) and st.session_state.current_row < len(df) - 1:
        st.session_state.current_row += 1
        st.rerun()  # Rerun the app to display the new row

    # Sidebar section for additional details (other columns in the DataFrame)
    st.sidebar.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)
    with st.expander("Additional Details"):
        for col in df.columns:
            if col not in ['question', 'answer', 'Score']:
                st.write(f"**{col.capitalize()}**: {current_data.get(col, 'N/A')}")


    # Initialize session state for scores if it doesn't exist
    if 'scores' not in st.session_state:
        st.session_state.scores = [None] * len(df)  # Initialize with None for each question


    # Update DataFrame with scores from session state
    df['Score'] = st.session_state.scores
    
    # Save to a BytesIO stream to avoid writing to disk
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Scores')
    output.seek(0)  # Move pointer to the start for reading

    # Provide download button
    if st.sidebar.download_button(
        label="Download Scored Data",
        data=output,
        file_name="Scored_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        st.sidebar.success("Scored Data download!")

    # Button for starting a new file upload
    if st.sidebar.button("New Upload"):
        st.session_state['uploaded_file'] = None
        st.rerun()  # Rerun the app to reset the uploaded file state
