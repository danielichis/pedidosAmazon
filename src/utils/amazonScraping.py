import requests
from selectolax.parser import HTMLParser
import requests
import re
import json

def get_amazon_html(purchase_url:str):
    cookies = {
        'session-id': '138-3363892-2334805',
        'session-id-time': '2082787201l',
        'i18n-prefs': 'USD',
        'sp-cdn': '"L5Z9:PE"',
        'ubid-main': '135-7500017-8187530',
        'lc-main': 'es_US',
        'csm-hit': 'tb:42029YQ73ZR4Z693WDX2+s-1K8W6D050VS3RN9YGNDS|1726945361664&t:1726945361664&adb:adblk_yes',
        'session-token': 'BCeB0cRWvX5aauM9Jjl7P80R/4cQw/ADCCGTPXq9VhQwpusheeH94NgYUJXID51fiCamFYVSJdfz2n2ovb51gBbCsWJ3ZG8kW/C5QhvmkWCVHJ1EEqjYMyGfZGw33Wf0Md5vbMH3v+X48laymcN6X9AHA8hT3zePSSCE+Vq7Od7lmBF8yEOw7e5Hf9TtrsmuOQsWmr6gBqtTp3qNCFmt7t6y8lyIXvL5CHpSpIoPwimEdvo7sRgHK5jiWpZLXxv/GLKwQaoTpie6ggQU3jR35azljWZ0mJgkwr7hSa/flyS5Dkaa6vVONezZ2yU4o0KBVE4Ffn96hYNtOFaD6fkrIxg6HSNxgMDd',
    }
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'es-419,es;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        # 'cookie': 'session-id=138-3363892-2334805; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:PE"; ubid-main=135-7500017-8187530; lc-main=es_US; csm-hit=tb:42029YQ73ZR4Z693WDX2+s-1K8W6D050VS3RN9YGNDS|1726945361664&t:1726945361664&adb:adblk_yes; session-token=BCeB0cRWvX5aauM9Jjl7P80R/4cQw/ADCCGTPXq9VhQwpusheeH94NgYUJXID51fiCamFYVSJdfz2n2ovb51gBbCsWJ3ZG8kW/C5QhvmkWCVHJ1EEqjYMyGfZGw33Wf0Md5vbMH3v+X48laymcN6X9AHA8hT3zePSSCE+Vq7Od7lmBF8yEOw7e5Hf9TtrsmuOQsWmr6gBqtTp3qNCFmt7t6y8lyIXvL5CHpSpIoPwimEdvo7sRgHK5jiWpZLXxv/GLKwQaoTpie6ggQU3jR35azljWZ0mJgkwr7hSa/flyS5Dkaa6vVONezZ2yU4o0KBVE4Ffn96hYNtOFaD6fkrIxg6HSNxgMDd',
        'device-memory': '8',
        'downlink': '10',
        'dpr': '1',
        'ect': '4g',
        'priority': 'u=0, i',
        'rtt': '100',
        'sec-ch-device-memory': '8',
        'sec-ch-dpr': '1',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"10.0.0"',
        'sec-ch-viewport-width': '1297',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'viewport-width': '1297',
    }
    response = requests.get(purchase_url, cookies=cookies, headers=headers)
    print(response.status_code)
    if response.status_code==200:
        amazon_html=HTMLParser(response.text)
        with open("purchase_html.html","w",encoding="utf-8") as f:
            f.write(response.text)
        return amazon_html
    else:
        raise Exception("Error al obtener información de producto")

