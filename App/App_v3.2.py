# Made with the use of Streamlit.io
# Create a virtual Environment from the command prompt and then activate it
# use "streamlit run app.py" command in the command prompt to run the web application

###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
import re
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses1 import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos, swengg_course, blockchain_course, aiml_course, cybersec_course, dataengg_course
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

###### Preprocessing functions ######

# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# @st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def gauge_chart(score):
    if score >= 80:
        color = 'green'
    elif score >= 60:
        color = 'yellow'
    elif score >= 40:
        color = 'orange'
    else:
        color = 'red'
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Score"},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': color}}))
    
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    return fig

# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

###### Database Stuffs ######


# sql connector
connection = pymysql.connect(host='localhost',user='root',password='ABT211002',db='VTHREE')
cursor = connection.cursor()


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()

def validating_name(name): 
  
    # RegexObject = re.compile( Regular expression, flag ) 
    # Compiles a regular expression pattern into a regular expression object 
    regex_name = re.compile(r'^([a-z]+)( [a-z]+)*( [a-z]+)*$',  
              re.IGNORECASE)
  
    # RegexObject is matched with the desired  
    # string using search function 
    # In case a match is found, search() returns 
    # MatchObject Instance 
    # If match is not found, it return None 
    res = regex_name.search(name) 
  
    # If match is found, the string is valid 
    if res: 
        return True
          
    # If match is not found, string is invalid 
    else: 
        return False

def check(email):
    regex_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                re.IGNORECASE)
	# pass the regular expression
	# and the string into the fullmatch() method
    res = regex_email.fullmatch(email)

    if res:
        return True 
    else:
	    return False


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="Resume Evaluation System",
   page_icon='./Logo/RES_Logo.png',
)


###### Main function run() ######


