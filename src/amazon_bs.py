from datetime import datetime
from pedidosAmazon.src.utils.apiGsheet import updateGshhet
import csv
import os
from playwright.sync_api import sync_playwright,expect
from pedidosAmazon.src.utils.readconfig import settingsData as stt
from pedidosAmazon.src.utils.autoWaits import retry_on_exception
from tqdm import tqdm
from pedidosAmazon.src.interfaces import mainView,homeLogin,pedidosOverview,detallesPedidos,trakingView
from pedidosAmazon.src.utils.functions import previousUrl_bs, previusUrl
from pedidosAmazon.src.utils.amazonScraping import get_sku_info
from pedidosAmazon.src.utils.pdfScraping import extract_prod_condition_pdf
from pedidosAmazon.credentials import credentials
from PIL import Image
import time
import locale
import requests
from http.cookies import SimpleCookie

date_format={"esp":"%d de %B de %Y","eng":"%B %d, %Y"}

class AmazonBs:
    def __init__(self,dateConfigSheet=None) -> None:
        self.p= sync_playwright().start()
        self.browser = self.p.chromium.launch_persistent_context(user_data_dir=stt.user_data_dir,headless=stt.headless)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(10000)
        self.urlMain=stt.URLS_LINKS["URL-MAIN"]
        self.urlSignin=stt.URLS_LINKS["URL-SIGIN"]
        self.urlOrders=stt.URLS_LINKS["URL-ORDERS"]
        self.dateConfigSheet=dateConfigSheet
        self.orderCards_list=None
        print("---->INICIANDO<----")
        print(self.dateConfigSheet)
        self.dateConfig={"DESDE":stt.dateFrom,"HASTA":stt.dateTo}
        self.set_dateConfigSheet()
        self.ScrapedData=[]

    def set_dateConfigSheet(self):
        if self.dateConfigSheet==None:
            self.dateConfigSheet=self.dateConfig
    def go_to_login(self):
        self.page.goto(self.urlSignin)
        self.page.wait_for_url(self.urlSignin)
        print("---->LOGEADO CORRECTAMENTE<----")

    def go_to_orders(self):

        if self.acount=='seguimientomkp@unaluka.com':
            self.page.get_by_role("link", name="Hello, Gianfranco Account for").click()
            self.page.get_by_role("button", name="Your Orders Your Orders Track").click()
        else:
            self.page.locator(mainView.button_orders.selector).click()
        time.sleep(3)
        if len(self.page.query_selector_all("span[class='a-size-base transaction-approval-word-break']"))>0:
            print(f"La cuenta {self.acount} pide codigo de verificacion")
            #hacer click en el boton de enviar codigo
            exit()
        if len(self.page.query_selector_all("input[id='signInSubmit']"))>0:
            print(f"La cuenta {self.acount} pide ingresar contraseña nuevamente")
            time.sleep(2)
            self.page.get_by_label("Password").fill(credentials[self.acount])
            self.page.get_by_label("Sign in").click()
            #exit()
        self.page.wait_for_selector(pedidosOverview.orderCards_list_bs.selector)
    def get_pdf(self):
        #self.page.goto(self.UrlPdf,wait_until="load")
        ###Getting headers and cookies from request
        with self.page.expect_request(self.UrlPdf) as request_info:
            self.page.goto(self.UrlPdf,wait_until="load")

        request = request_info.value
        amazon_headers=request.headers
        amazon_cookies=request.all_headers()['cookie']
        #print(amazon_headers)
        #print(amazon_cookies)
        #Creating cookie object to create cookies dict
        cookie = SimpleCookie()
        cookie.load(amazon_cookies)
        cookies_dict ={ key:morsel.value for key, morsel in cookie.items()}


        ##Obtaining location which contain the pdf URL from the response
        with self.page.expect_response(self.UrlPdf) as response_info:
            self.page.goto(self.UrlPdf,wait_until="load")


        response = response_info.value
        location=response.headers['location']
        #print(request.headers)

        ##Obtaining pdf
        response_pdf = requests.get(
            self.UrlPdf,
            cookies=cookies_dict,
            headers=amazon_headers,
        )

        print(response_pdf.status_code)
        pdfPath=os.path.join("downloads",f"{self.orderIdOfCard}.pdf")
        with open(pdfPath, 'wb') as f:
            f.write(response_pdf.content)
        print(f"Se descargó resumen de pedido {self.orderIdOfCard}.")
        self.view="pdfView"
        ##Setting the conditions of the products in the dataproductsInfo
        productConditionList=extract_prod_condition_pdf(pdf_path=pdfPath)
        products_list=[]
        for shipping in self.dataShippings:
            products_list=products_list+shipping["dataProducts"]
        if len(productConditionList)==len(products_list):
            print("Cantidad de filas de pdf y productos coinciden")
            print("Extrayendo los estados de los productos...")
            for i,productCondition in enumerate(productConditionList):
                products_list[i]["conditionProduct"]=productCondition

    def get_trakingInfo(self):
        self.page.wait_for_selector("span[id='primaryStatus'],h1[class='pt-promise-main-slot']")
        self.shiptmentdate=self.page.query_selector("span[id='primaryStatus'],h1[class='pt-promise-main-slot']").inner_text()
        try:
            self.page.wait_for_selector("div[class='pt-delivery-card-trackingId'],h4[class*='trackingId-text']",timeout=1000)
            self.trakingId=self.page.query_selector("div[class='pt-delivery-card-trackingId'],h4[class*='trackingId-text']").inner_text().replace("Tracking ID:","")
            self.courier=self.page.query_selector("div[class='pt-delivery-card-wrapper'] h3").inner_text().replace("Shipped with","").replace("Delivery by","").strip()
        except Exception as e:
            print("error en trackingID"+str(e))
            self.trakingId="-"
            self.courier="-"


    def is_order_wanted(self,dateofCard):
        #conver string to date object
        #locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        dateofCard_date = datetime.strptime(dateofCard,date_format["eng"])
        dateFrom_date = datetime.strptime(self.dateConfigSheet["DESDE"], '%d/%m/%Y')
        dateTo_date = datetime.strptime(self.dateConfigSheet["HASTA"], '%d/%m/%Y')
        
        if dateofCard_date<dateFrom_date:
            r="stop"
        elif dateofCard_date>=dateFrom_date and dateofCard_date<=dateTo_date:
            r="scrap"
        else:
            r="skip"
        return r
    
    def get_bill_info(self):
        summaryBill=self.page.locator(detallesPedidos.summaryConcept_list.selector).all_inner_texts()
        obj_bill={}
        for row in summaryBill:
            if ":" not in row:
                print("No se encontró ':' en la fila de la cuenta(Billing),saltando fila")
                continue
            if row!="":
                key,value=row.split(":")
                obj_bill[key]=value
            else:
                print("Se encontró fila vacía en la cuenta(Billing),saltando fila")
        keysDiscount=list(obj_bill.keys())

        list_keys_discount=["Buy any 4, Save 5%","Deal of the Day","Your Coupon Savings","Promotion Applied","Envío gratis","Free Shipping","Promotional credit","Saldo Amazon","Crédito de cortesía"]
        obj_bill["Cupón/Puntos"]=0
        for key in list_keys_discount:
            if key in keysDiscount:
                discount=obj_bill[key].replace("$","").replace(",","")
                obj_bill["Cupón/Puntos"]=round(obj_bill["Cupón/Puntos"]+float(discount),3)
        finallyBill={
            "Item(s) Subtotal":float(obj_bill["Item(s) Subtotal"].replace("$","").replace("\n","").replace(",","")),
            "Shipping & Handling":float(obj_bill["Shipping & Handling"].replace("$","").replace("\n","").replace(",","")),
            "Discounts":float(obj_bill["Cupón/Puntos"]),
            "Total before tax":float(obj_bill["Total before tax"].replace("$","").replace("\n","").replace(",","")),
            "Estimated tax to be collected":float(obj_bill["Estimated tax to be collected"].replace("$","").replace("\n","").replace(",","")),
            "Grand Total":float(obj_bill["Grand Total"].replace("$","").replace("\n","").replace(",","")),
        }
        self.info_bill=finallyBill

    def search_product_brand(self):
        sku_info=get_sku_info(self.linkProduct)
        for category,info in sku_info.items():
            print("Buscando en "+category+"...")
            if "Marca" in info.keys():
                print("Se encontró Marca")
                return info["Marca"].upper()
            elif "Fabricante" in info.keys():
                print("Se encontró Fabricante")
                return info["Fabricante"].upper()
        
        print("No se encontró Marca o Fabricante")
        return "---No se encontró Marca,buscar manualmente---"

        
    def get_products_list(self):
        #another idea
        #self.page.locator("div[class='a-fixed-left-grid-inner']").inner_text()
        self.products_list=self.shipping.locator(detallesPedidos.products_list.selector).all()
        #self.products_list=self.shippings
        #studycase 112-7005829-6740208
        #self.products_list=[product.inner_text().split("\n") for product in self.shippings]
        self.dataProducts=[]
        for product in self.products_list:
            product_text=product.inner_text().split("\n")
            if len(product_text)==6:
                offset=1
                self.quantityProduct=product_text[0]
                print("Cantidad del producto mayor a 1")
            else:
                offset=0
                self.quantityProduct=1


            # if len(product_text)==5:
            #     offset=0
            #     self.quantityProduct=1

            self.priceProduct=product.locator(detallesPedidos.priceOfProduct2.selector).first.inner_text().replace("US$","").replace("$","")
            #self.priceProduct=float(self.priceProduct.replace("$","").replace("\n","").replace(",",""))
            #self.priceProduct=product_text[2+offset].replace("US$","").replace("$","")
            try:
                self.conditionProduct="-"
                #self.conditionProduct=product.locator(detallesPedidos.conditionOfProduct.selector).inner_text()
            except Exception as e:
                print(str(e))
                self.conditionProduct="-"
            self.sellerProduct=product.locator(detallesPedidos.sellerOfProduct.selector).inner_text().replace("Sold by:","").strip()
            #self.sellerProduct=product_text[1+offset].replace("Vendido por:","").strip()
            try:
                #timeout 3s
                self.page.wait_for_selector(detallesPedidos.quantityOfProduct.selector,timeout=1000)
                self.quantityProduct=product.locator(detallesPedidos.quantityOfProduct.selector).inner_text()
            except Exception as e:
                print("error en cantidad:"+str(e))
                self.quantityProduct=1
            self.nameProduct=product.locator("div[class*='a-fixed-left-grid'] div[class*='a-row']:first-child>a").inner_text()
            self.linkProduct=self.urlMain+product.locator("div[class*='a-fixed-left-grid'] div[class*='a-row']:first-child>a").get_attribute("href")

            #self.nameProduct=product_text[0+offset]

            #brand
            self.brandProduct=self.search_product_brand()

            products_dict={"nameProduct":self.nameProduct,
                           "priceProduct":self.priceProduct,
                           "conditionProduct":self.conditionProduct,
                           "sellerProduct":self.sellerProduct,
                           "quantityProduct":self.quantityProduct,
                           "linkProduct":self.linkProduct,
                           "brandProduct":self.brandProduct}
            self.dataProducts.append(products_dict)

    def createData(self):
        for ship in self.dataShippings:
            self.dataProducts=ship["dataProducts"]
            for product in self.dataProducts:
                var=[]
                for q in range(int(product["quantityProduct"])):
                    data={
                        "date":self.order_date,
                        "orderId":self.orderIdOfCard,
                        "nameProduct":product["nameProduct"],
                        "linkProduct":product["linkProduct"],
                        "brand":product["brandProduct"],
                        "Condition":product["conditionProduct"],
                        "Seller":product["sellerProduct"],
                        "Quantity":1,
                        "Price":product["priceProduct"],
                        "Payment Instrument Card":self.nameCards,
                        "Payment Instrument Numbers":self.digitCards,
                        "Ordering Customer Email":self.acount,
                        "shiptmentdate":ship["shiptmentdate"],
                        **self.adressInfo,
                        "courier":ship["courier"],
                        "trakingId":ship["trakingId"],
                        **self.info_bill
                    }
                    self.ScrapedData.append(data)
                    var.append(data)
                updateGshhet(var)
        
    def get_shipping_info(self):
        try:
            self.page.wait_for_selector("div[class='a-fixed-left-grid-inner']")
            shippings1=self.page.locator("div[class*='a-box shipment'] div[class='a-box-inner']").all()
            shippings2=self.page.locator("div[data-component='shipments'] div[class='a-box-inner']").all()
            if len(shippings1)>0:
                self.shippings=shippings1
            elif len(shippings2)>0:
                self.shippings=shippings2

            #self.shippings=self.page.locator("div[class='a-fixed-left-grid-inner']").all()
            # self.page.wait_for_selector("div[class='a-box shipment']")
            # self.shippings=self.page.locator("div[class*='a-box shipment']").all()
        except:
            self.page.wait_for_selector("div[class*='a-box-group']")
            self.shippings=self.page.locator("div[class*='a-box-group']").all()

        self.dataShippings=[]

        for self.shipping in self.shippings:
            self.get_products_list()
            try:
                #self.urlTraking=self.shipping.locator("span[class*='track-package-button'] a").get_attribute("href")
                self.urlTraking=self.shipping.get_by_text("Track package").get_attribute("href")
                self.urlTraking=self.urlMain+self.urlTraking
            except:
                self.urlTraking="sin url"
            self.dataShippings.append({"urlTraking":self.urlTraking,"dataProducts":self.dataProducts,"shiptmentdate":"sin rastreo","trakingId":"sin rastreo","courier":"sin rastreo"})
        
        for dataShipping in self.dataShippings:
            if dataShipping["urlTraking"]!="sin url":
                self.page.goto(dataShipping["urlTraking"],wait_until="load")
                self.get_trakingInfo()
                dataShipping["shiptmentdate"]=self.shiptmentdate
                dataShipping["trakingId"]=self.trakingId
                dataShipping["courier"]=self.courier
            
    def get_adress_info(self):

        directions_list_1=self.page.locator(detallesPedidos.directions_list.selector).all_inner_texts()
        directions_list_2=self.page.locator(detallesPedidos.directions_list2.selector).all_inner_texts()
        if len(directions_list_1)>0:
            self.directions_list=directions_list_1
        elif len(directions_list_2)>0:
            self.directions_list=directions_list_2
        else:
            print("No se encontraron direcciones")
            self.directions_list=[]

        if len(self.directions_list)<4:
            directions_concatenated="\n".join(self.directions_list)
            self.directions_list=directions_concatenated.split("\n")

        try:
            address_name=self.directions_list[0]
        except:
            address_name="-"
        try:
            address_street1=self.directions_list[1]
        except:
            address_street1="-"
        try:
            address_city=self.directions_list[2]
        except:
            address_city="-"
        try:
            address_state=self.directions_list[3].split(",")[0]
        except:
            address_state="-"
        try:
            address_zip=self.directions_list[3].split(",")[1]
        except:
            address_zip="-"

        #Splitting address zip

        address_zip_list=address_zip.strip().split(" ")
        if len(address_zip_list)==2:
            address_zip_1,address_zip_2=address_zip_list[0],address_zip_list[1]
        else:
            address_zip_1,address_zip_2="-","-"
        
        self.adressInfo={"address_name":address_name,"address_street1":address_street1,"address_city":address_city,"address_state":address_state,"address_zip":address_zip,"address_zip_1":address_zip_1,"address_zip_2":address_zip_2}


    def get_detailsOrderInfo(self):
        self.view="detallesPedidos"
        self.page.wait_for_selector(detallesPedidos.products_list.selector)
        try:
            order_date=self.page.query_selector(detallesPedidos.dateOfDetailsProduct1.selector).inner_text().replace("Ordered on","").strip()
        # except:
        #     order_date=self.page.query_selector(detallesPedidos.dateOfDetailsProduct2.selector).inner_text().split("N.º")[0].replace("Order","").strip()
        except:
            order_date=self.page.query_selector(detallesPedidos.dateOfDetailsProduct3.selector).inner_text().replace("Order Date:","").strip()
        self.order_date=datetime.strptime(order_date,date_format["eng"]).strftime("%d/%m/%Y")
        self.get_adress_info()
        try:
            #self.digitCards=self.page.locator("li>span:has(img)").inner_text()
            #Get last 4 character because they contain the digits numbers
            cardInfo=self.page.locator("li>span:has(img)").first.inner_text().split("ending in")
            self.nameCards=cardInfo[0]
            self.digitCards=int(cardInfo[1])
            #self.digitCards=self.page.locator("li>span:has(img)").first.inner_text()[-4:]
        except:
            self.digitCards="No digits"
        self.get_bill_info()
        #self.UrlPdf=self.page.locator("//span[@class='a-button-inner']/a[contains(text(), 'Ver o Imprimir Recibo')]").get_attribute("href")    
        #self.UrlPdf=self.page.locator("//span[@class='a-list-item']/a[contains(text(),'Printable Order Summary')]").get_attribute("href") 
        self.get_shipping_info()
        #self.UrlPdf=self.urlMain+self.UrlPdf
        #self.get_pdf()
        self.createData()
    
    def save_to_csv(self):
        with open('pedidos.csv', mode='w',newline='',encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.ScrapedData[0].keys())
            writer.writeheader()
            for data in self.ScrapedData:
                writer.writerow(data)

    def esperar_lista_paginas(self):
        max_retries=5
        retrie=0
        delay=2
        self.orderCards_list=self.page.locator(pedidosOverview.orderCards_list_bs.selector).all()
        while retrie<max_retries:
            self.orderCards_list=self.page.locator(pedidosOverview.orderCards_list.selector).all()
            if len(self.orderCards_list)==10:
                break
            time.sleep(delay)
            retrie+=1
            print("esperando lista de pedidos")
        
    def scrap_page(self):
        print("------------leyendo pagina")
        self.esperar_lista_paginas()
        orderCards_list=self.page.locator(pedidosOverview.orderCards_list_bs.selector).all()
        #ordersLinks=[orderCard.locator("//a[contains(text(),'Ver detalles del pedido')]").get_attribute("href") for orderCard in orderCards_list]
        ordersLinks=[]
        for orderCard in orderCards_list:
            try:
                orderLink=orderCard.locator("//a[contains(text(),'View order details')]").get_attribute("href")
                ordersLinks.append(orderLink)
            except:
                print("Orden no tiene link de rastreo,pasando a la siguiente")
                orderLink=None
                ordersLinks.append(orderLink)
        ordersIds=[orderCard.locator(pedidosOverview.orderIdOfCard_bs.selector).inner_text().replace("Order # ","").strip() for orderCard in orderCards_list]
        ordersDates=[orderCard.locator(pedidosOverview.dateofCard_bs.selector).inner_text() for orderCard in orderCards_list]
        print(f"numero de pedidos:{len(orderCards_list)}")
        for i,link in enumerate(ordersLinks):
            if link:
                dateofCard=ordersDates[i]
                self.orderIdOfCard=ordersIds[i]
                r= self.is_order_wanted(dateofCard)
                self.status=r
                print("\n")
                print(f"pedido {self.orderIdOfCard}-{dateofCard}...")
                if r=="stop":
                    print("terminando de leer pedidos")
                    break
                elif r=="skip":
                    print(f"Saltando pedido ...")
                    continue
                print(f"leyendo pedido ...")
                link=self.urlMain+link            
                #time.sleep(1)
                self.page.goto(link,wait_until="load")
                try:
                    self.get_detailsOrderInfo()
                except Exception as e:
                    print("Error al capturar info de producto "+str(e))
                    print("Pasando a siguiente producto...")
                    error_data={
                            "date":ordersDates[i],
                            "orderId":self.orderIdOfCard,
                            "nameProduct":"ERROR AL OBTENER INFORMACIÓN DE PRODUCTO"
                        }
                    updateGshhet([error_data])
                    self.view="detallesPedidos"
                    continue

                self.view="detallesPedidos"
            else:
                self.orderIdOfCard=ordersIds[i]
                print("Orden no tiene link de acceso")
                print("Pasando a siguiente producto...")
                error_data={
                            "date":ordersDates[i],
                            "orderId":self.orderIdOfCard,
                            "nameProduct":"ORDEN NO TIENE LINK DE ACCESO"
                        }
                updateGshhet([error_data])
                self.view="detallesPedidos"
            
    def switch_to_tab(self,tab):
        if tab>1:
            self.page.locator(pedidosOverview.button_next.selector).click()
            self.page.wait_for_selector(pedidosOverview.orderCards_list_bs.selector)
            print(f"-----leyendo pagina {tab}")
        else:
            print(f"-----leyendo pagina {tab}")
    def scrap_account(self):
        self.go_to_orders()
        tab=1
        try:
            self.page.wait_for_selector(pedidosOverview.button_next.selector)
        except:
            pass
        self.view="pedidosOverview"
        self.status="scrap"
        while True:
            # if len(self.page.query_selector_all(pedidosOverview.button_next.selector))==0:
            #     print(f"SIN BOTON NEXT,terminando de leer pedidos en cuenta {self.acount}")
            #     break
            self.switch_to_tab(tab)
            self.scrap_page()
            if self.status=="stop":
                print(f"terminando de leer pedidos en cuenta {self.acount}")
                break
            tab+=1
            if self.view!="pedidosOverview":
                Url=previousUrl_bs(tab)
                self.page.goto(Url,wait_until="load")
                self.page.wait_for_load_state("load")
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_load_state("domcontentloaded")
                self.view="pedidosOverview"
    def scrap_info(self):
        self.page.wait_for_selector(homeLogin.buttons_cuentas.selector)
        self.view="homeLogin"
        account_list=self.page.query_selector_all(homeLogin.buttons_cuentas.selector)
        acounts_strings=[account.inner_text() for account in account_list]
        for account in acounts_strings:
            selectorAcount=f"//div[contains(text(),'{account}')]"
            self.acount=account
            if account!='seguimientomkp@unaluka.com':
                continue
            self.page.locator(selectorAcount).click()
            #wait load page
            self.page.wait_for_load_state("load")
            time.sleep(3)
            #goto spanish language account
            #self.page.goto("https://www.amazon.com/?ref_=nav_youraccount_switchacct&language=es_US")
            #self.page.wait_for_load_state("networkidle")
            self.page.wait_for_load_state("load")
            time.sleep(3)
            if len(self.page.query_selector_all("span[class='a-size-base transaction-approval-word-break']"))>0:
                print(f"La cuenta {self.acount} pide codigo de verificacion")
                #hacer click en el boton de enviar codigo
                exit()
            if len(self.page.query_selector_all("input[id='signInSubmit']"))>0:
                print(f"La cuenta {self.acount} pide ingresar contraseña nuevamente")
                time.sleep(2)
                self.page.get_by_label("Password").fill(credentials[account])
                self.page.get_by_label("Sign in").click()
                #exit()

            #self.page.wait_for_selector(mainView.button_orders.selector)
            print(f"leyendo en cuenta:{self.acount}")
            self.scrap_account()
            self.go_to_login()

    def end(self):
        self.page.close()
        self.browser.close()
        self.p.stop()
def get_pedidos_amazon_bs(dates_dict=None):
    try:
        amazonPage=AmazonBs(dateConfigSheet=dates_dict)
        amazonPage.go_to_login()
        amazonPage.scrap_info()
        amazonPage.end()
        return "terminado"
    except Exception as e:
        print("Error al extraer órdenes business")
        print(str(e))
        amazonPage.end()
if __name__ == "__main__":
    get_pedidos_amazon_bs()

    


