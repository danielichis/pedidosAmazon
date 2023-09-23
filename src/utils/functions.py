import re
from src.interfaces import mainView,homeLogin,pedidosOverview

    
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

def previusUrl(z):
    return f"https://www.amazon.com/-/es/gp/your-account/order-history/ref=ppx_yo_dt_b_pagination_{z-2}_{z-1}?ie=UTF8&orderFilter=year-2023&search=&startIndex={(z-2)*10}"
def get_pdf(page):
    page.pdf(path="pdf.pdf")

