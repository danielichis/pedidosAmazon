from playwright.sync_api import sync_playwright
import json
import requests
import io
from tqdm import tqdm
import os
from PIL import Image
import csv

urlPedidosAmazon="https://www.amazon.com/-/es/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
urlHome="https://www.amazon.com/"
p= sync_playwright().start()
browser = p.chromium.launch(headless=False)
context=browser.new_context(storage_state="state_ped_amazon.json")
page = context.new_page()
page.goto(urlHome)
context.storage_state(path="state_ped_amazon.json")
#page.pause()
