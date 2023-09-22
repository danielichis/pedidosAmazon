import re

def get_courier(adressName):
    try:
        if len(re.findall(r"8414 Nw 66th St",adressName,flags=re.I))>0:
            courier="EF"
        elif len(re.findall(r"7806 NW 46TH ST",adressName,flags=re.I))>0:
            courier="Alexim"
        elif len(re.findall(r"2868 NW 72ND AVE",adressName,flags=re.I))>0:
            courier="JMC"
        elif len(re.findall(r"1350 NW 121ST AVE",adressName,flags=re.I))>0:
            courier="MSL"
        else:
            courier="otros"
    except:
        courier="Sin courier"
    return courier

def get_pdf(page):
    page.pdf(path="pdf.pdf")
