# PHM-Alumni-Dashboard
An interactive Streamlit dashboard for exploring where ΨHM fraternity alumni live and work. Loads a local data.csv with location, job, and company columns, then renders KPI tiles, top-N bar charts for companies and locations, and a clustered view of job titles (e.g. "Cybersecurity Supervisor" and "Cyber Security Specialist" group together) shown as both a bar chart and a word cloud. Includes sidebar filters, full-text search over the alumni records, and a filtered-CSV download.

First run pip install -r requirements.txt to install needed packages.
Then run with streamlit run app.py.