def run():
    st.sidebar.markdown("# Navigation Sidebar")
    # st.sidebar.markdown("A Quick and easy to use Resume Analyzer that analyse resume data and extract it into machine-readable output, Helps applicants with few recommendations and helps automatically store, organize, and analyse resume data to find the best candidate.")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose an option from the following:", activities)
    st.sidebar.markdown("# Swtich to another page anytime")

    ###### Creating Database and Table ######

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS VTHREE;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        img = Image.open('./Logo/User_1.png')
        st.image(img)
	
        # Collecting Miscellaneous Information
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        geolocator = Nominatim(user_agent="http")
        location = geolocator.reverse(latlong, language='en')
        address = location.raw['address']
        cityy = address.get('city', '')
        statee = address.get('state', '')
        countryy = address.get('country', '')  
        city = cityy
        state = statee
        country = countryy

        # Upload Resume
        st.markdown('''<h5 style='text-align: left; color: white;'> Upload Your Resume to get Evaluated Data:</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume*", type=["pdf"])
        if pdf_file is not None:
            if (len(act_name) != 0) and (len(act_mail) != 0) and (len(act_mob) != 0):
                if validating_name(act_name) == True and check(act_mail) == True and act_mob.isnumeric() and (len(act_mob) == 10):

                    with st.spinner('Please wait for a moment...'):
                        time.sleep(4)

                    #if act_name is not None and act_mail is not None and act_mob is not None:

                    # if st.button('Submit'):
                    ### saving the uploaded resume to folder
                    save_image_path = './Uploaded_Resumes/'+pdf_file.name
                    pdf_name = pdf_file.name
                    with open(save_image_path, "wb") as f:
                        f.write(pdf_file.getbuffer())
                        show_pdf(save_image_path)

                    ### parsing and extracting whole resume 
                    resume_data = ResumeParser(save_image_path).get_extracted_data()
                    if resume_data:
                    
                        ## Get the whole resume data into resume_text
                        resume_text = pdf_reader(save_image_path)

                        ## Showing Analyzed data from (resume_data)
                        st.header("**Resume Evaluation**")
                        st.success("Hello "+ resume_data['name'])
                        st.subheader("**Your Basic Data**")
                        try:
                            st.text('Name: '+resume_data['name'])
                            st.text('Email: ' + resume_data['email'])
                            st.text('Contact: ' + resume_data['mobile_number'])
                            # st.text('Contact: ' + act_mob)
                            st.text('Degree: '+ str(resume_data['degree']))                    
                            st.text('Resume pages: '+ str(resume_data['no_of_pages']))

                        except:
                            pass
                        ## Predicting Candidate Experience Level 

                        ## Resume Scorer & Resume Writing Tips
                        # st.subheader("**Resume Tips & Ideas**")
                        resume_score = 0
                        
                        ### Predicting Whether these key points are added to the resume
                        if 'Objective' or 'Summary' in resume_text:
                            resume_score = resume_score + 6
        
                        if 'Education' or 'School' or 'College' or 'University'  in resume_text:
                            resume_score = resume_score + 10
                        if 'EDUCATION' or 'SCHOOL' or 'COLLEGE' or 'UNIVERSITY'  in resume_text:
                            resume_score = resume_score + 10
                            
                        if 'EXPERIENCE' in resume_text:
                            resume_score = resume_score + 12
                        elif 'Experience' in resume_text:
                            resume_score = resume_score + 12
                            
                        if 'INTERNSHIPS'  in resume_text:
                            resume_score = resume_score + 8
                        elif 'INTERNSHIP'  in resume_text:
                            resume_score = resume_score + 8
                        elif 'Internships'  in resume_text:
                            resume_score = resume_score + 8
                        elif 'Internship'  in resume_text:
                            resume_score = resume_score + 8
                
                        if 'SKILLS'  in resume_text:
                            resume_score = resume_score + 7
                        elif 'SKILL'  in resume_text:
                            resume_score = resume_score + 7
                        elif 'Skills'  in resume_text:
                            resume_score = resume_score + 7
                        elif 'Skill'  in resume_text:
                            resume_score = resume_score + 7
                            
                        if 'INTERESTS'in resume_text:
                            resume_score = resume_score + 5
                        elif 'Interests'in resume_text:
                            resume_score = resume_score + 5
                        elif 'HOBBIES'in resume_text:
                            resume_score = resume_score + 5
                        elif 'Hobbies'in resume_text:
                            resume_score = resume_score + 5
                      
                        if 'ACHIEVEMENTS' in resume_text:
                            resume_score = resume_score + 13
                        elif 'Achievements' in resume_text:
                            resume_score = resume_score + 13
                        elif 'Awards' in resume_text:
                            resume_score = resume_score + 13
                        elif 'AWARDS' in resume_text:
                            resume_score = resume_score + 13
                
                        if 'CERTIFICATIONS' in resume_text:
                            resume_score = resume_score + 14
                        elif 'Certifications' in resume_text:
                            resume_score = resume_score + 14
                        elif 'Certifications' in resume_text:
                            resume_score = resume_score + 14
                        elif 'Certification' in resume_text:
                            resume_score = resume_score + 14
                        elif 'Certificates' in resume_text:
                            resume_score = resume_score + 14
                
                        if 'PROJECTS' in resume_text:
                            resume_score = resume_score + 19
                        elif 'PROJECT' in resume_text:
                            resume_score = resume_score + 19
                        elif 'Projects' in resume_text:
                            resume_score = resume_score + 19
                        elif 'Project' in resume_text:
                            resume_score = resume_score + 19
                
                        st.subheader("**Resume Score**")
                        
                        st.markdown(
                            """
                            <style>
                                .stProgress > div > div > div > div {
                                    background-color: #d73b5c;
                                }
                            </style>""",
                            unsafe_allow_html=True,
                        )

                        ### Score Bar
                        my_bar = st.progress(0)
                        score = 0
                        for percent_complete in range(resume_score):
                            # score +=1
                            time.sleep(0.1)
                            # my_bar.progress(percent_complete + 1)
                            my_bar.progress(percent_complete)

                        st.plotly_chart(gauge_chart(resume_score), use_container_width=True)

                        ### Score
                        # st.markdown('** Your Resume Writing Score: **' + str(score))
                        # st.markdown('## Your Resume Writing Score: ' + str(resume_score))
                        # st.write('## ' + str(resume_score))
                        st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                        ## Resume Scorer & Resume Writing Tips
                        # st.subheader("**Resume Tips & Ideas**")
                        # resume_score = 0

                        # local_css("style.css")
                        
                        # text = st.markdown("# Resume Score Evaluation Explanation")

                        st.markdown(
                                """
                                <style>
                                    .streamlit-expanderHeader {
                                    font-size: 20px;
                                    }
                                </style>
                                """, unsafe_allow_html=True)

                        with st.expander("Evaluated Resume Score Explanation"):
                            ### Predicting Whether these key points are added to the resume
                            if 'Objective' or 'Summary' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                            if 'Education' or 'School' or 'College'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                            if 'EXPERIENCE' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                            elif 'Experience' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                            if 'INTERNSHIPS'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                            elif 'INTERNSHIP'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                            elif 'Internships'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                            elif 'Internship'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                            if 'SKILLS'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                            elif 'SKILL'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                            elif 'Skills'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                            elif 'Skill'  in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)
                            
                            if 'INTERESTS'in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interests/Hobbies</h4>''',unsafe_allow_html=True)
                            elif 'Interests'in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interests/Hobbies</h4>''',unsafe_allow_html=True)
                            elif 'HOBBIES'in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interests/Hobbies</h4>''',unsafe_allow_html=True)
                            elif 'Hobbies'in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interests/Hobbies</h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Interests/Hobbies. It is recommended to do so.</h4>''',unsafe_allow_html=True)

                            if 'ACHIEVEMENTS' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                            elif 'Achievements' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                            elif 'Awards' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                            elif 'AWARDS' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                            if 'CERTIFICATIONS' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                            elif 'Certifications' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                            elif 'Certifications' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                            elif 'Certification' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                            elif 'Certificates' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                            if 'PROJECTS' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                            elif 'PROJECT' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                            elif 'Projects' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                            elif 'Project' in resume_text:
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                            else:
                                st.markdown('''<h5 style='text-align: left; color: red;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)


                        ### Trying with different possibilities
                        cand_level = ''
                        if resume_data['no_of_pages'] < 1:                
                            cand_level = "NA"
                            st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                        
                        #### if internship then intermediate level
                        elif 'INTERNSHIP' in resume_text:
                            cand_level = "Intermediate"
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                        elif 'INTERNSHIPS' in resume_text:
                            cand_level = "Intermediate"
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                        elif 'Internship' in resume_text:
                            cand_level = "Intermediate"
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                        elif 'Internships' in resume_text:
                            cand_level = "Intermediate"
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                        
                        #### if Work Experience/Experience then Experience level
                        elif 'EXPERIENCE' in resume_text:
                            cand_level = "Experienced"
                            st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                        elif 'WORK EXPERIENCE' in resume_text:
                            cand_level = "Experienced"
                            st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                        elif 'Experience' in resume_text:
                            cand_level = "Experienced"
                            st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                        elif 'Work Experience' in resume_text:
                            cand_level = "Experienced"
                            st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                        else:
                            cand_level = "Fresher"
                            st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                        ## Skills Analyzing and Recommendation
                        st.subheader("**Skills Recommendation **")
                        
                        ### Current Analyzed Skills
                        keywords = st_tags(label='### Your Current Skills',
                        text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                        ### Keywords for Recommendations
                        ds_keyword = ['statistics','sql','data analysis','data visualization','graph plotting','tableau','database', 'algorithm', 'power bi', 'excel', 'r', 'big data', 'data mining']
                        web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                        android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                        ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                        uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                        swengg_keyword = ['data structures and algorithms', 'dsa', 'os', 'sql', 'C', 'JavaScript', 'Computer Networks', 'communication']
                        blockchain_keyword = ['token', 'ethereum', 'cryptocurrency', 'block', 'contract', 'bitcoin']
                        aiml_keyword = ['machine learning', 'deep learning', 'computer vision', 'artificial intelligence', 'ai', 'ml']
                        cybersec_keyword = ['information security', 'security', 'openvpn', 'nmap', 'cisco asa', 'snort' 'vulnerability assessment', 'analysis', 'firewalls', 'linux']
                        dataengg_keyword = ['database', 'data warehouse', 'business intelligence', 'innovation']
                        n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media', 'verbal skills', 'collaboration', 'team work']
                        ### Skill Recommendations Starts                
                        recommended_skills = []
                        reco_field = ''
                        rec_course = ''

                        ### condition starts to check skills from keywords and predict field
                        for i in resume_data['skills']:
                        
                            #### Data science recommendation
                            if i.lower() in ds_keyword:
                                print(i.lower())
                                reco_field = 'Data Science'
                                st.success("** Our analysis says you are suitable for Data Science Jobs.**")
                                recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from System',value=recommended_skills,key = '2')
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(ds_course)
                                break

                            #### Web development recommendation
                            elif i.lower() in web_keyword:
                                print(i.lower())
                                reco_field = 'Web Development'
                                st.success("** Our analysis says you are suitable for Web Development Jobs **")
                                recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from System',value=recommended_skills,key = '3')
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(web_course)
                                break

                            #### Android App Development
                            elif i.lower() in android_keyword:
                                print(i.lower())
                                reco_field = 'Android Development'
                                st.success("** Our analysis says you are suitable for Android App Development Jobs **")
                                recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from System',value=recommended_skills,key = '4')
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(android_course)
                                break

                            #### IOS App Development
                            elif i.lower() in ios_keyword:
                                print(i.lower())
                                reco_field = 'IOS Development'
                                st.success("** Our analysis says you are suitable for IOS App Development Jobs **")
                                recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from System',value=recommended_skills,key = '5')
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(ios_course)
                                break

                            #### Ui-UX Recommendation
                            elif i.lower() in uiux_keyword:
                                print(i.lower())
                                reco_field = 'UI-UX Development'
                                st.success("** Our analysis says you are suitable for UI-UX Development Jobs **")
                                recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from System',value=recommended_skills,key = '6')
                                st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(uiux_course)
                                break
                            
                            ## software engineering/development recommendation
                            elif i.lower() in swengg_keyword:
                                print(i.lower())
                                reco_field = 'Software Development / Engineering'
                                st.warning("** Our analysis says you are suitable for Software Engineering / Development Jobs **")
                                recommended_skills = ['source control', 'computing', 'debugging', 'database management', 'MongoDB', 'compiling', 'testing']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from system',value=recommended_skills,key = '7')
                                st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(swengg_course)
                                break

                            ## blockchain recommendation
                            elif i.lower() in blockchain_keyword:
                                print(i.lower())
                                reco_field = 'Blockchain'
                                st.warning("** Our analysis says you are suitable for Blockchain Jobs **")
                                recommended_skills = ['decentralization', 'fork', 'mining', 'nodes', 'staking', 'digital mining', 'consensus', 'dao']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from system',value=recommended_skills,key = '8')
                                st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(blockchain_course)
                                break

                            ## aiml recommendation
                            elif i.lower() in aiml_keyword:
                                print(i.lower())
                                reco_field = 'AIML'
                                st.warning("** Our analysis says you are suitable for Artificial Intelligence / Machine Learning Jobs **")
                                recommended_skills = ['tensorflow', 'pytorch', 'python', 'neural networks', 'modelling', 'natural language processing']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from system',value=recommended_skills,key = '9')
                                st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                # rec_course = course_recommender(aiml_course)
                                break

                            ## software engineering/development recommendation
                            elif i.lower() in cybersec_keyword:
                                print(i.lower())
                                reco_field = 'CyberSecurity Specialist'
                                st.warning("** Our analysis says you are suitable for CyberSecurity Jobs **")
                                recommended_skills = ['compliance', 'risk management', 'malware', 'botnet', 'mitigation', 'attack vector']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from system',value=recommended_skills,key = '10')
                                st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(cybersec_course)
                                break

                            ## software engineering/development recommendation
                            elif i.lower() in dataengg_keyword:
                                print(i.lower())
                                reco_field = 'Data Engineering'
                                st.warning("** Our analysis says you are suitable for Data Engineering Jobs **")
                                recommended_skills = ['etl', 'scripting', 'azure', 'aws', 'modelling', 'scala', 'analysis', 'hadoop', 'spark']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Recommended skills generated from system',value=recommended_skills,key = '11')
                                st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = course_recommender(dataengg_course)
                                break

                            #### For Not Any Recommendations
                            elif i.lower() in n_any:
                                print(i.lower())
                                reco_field = 'NA'
                                st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                                recommended_skills = ['No Recommendations']
                                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                text='Currently No Recommendations',value=recommended_skills,key = '11')
                                st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                                # course recommendation
                                rec_course = "Sorry! Not Available for this Field"
                                break

                        # st.markdown(recommended_skills)
                        #for j in recommended_skills:
                            #if j in 

                        ### Getting Current Date and Time
                        ts = time.time()
                        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                        timestamp = str(cur_date+'_'+cur_time)


                        # Calling insert_data to add all the data into user_data                
                        insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                        st.markdown("### Add a bonus to your resume and career! Below are the recommended videos to upgrade your resume and interview tips.")
                        
                        tab1, tab2 = st.tabs(["Resume Tips", "Interview Tips"])

                        with tab1:
                            ## Recommending Resume Writing Video
                            st.header("**Bonus Video for Resume Writing Tips**")
                            resume_vid = random.choice(resume_videos)
                            st.video(resume_vid)

                        with tab2:
                            ## Recommending Interview Preparation Video
                            st.header("**Bonus Video for Interview Tips**")
                            interview_vid = random.choice(interview_videos)
                            st.video(interview_vid)

                        # ## On Successful Result 
                        # st.spinner("Loading...")
                else:
                    if validating_name(act_name) == False:
                        st.error("Please enter a valid name")
                    elif check(act_mail) == False:
                        st.error("Please enter a valid email")
                    elif len(act_mob) != 10:
                        st.error("Please enter a valid contact number")
            
            else:
                st.error('Please fill all the details...')

        # else:
        #     st.error('Something went wrong..')
                    #else:
                    # st.write("Please fill all the details to continue.")    


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        img2 = Image.open('./Logo/Feedback_2.png')
        st.image(img2)

        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.markdown("### Feedback Form")            
            feed_name = st.text_input(' Name*')
            feed_email = st.text_input('* Email*')
            feed_score = st.slider('Rate our tool on a scale of 1 to 5', 1, 5)
            comments = st.text_input('Comment your opinion')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.spinner()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.bar(y=values, x=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        img3 = Image.open('./Logo/AboutUs_4.png')
        st.image(img3)
        
        st.subheader("**About The Tool: Resume Evaluation System**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>
                    
        <p align='justify'>
            A Quick and easy to use Resume Analyzer that analyse resume data and extract it into machine-readable output, Helps applicants with few recommendations and helps automatically store, organize, and analyse resume data to find the best candidate.        
        </p>

        <p align="justify">
            <b><h2>How to use the RES Tool:  </h2></b>
            <b><h2>User </h2></b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Your uploaded resume will be visible to you, once uploaded successfully.<br/><br/>
            Our Tool will then extract the data from your resume to make it possible to analyze and evaluate to show you the information regarding the same in an organized form.<br/><br/>
            <b><h2>Feedback </h2></b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            Simply, rate our tool with on a scale of 1 to 5, 1 being the least satisfactory response and 5 being the best response. <br/><br/>
            Other than that, you can type your feedback on your own which is optional, and totally upto you. <br/><br/>
            <b><h2>Admin </h2></b> <br/>
            For login use <b>admin</b> as username and <b>adminpwd</b> as password.<br/>
            It will load all the data till this time about all the users that have used the app and perform analysis. <br/><br/>
            It is basically the analysis of all the data our tool has been used for, till now. It consists of the data from the User page and also the feedback. <br/><br/>
            Other than that, it shows the analysis of all this data using data visualization.
        </p><br/><br/>

        ''',unsafe_allow_html=True)


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        img4 = Image.open('./Logo/Admin_3.png')
        st.image(img4)

        st.markdown('### Enter your Admin Credentials to Login:')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'adminpwd':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Total %d " % values + " Users Have Used The Tool.")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                # csv = convert_df(df)

                ## Downloading Report of user_data in csv file
                # st.download_button(
                #     label="Download data as CSV",
                #     data=csv,
                #     file_name='User_Data.csv',
                #     mime='text/csv',
                # )

                # btn = st.button("Download Report")
                # if btn:
                #     get_csv_download_link(df, 'User_Data.csv')
                # st.button(get_csv_download_link(df,'User_Data.csv','Download Report'))
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                
                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**Users Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Feedback Ratings**")
                fig = px.bar(y=values, x=labels, title="Graph of User Rating Score From 1 - 5")
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()
                # x = plot_data.resume_score.unique()
                # y = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)
                # fig = px.bar(df, x, y)
                # st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                tab3, tab4, tab5 = st.tabs(["City", "State", "Country"])

                # with tab1:
                # st.header("City Piechart")
                # with tab2:
                # st.header("State PieChart")
                # with tab3:
                # st.header("Country PieChart")
                # fetching City from the query and getting the unique values and total value count
                with tab3:
                    labels = plot_data.City.unique()
                    values = plot_data.City.value_counts()

                    # Pie chart for City
                    st.subheader("**Pie-Chart for City**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                    st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                with tab4:
                    labels = plot_data.State.unique()
                    values = plot_data.State.value_counts()

                    # Pie chart for State
                    st.subheader("**Pie-Chart for State**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                    st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count
                with tab5: 
                    labels = plot_data.Country.unique()
                    values = plot_data.Country.value_counts()

                    # Pie chart for Country
                    st.subheader("**Pie-Chart for Country**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                    st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Invalid Credentials")

# Calling the main (run()) function to make the whole process run
run()
