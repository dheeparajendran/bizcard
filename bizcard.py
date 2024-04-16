import streamlit as st 
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

def image_to_text(path):

    input_image = Image.open(path)

    #Converting Image into Array Format

    image_array = np.array(input_image)

    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_array,detail= 0)

    return text,input_image

def extracted_text(texts):

    extrd_dict = {"NAME" : [], 
                  "DESIGNATION" : [], 
                  "CONTACT" : [] ,
                  "COMPANY_NAME" :[] , 
                  "EMAIL" : [], 
                  "WEBSITE" : [], 
                  "ADDRESS" : [],
                  "PINCODE" :[]}
    
    extrd_dict["NAME"].append(texts[0])
    extrd_dict["DESIGNATION"].append(texts[1])
    

    for i in range(2 ,len(texts)):

        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):

            extrd_dict["CONTACT"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:

            extrd_dict["EMAIL"].append(texts[i])

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or  "wWw" in texts[i] or "wwW" in texts[i]:

            smallcase = texts[i].lower()
            extrd_dict["WEBSITE"].append(smallcase)

        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():

            extrd_dict["PINCODE"].append(texts[i])

        elif re.match(r'^[A-Za-z]', texts[i]):

            extrd_dict["COMPANY_NAME"].append(texts[i])  # Use strip() to remove leading/trailing spaces

        else:

            remove_colon = re.sub(r'[,:]','',texts[i])
            extrd_dict["ADDRESS"].append(remove_colon)

    for key,value in extrd_dict.items():

        if len(value)>0:
           
           concatenate = " ".join(value)
           extrd_dict[key] = [concatenate]

        else:
            
            extrd_dict[key] = ["NA"]

    return extrd_dict


#STREAMLIT PART 

# SETTING PAGE CONFIGURATIONS

st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR | By DHEEPA",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """# This OCR app is created by * DHEEPA*!"""})
st.markdown("<h1 style='text-align: center; color: blue;'>BizCardX:Extracting Business Card Data with OCR</h1>",
            unsafe_allow_html=True)

# SETTING-UP BACKGROUND IMAGE

def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background:url("https://wallpapers.com/images/featured/plain-zoom-background-d3zz0xne0jlqiepg.jpg");
                        background-size: cover}}
                     </style>""", unsafe_allow_html=True)


setting_bg()


with st.sidebar:

    select = option_menu(None,
                        options = ["HOME","UPLOAD AND MODIFY","DELETE"],
                        icons=["house","cloud-upload","pencil-square"],
                        default_index=0,
                        orientation="horizantal")

if select == "HOME":
            
    col1 , col2 = st.columns(2)

    with col1:
        st.image(Image.open("C:/Users/user/OneDrive/Desktop/biz.jpg"),width =350)    
        st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")

    with col2:

        st.write("## :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
        st.write('## The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

        

elif select == "UPLOAD AND MODIFY":
    img = st.file_uploader("Upload the Image ", type= ["png","jpg","jpeg"],label_visibility="hidden")

    if img is not None:

        st.image(img, width=400)

        text_imag,input_image = image_to_text(img)

        text_data = extracted_text(text_imag)
        
        if text_data:
            st.success("TEXT IS EXTRACTED SUCCESSFULLY")

        df = pd.DataFrame(text_data)

        #converting Image to Bytes

        Image_bytes = io.BytesIO()

        input_image.save(Image_bytes, format= "PNG")

        image_data = Image_bytes.getvalue()

        #Creating Dictionary

        data = {"IMAGE" : [image_data]}

        df_1 = pd.DataFrame(data)

        concat_df = pd.concat([df,df_1],axis =1) #it will assisgn 

        st.dataframe(concat_df)

        button_1 = st.button("SAVE",use_container_width=True)

        if button_1:
                                                    
            mydb = sqlite3.connect("bizcardx.db") #SQL CONNECTION
            cursor = mydb.cursor()

            #Table Creation

            create_query = '''CREATE TABLE if not exists bizcard_details(name varchar(200),
                                                                        designation varchar(200),
                                                                        contact varchar(200),
                                                                        company_name varchar(200),
                                                                        email varchar(200),
                                                                        website text,
                                                                        address text,
                                                                        pincode varchar(200),
                                                                        image text)'''

            cursor.execute(create_query)
            mydb.commit()
            
             #INSERT QUERY

            insert_query = '''INSERT INTO bizcard_details(name,designation,contact,company_name,email,
                                                        website,address,pincode,image)
                                                        
                                                        values(?,?,?,?,?,?,?,?,?)'''

            datas = concat_df.values.tolist()[0]
            cursor.execute(insert_query,datas)
            mydb.commit()

            st.success("SAVED SUCCESSFULLY")
    
    method = st.radio("Select the Method",["Preview","Modify"]) 

    if method == "Preview":

        mydb = sqlite3.connect("bizcardx.db")
        cursor = mydb.cursor()
        
        #SELECT QUERY

        select_query = "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table,columns=["NAME","DESIGNATION","CONTACT","COMPANY_NAME","EMAIL",
                                                    "WEBSITE","ADDRESS","PINCODE","IMAGE"])
        st.dataframe(table_df)

    elif method == "Modify":
        
        mydb = sqlite3.connect("bizcardx.db")
        cursor = mydb.cursor()

        #SELECT QUERY

        select_query = "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table,columns=["NAME","DESIGNATION","CONTACT","COMPANY_NAME","EMAIL",
                                                    "WEBSITE","ADDRESS","PINCODE","IMAGE"])
        
        col1,col2 = st.columns(2)

        with col1:

            selected_name = st.selectbox("Select the Name",table_df["NAME"])

        df_3 = table_df[table_df["NAME"] == selected_name]

        df_4 = df_3.copy()

        col1,col2 = st.columns(2)
        with col1:
            
            modify_name = st.text_input("Name",df_3["NAME"].unique()[0])
            modify_desig = st.text_input("Designation",df_3["DESIGNATION"].unique()[0])
            modify_contact = st.text_input("Contact",df_3["CONTACT"].unique()[0])
            modify_company = st.text_input("Company_name",df_3["COMPANY_NAME"].unique()[0])
            modify_email = st.text_input("Email",df_3["EMAIL"].unique()[0])

            df_4["NAME"] = modify_name
            df_4["DESIGNATION"] = modify_desig
            df_4["CONTACT"] = modify_contact
            df_4["COMPANY_NAME"] = modify_company
            df_4["EMAIL"] = modify_email

                
        with col2:

            modify_website = st.text_input("Website",df_3["WEBSITE"].unique()[0])
            modify_add = st.text_input("Address",df_3["ADDRESS"].unique()[0])
            modify_pin = st.text_input("Pincode",df_3["PINCODE"].unique()[0])
            modify_imag = st.text_input("Image",df_3["IMAGE"].unique()[0])
            
            
            df_4["WEBSITE"] = modify_website
            df_4["ADDRESS"] = modify_add
            df_4["PINCODE"] = modify_pin
            df_4["IMAGE"] = modify_imag

            st.dataframe(df_4)

        col1,col2 = st.columns(2)
        with col1:
            button_3 = st.button("Modify",use_container_width= True)

            if button_3:
                
                mydb = sqlite3.connect("bizcardx.db")
                cursor = mydb.cursor()

                cursor.execute(f"DELETE from bizcard_details WHERE name= '{selected_name}' ")
                mydb.commit()

                                
                insert_query = '''INSERT INTO bizcard_details(name,designation,contact,company_name,email,
                                                            website,address,pincode,image)
                                                            
                                                            values(?,?,?,?,?,?,?,?,?)'''

                datas = concat_df.values.tolist()[0]
                cursor.execute(insert_query,datas)
                mydb.commit()

                st.success('updated successfully', icon="✅")

elif select == "DELETE":
    
    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()

    col1,col2 = st.columns([4,4])

    with col1:

        select_query = "select NAME from bizcard_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()

        names = ["Select"]

        for i in table:
            names.append(i[0])

        name_select = st.selectbox("Select The Name to Delete", options = names)
    
    with col2:

        select_query = f"select DESIGNATION from bizcard_details  where NAME = '{name_select}' "

        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()

        designations = ["Select"]

        for j in table:
            designations.append(j[0])

        designation_select = st.selectbox("Select The Designation of the chosen Name", options = designations)
    
    st.markdown(" ")


    if name_select and designation_select:
    
        col1,col2,col3 = st.columns([5,3,3])

        with col1:
            st.write(f"Selected Name : {name_select}")
            st.write("")
            st.write("")
            st.write("")
            st.write(f" Selected Designation :  {designation_select}")

        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
             
            remove = st.button("Click here to Delete", use_container_width = True)

            if remove:
                cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{name_select}' AND DESIGNATION = '{designation_select}'")
                mydb.commit()

                st.warning('DELETED', icon="⚠️")