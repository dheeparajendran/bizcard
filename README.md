BizCardX: Business Card Data Extraction using OCR

BizCardX is a Streamlit web application designed to effortlessly extract data from business cards using Optical Character Recognition (OCR) technology. With BizCardX, users can easily upload images of business cards, and the application leverages the powerful easyOCR library to extract pertinent information from the cards. The extracted data is then presented in a user-friendly format and can be stored in a MySQL database for future reference and management.

Prerequisites
To successfully run and deploy BizCardX, ensure you have the following prerequisites in place:

Python environment (Python 3.x recommended) Necessary libraries installed: 

Streamlit, Pandas, easyOCR, PIL, re, sqlite3.A functioning MySQL server setup Features Home The home section of BizCardX provides users with an introduction to the application, outlining the technologies utilized and offering a concise overview of its capabilities.

Upload & Modify

This pivotal section empowers users to upload images of business cards. Once an image is uploaded, BizCardX undertakes the image processing using the easyOCR library to extract essential details from the card. The extracted information encompasses:

Modify

The modify section of BizCardX allows users to interact with the data extracted from business cards. Through a user-friendly dropdown menu, users can select specific entries from the database. This selection enables them to either update or delete the chosen entry. Any modifications performed are promptly saved in the database.

Delete

If we delete any entries from the table table we delete based on name and designation.
