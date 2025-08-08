# README.md content
echo "# Companies House Accounts Date Portal

Streamlit application for extracting company accounts dates from Companies House API.

## Features
- Bulk processing of company numbers
- Automatic date extraction (filed dates, due dates)
- CSV/Excel file support

## Installation
\`\`\`bash
git clone https://github.com/yourusername/companies-house-portal.git
cd companies-house-portal
pip install -r requirements.txt
\`\`\`

## Usage
\`\`\`bash
streamlit run app/frontend/dashboard.py
\`\`\`

## Configuration
Add your Companies House API key in \`.streamlit/secrets.toml\`:
\`\`\`toml
COMPANIES_HOUSE_API_KEY = \"your-api-key-here\"
\`\`\`

#Deployment tutorial
https://www.youtube.com/watch?v=oynd7Xv2i9Y
" 
AWS EC2 deplyment:
Connect to the session
Run Sudo su
Run yum update
Run yum install git
Run git clone https://github.com/waran2/companieshouseapi_ac1.git

--step into the folder using cd command
Run cd companieshouseap_ac1
Run yum install python3-pip
Run python3 -m pip install -r requirement.txt

if error: run python3 -m pip install --ignore-installed streamlit

Run python3 -m streamlit run main.py


To Edit: nano st main.py
ctrl + s to save
ctrl + x to exit

Continous running: nohub python3 -m streamlit run main.py
To stop: Run ps -ef and get the PID for the streamlit ap then run kill [PID]


> README.md
