import streamlit as st

# Homepage
def home_page():
    st.title("Welcome to مُيسِّر")
    st.markdown("### Revolutionizing Recruitment with AI-Powered Features")
    st.markdown("---")
    st.subheader("Choose Your Role")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Job Seeker"):
            st.session_state["role"] = "job_seeker"

    with col2:
        if st.button("HR Representative"):
            st.session_state["role"] = "hr"

# Job Seeker Dashboard
def job_seeker_page():
    st.title("Job Seeker Dashboard")
    st.markdown("### Upload Your Resume and Manage Interviews")
    
    # Resume Upload
    st.file_uploader("Upload Resume (PDF, DOCX)", type=["pdf", "docx"])
    
    # Capture or Upload Photo
    st.camera_input("Capture or Upload Your Self-Portrait")
    
    # Name Input
    name = st.text_input("Full Name")
    
    # National ID Input
    national_id = st.text_input("National ID")
    
    # Bootcamp Multi-select
    bootcamp_options = ["UI/UX Design", "AI Models", "Software Engineering"]
    bootcamps = st.multiselect("Select Your Bootcamp(s)", options=bootcamp_options)
    
    # Submit Button
    if st.button("Submit"):
        if name and national_id and bootcamps:
            st.session_state["next_page"] = "job_seeker_next"
            st.session_state["user_data"] = {
                "name": name,
                "national_id": national_id,
                "bootcamps": bootcamps,
            }
            st.success("Details submitted successfully! Proceeding to the next step...")
        else:
            st.error("Please fill in all the required details.")

# Job Seeker Next Page
def job_seeker_next_page():
    st.title("Job Seeker Dashboard - Next Steps")
    st.markdown("### Thank you for submitting your details!")
    st.write(f"Name: {st.session_state['user_data']['name']}")
    st.write(f"National ID: {st.session_state['user_data']['national_id']}")
    st.write("Bootcamps: " + ", ".join(st.session_state["user_data"]["bootcamps"]))
    st.markdown("---")
    st.markdown("#### Next steps will be provided here...")
    if st.button("Back to Home"):
        st.session_state["role"] = "home"
        st.session_state["next_page"] = "job_seeker_page"

# HR Dashboard Pages
def jobs_posted_page():
    st.subheader("Jobs Posted")
    # Display current jobs
    if st.session_state["jobs"]:
        for i, job in enumerate(st.session_state["jobs"]):
            st.markdown(f"**{i+1}. {job['title']}**")
            st.write(f"**Description:** {job['description']}")
            st.write(f"**Skills Required:** {', '.join(job['skills'])}")
            st.write(f"**Education Requirements:** {job['education']}")
            st.write(f"**Openings:** {job['openings']}")
            st.write(f"**Targeted Bootcamp Graduates:** {', '.join(job['bootcamps'])}")
            st.markdown("---")
    else:
        st.write("No jobs posted yet.")
    
    # Button to create a new job posting
    if st.button("Create a Job Posting"):
        st.session_state["create_job"] = True
    
    # Job Posting Form
    if "create_job" in st.session_state and st.session_state["create_job"]:
        st.markdown("### Create a New Job Posting")
        job_title = st.text_input("Job Title")
        job_description = st.text_area("Job Description")
        skills = st.text_input("Skills Required (comma-separated)")
        education = st.text_input("Education Requirements")
        openings = st.number_input("Number of Openings", min_value=1)
        
        # Bootcamp Multi-select
        bootcamp_options = ["UI/UX Design", "AI Models", "Software Engineering"]
        targeted_bootcamps = st.multiselect("Target Specific Bootcamp Graduates", options=bootcamp_options)

        if st.button("Submit Job Posting"):
            if job_title and job_description and skills and education and openings and targeted_bootcamps:
                st.session_state["jobs"].append({
                    "title": job_title,
                    "description": job_description,
                    "skills": [s.strip() for s in skills.split(",")],
                    "education": education,
                    "openings": openings,
                    "bootcamps": targeted_bootcamps,
                })
                st.session_state["create_job"] = False
                st.success("Job posting created successfully!")
            else:
                st.error("Please fill in all the required details.")

def interviews_page():
    st.subheader("Interviews")
    # Placeholder for interview data
    if "interviews" not in st.session_state:
        st.session_state["interviews"] = [
            {
                "name": "Alice Johnson",
                "summary": "Alice demonstrated excellent problem-solving skills during the interview.",
                "transcript": "Full transcript of Alice Johnson's interview goes here...",
            },
            {
                "name": "Bob Smith",
                "summary": "Bob showcased strong communication skills and teamwork experience.",
                "transcript": "Full transcript of Bob Smith's interview goes here...",
            },
        ]

    for i, interview in enumerate(st.session_state["interviews"]):
        st.markdown(f"**{i+1}. {interview['name']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"View Summary ({interview['name']})"):
                st.write(f"**Summary:** {interview['summary']}")
        
        with col2:
            if st.button(f"View Transcript ({interview['name']})"):
                st.write(f"**Transcript:** {interview['transcript']}")
        
        st.markdown("---")

# HR Representative Dashboard
def hr_page():
    if "jobs" not in st.session_state:
        st.session_state["jobs"] = []

    if "hr_registered" not in st.session_state:
        st.session_state["hr_registered"] = False

    if not st.session_state["hr_registered"]:
        st.title("HR Representative Dashboard")
        st.markdown("### Register as HR Representative")
        
        # Organization and Personal Details
        org_name = st.text_input("Organization Name")
        hr_name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        phone = st.text_input("Your Phone Number")
        password = st.text_input("Password", type="password")
        
        if st.button("Submit HR Details"):
            if org_name and hr_name and email and phone and password:
                st.session_state["hr_registered"] = True
                st.session_state["hr_page"] = "jobs_posted"
                st.success("Details submitted successfully!")
            else:
                st.error("Please fill in all the required details.")
    else:
        # Navigation for HR Pages
        st.sidebar.title("HR Navigation")
        page = st.sidebar.radio("Go to", ["Jobs Posted", "Interviews"])

        if page == "Jobs Posted":
            jobs_posted_page()
        elif page == "Interviews":
            interviews_page()

# Main App Logic
if "role" not in st.session_state:
    st.session_state["role"] = "home"
if "next_page" not in st.session_state:
    st.session_state["next_page"] = "job_seeker_page"

if st.session_state["role"] == "home":
    home_page()
elif st.session_state["role"] == "job_seeker" and st.session_state["next_page"] == "job_seeker_page":
    job_seeker_page()
elif st.session_state["role"] == "job_seeker" and st.session_state["next_page"] == "job_seeker_next":
    job_seeker_next_page()
elif st.session_state["role"] == "hr":
    hr_page()
