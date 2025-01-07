import streamlit as st
import sqlite3

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('Alawi_platform.db')
    return conn

# Function to create a new company (Sign Up)
def sign_up(comp_name, representative, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO Company (comp_name, representative, password)
        VALUES (?, ?, ?)
        ''', (comp_name, representative, password))
        conn.commit()
        st.success("Company account created successfully! Please log in.")
    except sqlite3.IntegrityError:
        st.error("Error: Company name already exists. Please choose a different name.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        conn.close()

# Function to authenticate a company (Log In)
def log_in(comp_name, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM Company WHERE comp_name = ? AND password = ?
    ''', (comp_name, password))
    company = cursor.fetchone()
    conn.close()
    return company

# Streamlit app
def main():
    st.title("Company Sign Up / Log In")

    # Check if the company is logged in
    if 'company_id' not in st.session_state:
        # Display the login/signup page
        menu = st.sidebar.radio("Menu", ["Sign Up", "Log In"])

        if menu == "Sign Up":
            st.header("Sign Up")
            comp_name = st.text_input("Company Name")
            representative = st.text_input("Representative Name")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Sign Up"):
                if password == confirm_password:
                    sign_up(comp_name, representative, password)
                else:
                    st.error("Passwords do not match. Please try again.")

        elif menu == "Log In":
            st.header("Log In")
            comp_name = st.text_input("Company Name")
            password = st.text_input("Password", type="password")

            if st.button("Log In"):
                company = log_in(comp_name, password)
                if company:
                    st.session_state['company_id'] = company[0]  # Store company ID in session state
                    st.session_state['comp_name'] = company[1]   # Store company name in session state
                   
                else:
                    st.error("Invalid company name or password. Please try again.")

    else:
        # If the company is logged in, display the job listing page
        import job_listing_app
        job_listing_app.main()

# Run the app
if __name__ == "__main__":
    main()