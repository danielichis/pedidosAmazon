#import pdfplumber
import fitz  # PyMuPDF
import re

def extract_prod_condition_pdf(pdf_path:str)->list:
    #pdf_path="D:/unalukaBots/unalukaBots/downloads/114-5063002-9487454.pdf"
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    print(text)
    product_conditions = re.findall(r"Condition:\s*(\w+)", text)
    if product_conditions:
        #product_conditions=[prod(1) for prod in product_condition.groups()]
        print(product_conditions)
        return product_conditions
    else:
        return []
        #print(len(product_condition.groups()))
        #print(product_condition.groups())
        #print("Condition:", product_condition.group(1))


#extract_prod_condition_pdf("asd")
# with pdfplumber.open(pdf_path) as pdf:
#     first_page = pdf.pages[0]
#     tables = first_page.extract_tables()
#     print(tables)