def get_descriptions(sku_html):
    
    descriptions=sku_html.css("div#productDescription span")
    #descriptions=sku_html.css("div#productOverview_feature_div span")
    dicDescs={}
    if descriptions:
        list_Descs=[description.text() for description in descriptions]
        # if len(list_Descs)==1:
        #     list_Descs=[x+"." for x in descriptions.inner_text().split(".") if x!=""]
        #     for i,desc in enumerate(list_Descs):
        #         dicDescs[str("-")]=desc

        for i in range(len(list_Descs)//2):
            #print("texto en linea: "+desc)
            try:
                d1=list_Descs[2*i]
                d2=list_Descs[2*i+1]
                dicDescs[d1]=d2
            except: 
                pass
    return dicDescs

def get_overview(sku_html):
    overViewSelectors=["div[id='productOverview_feature_div'] div[class='a-section a-spacing-small a-spacing-top-small'] tr","div[id='productOverview_feature_div'] div[class='a-section a-spacing-small a-spacing-top-small'] tr"]
    try:
        sku_html.css("div[id='productOverview_feature_div'] div[class='a-section a-spacing-small a-spacing-top-small'] tr",timeout=3000)
    except:
        pass
    overView=sku_html.css("div[id='productOverview_feature_div'] div[class='a-section a-spacing-small a-spacing-top-small'] tr")


    overVies={}
    for view in overView:
        try:
            overVies[view.css_first("td:nth-child(1) span").text()]=view.css_first("td:nth-child(2) span").text().replace("\u200e","")
        except:
            pass

    if len(overView)==0:
        overView=sku_html.css("div[id='feature-bullets'] li")
        for i,view in enumerate(overView):
            try:
                overVies[view.css_first("span").text().replace("\u200e","").split(":")[0]]=':'.join(view.css_first("span").text().replace("\u200e","").split(":")[1:])
            except:
                pass
    if len(overView)==0:
        #overView=sku_html.css("div:has(>h3[class='product-facts-title'])>div>div")

        parent_divs = [node for node in sku_html.css("div") if node.css_first("h3.product-facts-title")]

        # Step 2: From those parents, find the inner divs
        overView = []
        
        for parent in parent_divs:
            try:
                inner_divs = parent.css_first("div > div").text()
                overView.extend(inner_divs)
            except:
                print("Couldn't capture overview")

        #for view in overView:
        #    try:
        #        overVies[view.css_first("div:nth-child(1)").text().replace("\u200e","")]=view.css_first("div:nth-child(2)").text().replace("\u200e","")
        #    except:
        #        pass
    return overVies

def get_product_subtitle(sku_html):
    try:
        subtitle=sku_html.css_first("a#bylineInfo").text()
        if "Visita la tienda de" in subtitle:
            subtitle=subtitle.replace("Visita la tienda de","").strip()
        elif "Marca" in subtitle:
            subtitle=subtitle.replace("Marca:","").strip()
        return {"Marca":subtitle}
    except:
        return {}
    

def get_product_information(sku_html):
    productInformation=sku_html.css("table[id*='productDetails_detailBullets'] tr")
    productInformationDict={}
    for info in productInformation:
        productInformationDict[info.css_first("th").text()]=info.css_first("td").text().replace("\u200e","")
    return productInformationDict

def get_sku_info(purchase_url:str):
    print("Capturando información del producto...")
    #skus_info=[]
    sku_html=get_amazon_html(purchase_url)
    descriptions=get_descriptions(sku_html=sku_html)
    #print(descriptions)
    overview=get_overview(sku_html=sku_html)
    #print(overview)
    product_information=get_product_information(sku_html=sku_html)
    #print(product_information)
    subtitle=get_product_subtitle(sku_html=sku_html)
    #print(subtitle)

    sku_info={
        "descriptions":descriptions,
        "overview":overview,
        "product information":product_information,
        "subtitle":subtitle
    }

    return sku_info
    #print(sku_info)
    #skus_info.append(sku_info)

def search_sku_brand(sku_info:dict):
    
    for category,info in sku_info.items():
        print("Buscando en "+category+"...")
        if "Marca" in info.keys():
            print("Se encontró Marca")
            return info["Marca"]
        
    return "No se encontró Marca"
        
        

if __name__ == "__main__":
    purchase_url=["https://www.amazon.com/-/es/dp/B09VSD4YVD?ref_=ppx_hzod_title_dt_b_fed_asin_title_1_0&th=1",
                  "https://www.amazon.com/-/es/dp/B07FHM225F?ref_=ppx_hzod_title_dt_b_fed_asin_title_0_0",
                  "https://www.amazon.com/-/es/gp/product/B000GB0G2A/ref=ppx_od_dt_b_asin_title_s00?ie=UTF8&psc=1",
                    "https://www.amazon.com/-/es/dp/B0012SNLJG?ref_=ppx_hzod_title_dt_b_fed_asin_title_0_0",
                    "https://www.amazon.com/dp/B0C58H2CSP",
                    "https://www.amazon.com/-/es/gp/product/B00L8TBTXE/ref=ppx_od_dt_b_asin_title_s00?ie=UTF8&psc=1"]
    
    # skus_info=[]
    # sku_html=get_amazon_html(purchase_url[-1])
    # descriptions=get_descriptions(sku_html=sku_html)
    # print(descriptions)
    # overview=get_overview(sku_html=sku_html)
    # print(overview)
    # product_information=get_product_information(sku_html=sku_html)
    # print(product_information)

    # sku_info={
    #     "descriptions":descriptions,
    #     "overview":overview,
    #     "product information":product_information
    # }
    # print(sku_info)
    # skus_info.append(sku_info)

    sku_info=get_sku_info(purchase_url[-1])
    brand=search_sku_brand(sku_info)
    print(brand)
    
