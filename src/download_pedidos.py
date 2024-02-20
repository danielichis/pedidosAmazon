from datetime import datetime
from pedidosAmazon.src.utils.apiGsheet import updateGshhet
import csv
import os
from playwright.sync_api import sync_playwright,expect
from pedidosAmazon.src.utils.readconfig import settingsData as stt
from pedidosAmazon.src.utils.autoWaits import retry_on_exception
from tqdm import tqdm
from pedidosAmazon.src.interfaces import mainView,homeLogin,pedidosOverview,detallesPedidos,trakingView
from pedidosAmazon.src.utils.functions import previusUrl
from PIL import Image
import time
import locale

class Amazon:
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
        self.page.locator(mainView.button_orders.selector).click()
        time.sleep(3)
        if len(self.page.query_selector_all("span[class='a-size-base transaction-approval-word-break']"))>0:
            print(f"La cuenta {self.acount} pide codigo de verificacion")
            #hacer click en el boton de enviar codigo
            exit()
        if len(self.page.query_selector_all("input[id='signInSubmit']"))>0:
            print(f"La cuenta {self.acount} pide ingresar contraseña nuevamente")
            exit()
        self.page.wait_for_selector(pedidosOverview.orderCards_list.selector)
    def get_pdf(self):
        self.page.goto(self.UrlPdf,wait_until="load")
        self.page.wait_for_selector("//a[text()='Resumen del pedido']")
        pdfPath=os.path.join("downloads",f"{self.orderIdOfCard}.pdf")
        self.page.pdf(path=pdfPath)
        self.view="pdfView"
        #self.page.locator("//a[text()='Resumen del pedido']").click()
        pass
    def get_trakingInfo(self):
        self.page.wait_for_selector("span[id='primaryStatus'],h1[class='pt-promise-main-slot']")
        self.shiptmentdate=self.page.query_selector("span[id='primaryStatus'],h1[class='pt-promise-main-slot']").inner_text()
        try:
            self.page.wait_for_selector("div[class='pt-delivery-card-trackingId'],h4[class*='trackingId-text']",timeout=1000)
            self.trakingId=self.page.query_selector("div[class='pt-delivery-card-trackingId'],h4[class*='trackingId-text']").inner_text()
        except Exception as e:
            print("error en trakingID"+str(e))
            self.trakingId="-"


    def is_order_wanted(self,dateofCard):
        #conver string to date object
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        dateofCard_date = datetime.strptime(dateofCard, '%d de %B de %Y')
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
            key,value=row.split(":")
            obj_bill[key]=value
        keysDiscount=list(obj_bill.keys())

        list_keys_discount=["Buy any 4, Save 5%","Deal of the Day","Your Coupon Savings","Promotion Applied","Envío gratis","Free Shipping","Promotional credit","Saldo Amazon"]
        obj_bill["Cupón/Puntos"]=0
        for key in list_keys_discount:
            if key in keysDiscount:
                discount=obj_bill[key].replace("$","").replace(",","")
                obj_bill["Cupón/Puntos"]=round(obj_bill["Cupón/Puntos"]+float(discount),3)
        finallyBill={
            "Productos":float(obj_bill["Productos"].replace("$","").replace("\n","").replace(",","")),
            "Envío":float(obj_bill["Envío"].replace("$","").replace("\n","").replace(",","")),
            "Descuentos":float(obj_bill["Cupón/Puntos"]),
            "Total antes de impuestos:":float(obj_bill["Total antes de impuestos"].replace("$","").replace("\n","").replace(",","")),
            "Impuestos":float(obj_bill["Impuestos"].replace("$","").replace("\n","").replace(",","")),
            "Total (I.V.A. Incluido)":float(obj_bill["Total (I.V.A. Incluido)"].replace("$","").replace("\n","").replace(",","")),
        }
        self.info_bill=finallyBill
        
    def get_products_list(self):
        self.products_list=self.shipping.locator(detallesPedidos.products_list.selector).all()
        self.dataProducts=[]
        for product in self.products_list:
            self.priceProduct=product.locator(detallesPedidos.priceOfProduct.selector).inner_text()
            self.priceProduct=float(self.priceProduct.replace("$","").replace("\n","").replace(",",""))
            self.conditionProduct=product.locator(detallesPedidos.conditionOfProduct.selector).inner_text()
            self.sellerProduct=product.locator(detallesPedidos.sellerOfProduct.selector).inner_text()
            try:
                #timeout 3s
                self.page.wait_for_selector(detallesPedidos.quantityOfProduct.selector,timeout=1000)
                self.quantityProduct=product.locator(detallesPedidos.quantityOfProduct.selector).inner_text()
            except Exception as e:
                print("error en cantidad:"+str(e))
                self.quantityProduct=1
            self.nameProduct=product.locator("div[class*='a-fixed-left-grid'] div[class*='a-row']:first-child>a").inner_text()
            products_dict={"nameProduct":self.nameProduct,"priceProduct":self.priceProduct,"conditionProduct":self.conditionProduct,"sellerProduct":self.sellerProduct,"quantityProduct":self.quantityProduct}
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
                        "Condition":product["conditionProduct"],
                        "Seller":product["sellerProduct"],
                        "Quantity":1,
                        "Price":product["priceProduct"],
                        "Payment Instrument Type":self.digitCards,
                        "Ordering Customer Email":self.acount,
                        "shiptmentdate":ship["shiptmentdate"],
                        **self.adressInfo,
                        "trakingId":ship["trakingId"],
                        **self.info_bill
                    }
                    self.ScrapedData.append(data)
                    var.append(data)
                updateGshhet(var)
        
    def get_shipping_info(self):
        self.page.wait_for_selector("div[class*='a-box shipment']")
        self.shippings=self.page.locator("div[class*='a-box shipment']").all()
        self.dataShippings=[]
        for self.shipping in self.shippings:
            self.get_products_list()
            try:
                self.urlTraking=self.shipping.locator("span[class*='track-package-button'] a").get_attribute("href")
                self.urlTraking=self.urlMain+self.urlTraking
            except:
                self.urlTraking="sin url"
            self.dataShippings.append({"urlTraking":self.urlTraking,"dataProducts":self.dataProducts,"shiptmentdate":"sin rastreo","trakingId":"sin rastreo"})
        
        for dataShipping in self.dataShippings:
            if dataShipping["urlTraking"]!="sin url":
                self.page.goto(dataShipping["urlTraking"],wait_until="load")
                self.get_trakingInfo()
                dataShipping["shiptmentdate"]=self.shiptmentdate
                dataShipping["trakingId"]=self.trakingId
            
    def get_adress_info(self):
        self.directions_list=self.page.locator(detallesPedidos.directions_list.selector).all_inner_texts()
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
        self.adressInfo={"address_name":address_name,"address_street1":address_street1,"address_city":address_city,"address_state":address_state,"address_zip":address_zip}

    def get_detailsOrderInfo(self):
        self.view="detallesPedidos"
        self.page.wait_for_selector(detallesPedidos.products_list.selector)
        self.order_date=self.page.query_selector(detallesPedidos.dateOfDetailsProduct.selector).inner_text()
        self.get_adress_info()
        try:
            self.digitCards=self.page.locator("li>span:has(img)").inner_text()
        except:
            self.digitCards="Sin digitos"
        self.get_bill_info()
        self.UrlPdf=self.page.locator("//span[@class='a-button-inner']/a[contains(text(), 'Ver o Imprimir Recibo')]").get_attribute("href")    
        self.get_shipping_info()
        self.UrlPdf=self.urlMain+self.UrlPdf
        self.get_pdf()
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
        delay=1
        self.orderCards_list=self.page.locator(pedidosOverview.orderCards_list.selector).all()
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
        orderCards_list=self.page.locator(pedidosOverview.orderCards_list.selector).all()
        ordersLinks=[orderCard.locator("//a[contains(text(),'Ver detalles del pedido')]").get_attribute("href") for orderCard in orderCards_list]
        ordersIds=[orderCard.locator(pedidosOverview.orderIdOfCard.selector).inner_text() for orderCard in orderCards_list]
        ordersDates=[orderCard.locator(pedidosOverview.dateofCard.selector).inner_text() for orderCard in orderCards_list]
        print(f"numero de pedidos:{len(orderCards_list)}")
        for i,link in enumerate(ordersLinks):
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
            self.get_detailsOrderInfo()
            self.view="detallesPedidos"
            
    def switch_to_tab(self,tab):
        if tab>1:
            self.page.locator(pedidosOverview.button_next.selector).click()
            self.page.wait_for_selector(pedidosOverview.orderCards_list.selector)
            print(f"-----leyendo pagina {tab}")
        else:
            print(f"-----leyendo pagina {tab}")
    def scrap_account(self):
        self.go_to_orders()
        tab=1
        self.page.wait_for_selector(pedidosOverview.button_next.selector)
        self.view="pedidosOverview"
        self.status="scrap"
        while True:
            if len(self.page.query_selector_all(pedidosOverview.button_next.selector))==0:
                print(f"SIN BOTON NEXT,terminando de leer pedidos en cuenta {self.acount}")
                break
            self.switch_to_tab(tab)
            self.scrap_page()
            if self.status=="stop":
                print(f"terminando de leer pedidos en cuenta {self.acount}")
                break
            tab+=1
            if self.view!="pedidosOverview":
                Url=previusUrl(tab)
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
            self.page.locator(selectorAcount).click()
            #wait load page
            self.page.wait_for_load_state("load")
            time.sleep(3)
            if len(self.page.query_selector_all("span[class='a-size-base transaction-approval-word-break']"))>0:
                print(f"La cuenta {self.acount} pide codigo de verificacion")
                #hacer click en el boton de enviar codigo
                exit()
            if len(self.page.query_selector_all("input[id='signInSubmit']"))>0:
                print(f"La cuenta {self.acount} pide ingresar contraseña nuevamente")
                exit()
            self.page.wait_for_selector(mainView.button_orders.selector)
            print(f"leyendo en cuenta:{self.acount}")
            self.scrap_account()
            self.go_to_login()

    def end(self):
        self.page.close()
        self.browser.close()
        self.p.stop()
def get_pedidos_amazon():
    amazonPage=Amazon()
    amazonPage.go_to_login()
    amazonPage.scrap_info()
    amazonPage.end()
    return "terminado"
if __name__ == "__main__":
    get_pedidos_amazon()

    


