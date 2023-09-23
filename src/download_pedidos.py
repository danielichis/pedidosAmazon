from playwright.sync_api import sync_playwright
from utils.readconfig import settingsData as stt
from tqdm import tqdm
from src.interfaces import mainView,homeLogin,pedidosOverview,detallesPedidos,trakingView
from src.utils.functions import previusUrl
from PIL import Image
import time

class Amazon:
    def __init__(self) -> None:
        p= sync_playwright().start()
        browser = p.chromium.launch_persistent_context(user_data_dir=stt.user_data_dir,headless=stt.headless)
        self.page = browser.new_page()
        self.urlMain=stt.URLS_LINKS["URL-MAIN"]
        self.urlSignin=stt.URLS_LINKS["URL-SIGIN"]
        self.urlOrders=stt.URLS_LINKS["URL-ORDERS"]
    def go_to_login(self):
        self.page.goto(self.urlSignin)
        self.page.wait_for_url(self.urlSignin)

    def go_to_orders(self):
        self.page.locator(mainView.button_orders.selector).click()
        self.page.wait_for_selector(pedidosOverview.orderCards_list.selector)
    def get_pdf(self):
        pass
    def get_trakingInfo(self):
        self.page.wait_for_selector(trakingView.button_updates.selector)
        shiptmentdate=self.page.query_selector(trakingView.shiptmentdate.selector).inner_text()
        trakingId=self.page.query_selector(trakingView.trakingId.selector).inner_text()

    def is_order_wanted(self,dateofCard):
        return True
    def get_detailsOrderInfo(self):
        self.page.wait_for_selector(detallesPedidos.products_list.selector)
        date=self.page.query_selector(detallesPedidos.dateOfDetailsProduct.selector).inner_text()
        directions_list=self.page.query_selector_all(detallesPedidos.directions_list.selector).all_inner_text()
        digitCards=self.page.query_selector(detallesPedidos.digitCards.selector).inner_text()
        summaryBill=self.page.query_selector_all(detallesPedidos.summaryConcept_list.selector)
        products_list=self.page.query_selector_all(detallesPedidos.products_list.selector)
        for product in products_list:
            priceProduct=product.query_selector(detallesPedidos.priceOfProduct.selector).inner_text()
            conditionProduct=product.query_selector(detallesPedidos.conditionOfProduct.selector).inner_text()
            sellerProduct=product.query_selector(detallesPedidos.sellerOfProduct.selector).inner_text()
            quantityProduct=product.query_selector(detallesPedidos.quantityOfProduct.selector).inner_text()
            nameProduct=product.query_selector(detallesPedidos.nameOfProduct.selector).inner_text()
            dateDetailsProduct=product.query_selector(detallesPedidos.dateDetailsProduct.selector).inner_text()
        self.page.locator(detallesPedidos.trackingInfo.selector).click()
        self.get_trakingInfo()
        self.page.locator(detallesPedidos.button_pdf.selector).click()
        self.get_pdf()
    def scrap_page(self):
        print("------------leyendo pagina")
        self.page.wait_for_selector(pedidosOverview.orderCards_list.selector)
        orderCards_list=self.page.query_selector_all(pedidosOverview.orderCards_list.selector)
        print(f"numero de pedidos:{len(orderCards_list)}")
        for orderCard in orderCards_list:
            dateofCard=orderCard.query_selector(pedidosOverview.dateofCard.selector).inner_text()
            if not self.is_order_wanted(dateofCard):
                continue
            amountOfCard=orderCard.query_selector(pedidosOverview.amountOfCard.selector).inner_text()
            courierOfCard=orderCard.query_selector(pedidosOverview.courierOfCard.selector).inner_text()
            orderIdOfCard=orderCard.query_selector(pedidosOverview.orderIdOfCard.selector).inner_text()
            print(f"leyendo pedido:{orderIdOfCard}")
            detailsOfCard=orderCard.query_selector(pedidosOverview.detailsOfCard.selector).get_attribute("href")
            orderCard.query_selector(pedidosOverview.detailsOfCard.selector).click()
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
        self.account_list=self.page.query_selector_all(homeLogin.buttons_cuentas.selector)
        for account in self.account_list:
            self.acount=account.inner_text()
            account.click()
            self.page.wait_for_selector(mainView.button_orders.selector)
            print(f"leyendo en cuenta:{self.acount}")
            self.scrap_account()
            self.go_to_login()


if __name__ == "__main__":
    amazonPage=Amazon()
    amazonPage.go_to_login()
    amazonPage.scrap_info()


