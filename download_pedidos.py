from playwright.sync_api import sync_playwright
from tqdm import tqdm
from PIL import Image
import time

urlLogin="https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
urlLogin2="https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_youraccount_switchacct&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&switch_account=picker&ignoreAuthState=1&_encoding=UTF8"
urlHome="https://www.amazon.com/"
p= sync_playwright().start()
browser = p.chromium.launch_persistent_context(user_data_dir=r"C:\Users\Daniel\AppData\Local\Google\Chrome\User Data2",headless=False)
#context=browser.new_context(storage_state="state_ped_amazon.json")
#context= browser.new_context()
page = browser.new_page()

def go_to_signin():
    page.goto(urlLogin)
    page.wait_for_url(urlLogin)
    page.wait_for_selector("//div[contains(text(),'.com')]")
    cuentas_web_elements=page.query_selector_all("//div[contains(text(),'.com')]")
    for cuenta in cuentas_web_elements:
        print(cuenta)
        cuenta.click()
        page.wait_for_url(urlHome)
        print(f"cuenta{cuenta.inner_text()}")
        page.goto(urlLogin)
        page.wait_for_url(urlLogin)
    #page.pause()
    #page.fill("input[type=email]", "email")
page.goto(urlLogin2)
page.wait_for_url(urlLogin2)
time.sleep(3)
page.pdf(path="pdf.pdf")
page.pause()
print("Login")
go_to_signin()
page.screenshot(path="screenshot.png")

#context.storage_state(path="state_ped_amazon.json")
print("Login OK")
