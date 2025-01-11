import streamlit as st
import subprocess

def main():
    st.title("Company Dashboard")

    # Redirect buttons
    if st.button("Create Job Listing"):
        # Redirect to the Create Job Listing section within job_listing_page.py
        subprocess.run(["streamlit", "run", "job_listing_page.py", "--", "Create Job Listing"])

    if st.button("View All Listings"):
        # Redirect to the View All Listings section within job_listing_page.py
        subprocess.run(["streamlit", "run", "job_listing_page.py", "--", "View All Listings"])

    if st.button("View All Scheduled Interviews"):
        # Placeholder for future scheduled interviews page
        subprocess.run(["streamlit", "run", "view_all_interviews.py"])

if __name__ == "__main__":
    main()
