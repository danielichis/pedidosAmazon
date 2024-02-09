from datetime import datetime
from src.utils.apiGsheet import updateGshhet
import csv
import os
from playwright.sync_api import sync_playwright
from utils.readconfig import settingsData as stt
from tqdm import tqdm
from src.interfaces import mainView,homeLogin,pedidosOverview,detallesPedidos,trakingView
from src.utils.functions import previusUrl
from PIL import Image
import time
import locale

class Amazon:
    def __init__(self) -> None:
        self.p= sync_playwright().start()
        self.browser = self.p.chromium.launch_persistent_context(user_data_dir=stt.user_data_dir,headless=stt.headless)
        self.page = self.browser.new_page()
        self.urlMain=stt.URLS_LINKS["URL-MAIN"]
        self.urlSignin=stt.URLS_LINKS["URL-SIGIN"]
        self.urlOrders=stt.URLS_LINKS["URL-ORDERS"]
        self.dateConfig={"DESDE":stt.dateFrom,"HASTA":stt.dateTo}
        self.ScrapedData=[]
    def go_to_login(self):
        self.page.goto(self.urlSignin)
        self.page.wait_for_url(self.urlSignin)

    def go_to_orders(self):
        self.page.locator(mainView.button_orders.selector).click()
        self.page.wait_for_selector(pedidosOverview.orderCards_list.selector)
    def get_pdf(self):
        self.page.wait_for_selector("//a[text()='Resumen del pedido']")
        pdfPath=os.path.join("downloads",f"{self.orderIdOfCard}.pdf")
        self.page.pdf(path=pdfPath)
        #self.page.locator("//a[text()='Resumen del pedido']").click()
        pass
    def get_trakingInfo(self):
        self.page.wait_for_selector("span[id='primaryStatus'],h1[class='pt-promise-main-slot']")
        self.shiptmentdate=self.page.query_selector("span[id='primaryStatus'],h1[class='pt-promise-main-slot']").inner_text()
        try:
            self.trakingId=self.page.query_selector("div[class='pt-delivery-card-trackingId'],h4[class*='trackingId-text']").inner_text()
        except Exception as e:
            print(e)
            self.trakingId="-"
        self.page.locator("//a[text()='Ver detalles del pedido']").click()

    def is_order_wanted(self,dateofCard):
        #conver string to date object
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        dateofCard_date = datetime.strptime(dateofCard, '%d de %B de %Y')
        dateFrom_date = datetime.strptime(self.dateConfig["DESDE"], '%d/%m/%Y')
        dateTo_date = datetime.strptime(self.dateConfig["HASTA"], '%d/%m/%Y')
        
        if dateofCard_date>dateTo_date:
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
        obj_bill["Cupón/Puntos"]=0

        if "Buy any 4, Save 5%:" in keysDiscount :
            obj_bill["Cupón/Puntos"]=obj_bill["Cupón/Puntos"]+obj_bill["Buy any 4, Save 5%:"]
        if "Deal of the Day:" in keysDiscount:
            obj_bill["Cupón/Puntos"]=obj_bill["Cupón/Puntos"]+obj_bill["Deal of the Day:"]
        if "Your Coupon Savings:" in keysDiscount:
            obj_bill["Cupón/Puntos"]=obj_bill["Cupón/Puntos"]+obj_bill["Your Coupon Savings:"]
        self.info_bill=obj_bill
        
    def get_products_list(self):
        self.products_list=self.page.locator(detallesPedidos.products_list.selector).all()
        for product in self.products_list:
            self.priceProduct=product.locator(detallesPedidos.priceOfProduct.selector).inner_text()
            self.conditionProduct=product.locator(detallesPedidos.conditionOfProduct.selector).inner_text()
            self.sellerProduct=product.locator(detallesPedidos.sellerOfProduct.selector).inner_text()
            try:
                #timeout 3s
                self.page.wait_for_selector(detallesPedidos.quantityOfProduct.selector,timeout=3000)
                self.quantityProduct=product.locator(detallesPedidos.quantityOfProduct.selector).inner_text()
            except Exception as e:
                print(e)
                self.quantityProduct=1
            self.nameProduct=product.locator("div[class*='a-fixed-left-grid'] div[class*='a-row']:first-child>a").inner_text()
        self.page.locator("span[class*='track-package-button']").click()
        self.get_trakingInfo()
        self.page.locator("//span[@id='a-autoid-0']//a[contains(., 'Ver o Imprimir Recibo')]").click()
    def get_detailsOrderInfo(self):
        self.page.wait_for_selector(detallesPedidos.products_list.selector)
        order_date=self.page.query_selector(detallesPedidos.dateOfDetailsProduct.selector).inner_text()
        directions_list=self.page.locator(detallesPedidos.directions_list.selector).all_inner_texts()
        digitCards=self.page.locator("li>span:has(img)").inner_text()
        self.get_bill_info()
        self.get_products_list()
        for product in self.products_list:
            for q in range(int(self.quantityProduct)):
                data={
                    "date":order_date,
                    "orderId":self.orderIdOfCard,
                    "nameProduct":self.nameProduct,
                    "categoryProduct":"-",
                    "ASIN/ISBN":"-",
                    "UNSPSC Code":"-",
                    "Website":"Amazon",
                    "Release Date":"-",
                    "Condition":self.conditionProduct,
                    "Seller":self.sellerProduct,
                    "Seller Credentials":"-",
                    "Quantity":1,
                    "Purchase PriceUnit":self.priceProduct,
                    "Payment Instrument Type":digitCards,
                    "Purchase Order Number":"-",
                    "PO Line Number":"-",
                    "Ordering Customer Email":self.acount,
                    "shiptmentdate":self.shiptmentdate,
                    "address_name":directions_list[0],
                    "address_street1":directions_list[1],
                    "address_city":directions_list[2],
                    "address_state":directions_list[3],
                    "address_zip":directions_list[4],
                    "order_status":"-",
                    "trakingId":self.trakingId,
                    **self.info_bill
                }
                self.ScrapedData.append(data)
                var=[data]
                updateGshhet(var)
        self.get_pdf()
    
    def save_to_csv(self):
        with open('pedidos.csv', mode='w',newline='',encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.ScrapedData[0].keys())
            writer.writeheader()
            for data in self.ScrapedData:
                writer.writerow(data)
    def scrap_page(self):
        print("------------leyendo pagina")
        self.page.wait_for_selector(pedidosOverview.orderCards_list.selector)
        orderCards_list=self.page.locator(pedidosOverview.orderCards_list.selector).all()
        ordersLinks=[orderCard.locator("//a[contains(text(),'Ver detalles del pedido')]").get_attribute("href") for orderCard in orderCards_list]
        ordersAmounts=[orderCard.locator(pedidosOverview.amountOfCard.selector).inner_text() for orderCard in orderCards_list]
        ordersCouriers=[orderCard.locator(pedidosOverview.courierOfCard.selector).inner_text() for orderCard in orderCards_list]
        ordersIds=[orderCard.locator(pedidosOverview.orderIdOfCard.selector).inner_text() for orderCard in orderCards_list]
        ordersDates=[orderCard.locator(pedidosOverview.dateofCard.selector).inner_text() for orderCard in orderCards_list]
        print(f"numero de pedidos:{len(orderCards_list)}")
        for i,link in enumerate(ordersLinks):
            dateofCard=ordersDates[i]
            self.orderIdOfCard=ordersIds[i]
            r= self.is_order_wanted(dateofCard)
            if r=="stop":
                print("terminando de leer pedidos")
                break
            elif r=="skip":
                print(f"Saltando pedido {self.orderIdOfCard}...")
                continue
            print(f"leyendo pedido {self.orderIdOfCard}...")
            link="https://www.amazon.com"+link
            time.sleep(1)
            self.page.goto(link,wait_until="load")
            self.get_detailsOrderInfo()
            
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
        while len(self.page.query_selector_all(pedidosOverview.button_next.selector))>0:
            self.switch_to_tab(tab)
            self.scrap_page()
            tab+=1
            time.sleep(1)
            Url=previusUrl(tab)
            
    def scrap_info(self):
        self.page.wait_for_selector(homeLogin.buttons_cuentas.selector)
        account_list=self.page.query_selector_all(homeLogin.buttons_cuentas.selector)
        acounts_strings=[account.inner_text() for account in account_list]
        for account in acounts_strings:
            selectorAcount=f"//div[contains(text(),'{account}')]"
            self.acount=account
            self.page.locator(selectorAcount).click()
            self.page.wait_for_selector(mainView.button_orders.selector)
            print(f"leyendo en cuenta:{self.acount}")
            self.scrap_account()
            self.go_to_login()

    def end(self):
        self.page.close()
        self.browser.close()
        self.p.stop()

if __name__ == "__main__":
    amazonPage=Amazon()
    amazonPage.go_to_login()
    amazonPage.scrap_info()
    amazonPage.save_to_csv()
    amazonPage.end()


