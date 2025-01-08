import streamlit as st
from job_listing_logic import JobListingLogic

def main():
    st.title("Job Listing Management")

    # Check if the user is logged in
    if 'company_id' not in st.session_state:
        st.error("Please log in to access this page.")
        return

    db_path = "sure_platform.db"  # Adjust this path to match your database location
    logic = JobListingLogic(db_path)

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Create Job Listing", "View All Listings", "Delete Job Listing"])

    if choice == "Create Job Listing":
        st.subheader("Create a New Job Listing")

        # Automatically use the company_id from the session state
        company_id = st.session_state['company_id']
        st.write(f"**Company ID**: {company_id}")

        # Input fields for job listing
        job_title = st.text_input("Job Title")
        description = st.text_area("Job Description")
        requirements = st.text_area("Requirements")
        hr_questions = st.text_area("HR Questions")

        if st.button("Create Job Listing"):
            if job_title and description and requirements and hr_questions:
                # Generate a unique job_id (you can use a UUID or other method)
                job_id = f"JOB-{company_id}-{st.session_state.get('job_counter', 1)}"
                st.session_state['job_counter'] = st.session_state.get('job_counter', 1) + 1

                # Save the job listing to the database
                success, message, job_key = logic.create_job_listing(
                    job_id, company_id, job_title, description, requirements, hr_questions
                )

                if success:
                    st.success(message)
                    st.write(f"**Job Key**: {job_key}")  # Display the job_key
                else:
                    st.error(message)
            else:
                st.error("All fields are required!")

    elif choice == "View All Listings":
        st.subheader("All Job Listings")
        job_listings = logic.get_all_job_listings()

        if job_listings:
            for job in job_listings:
                st.write(f"**Job ID**: {job[0]}")
                st.write(f"**Company ID**: {job[1]}")
                st.write(f"**Job Title**: {job[2]}")
                st.write(f"**Description**: {job[3]}")
                st.write(f"**Requirements**: {job[4]}")
                st.write(f"**HR Questions**: {job[5]}")
                st.write("---")
        else:
            st.info("No job listings found.")

    elif choice == "Delete Job Listing":
        st.subheader("Delete a Job Listing")
        job_id = st.text_input("Enter Job ID to Delete")

        if st.button("Delete Job Listing"):
            if job_id:
                success, message = logic.delete_job_listing(job_id)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please provide a Job ID.")

if __name__ == "__main__":
    main()