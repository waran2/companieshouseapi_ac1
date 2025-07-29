import streamlit as st
import pandas as pd
import requests
import base64
import time
from io import BytesIO
from tqdm import tqdm

# Set page config
st.set_page_config(
    page_title="Companies House Accounts Date Extractor",
    page_icon="🏛️",
    layout="wide"
)

# Session state for tracking processed data
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

def get_company_accounts_info(company_number, api_key, session):
    """Fetch accounts information for a single company"""
    base_url = "https://api.company-information.service.gov.uk"
    
    try:
        # Get company profile
        profile_response = session.get(
            f"{base_url}/company/{company_number}",
            timeout=10
        )
        
        if profile_response.status_code != 200:
            return None
        
        profile_data = profile_response.json()
        accounts_data = profile_data.get("accounts", {})
        
        # Get filing history for filed date
        filing_response = session.get(
            f"{base_url}/company/{company_number}/filing-history",
            params={"category": "accounts", "items_per_page": 1},
            timeout=10
        )
        
        filing_data = filing_response.json() if filing_response.status_code == 200 else {}
        latest_filed_date = filing_data.get("items", [{}])[0].get("date") if filing_data.get("total_count", 0) > 0 else None
        
        return {
            "company_name": profile_data.get("company_name"),
            "accounting_reference_day": accounts_data.get("accounting_reference_date", {}).get("day"),
            "accounting_reference_month": accounts_data.get("accounting_reference_date", {}).get("month"),
            "last_made_up_to": accounts_data.get("last_accounts", {}).get("made_up_to"),
            "last_period_end": accounts_data.get("last_accounts", {}).get("period_end_on"),
            "last_period_start": accounts_data.get("last_accounts", {}).get("period_start_on"),
            "last_accounts_type": accounts_data.get("last_accounts", {}).get("type"),
            "last_accounts_filed_date": latest_filed_date,
            "next_due_on": accounts_data.get("next_accounts", {}).get("due_on"),
            "next_period_end": accounts_data.get("next_accounts", {}).get("period_end_on"),
            "next_period_start": accounts_data.get("next_accounts", {}).get("period_start_on"),
            "next_made_up_to": accounts_data.get("next_made_up_to"),
            "overdue": accounts_data.get("overdue")
        }
        
    except Exception:
        return None

def process_companies(uploaded_file, api_key):
    """Process the uploaded file with company numbers"""
    try:
        # Read input file
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        if 'company_number' not in df.columns:
            st.error("Input file must contain a 'company_number' column")
            return None
        
        # Prepare API session
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}"
        })
        
        # Process companies
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, company_number in enumerate(tqdm(df['company_number'])):
            company_number = str(company_number).strip().zfill(8)
            
            # Get company data
            company_data = get_company_accounts_info(company_number, api_key, session)
            
            if company_data:
                company_data['company_number'] = company_number
                results.append(company_data)
            
            # Update progress
            progress = (i + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"Processing {i + 1} of {len(df)} companies...")
            
            # Rate limiting
            time.sleep(0.1)
        
        progress_bar.empty()
        status_text.empty()
        
        return pd.DataFrame(results)
    
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

def create_download_link(df, filename="companies_house_data.csv"):
    """Generate a download link for the DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

# App UI
st.title("🏛️ Companies House Accounts Date Extractor")
st.markdown("""
Upload a CSV or Excel file containing company numbers to retrieve accounts dates including:
- Last accounts dates (made up to, period dates, filed date)
- Next accounts due dates
- Accounting reference dates
""")

with st.expander("🔑 API Key Setup"):
    st.markdown("""
    1. Get a free API key from [Companies House](https://developer.company-information.service.gov.uk/)
    2. The key should be in the format `your-api-key-here` (not base64 encoded)
    3. Your key will only be used during this session
    """)

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Companies House API Key", type="password")
    st.markdown("---")
    st.markdown("""
    **Note:** The free API has rate limits:
    - 600 requests per 5 minutes
    - Processing 3,000 companies takes ~30 minutes
    """)

# File upload section
uploaded_file = st.file_uploader(
    "Upload your file (CSV or Excel) with company numbers", 
    type=['csv', 'xlsx'],
    help="File must contain a 'company_number' column"
)

# Process button
if uploaded_file and api_key and st.button("Process Companies"):
    with st.spinner("Processing company data..."):
        results_df = process_companies(uploaded_file, api_key)
        
        if results_df is not None:
            st.session_state.results_df = results_df
            st.session_state.processing_complete = True
            st.success(f"Successfully processed {len(results_df)} companies!")

# Display results and download
if st.session_state.processing_complete and st.session_state.results_df is not None:
    st.subheader("Processed Data Preview")
    st.dataframe(st.session_state.results_df.head())
    
    st.markdown("### Download Results")
    st.markdown(create_download_link(st.session_state.results_df), unsafe_allow_html=True)
    
    # Show some stats
    st.markdown("### Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Companies Processed", len(st.session_state.results_df))
    
    overdue_count = st.session_state.results_df['overdue'].sum()
    col2.metric("Companies Overdue", overdue_count)
    
    filed_dates = st.session_state.results_df['last_accounts_filed_date'].notna().sum()
    col3.metric("Companies with Filed Dates", filed_count)
