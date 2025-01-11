import streamlit as st
from job_listing_logic import JobListingLogic

def main():
    st.title("Job Listing Management")

    db_path = "recruitment_platform.db"  # Adjust this path to match your database location
    logic = JobListingLogic(db_path)

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Create Job Listing", "View All Listings", "Delete Job Listing"])

    if choice == "Create Job Listing":
        st.subheader("Create a New Job Listing")

        job_id = st.text_input("Enter Job ID")
        company_id = st.text_input("Enter Company ID")
        job_title = st.text_input("Enter Job Title")
        description = st.text_area("Enter Job Description")
        skills = st.text_input("Enter Required Skills (comma-separated)")
        openings = st.number_input("Enter Number of Openings", min_value=1, step=1)
        targeted_bootcamp = st.text_input("Enter Targeted Bootcamp")

        if st.button("Create Job Listing"):
            if job_id and company_id and job_title and description and skills and openings and targeted_bootcamp:
                success, message = logic.create_job_listing(
                    job_id, company_id, job_title, description, skills, openings, targeted_bootcamp
                )
                if success:
                    st.success(message)
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
                st.write(f"**Skills**: {job[4]}")
                st.write(f"**Openings**: {job[5]}")
                st.write(f"**Targeted Bootcamp**: {job[6]}")
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
