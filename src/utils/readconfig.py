import configparser
import os
class configData:
    def __init__(self) -> None:
        with open("settings.ini") as f:
            lines=f.readlines()
            self.URLS_LINKS={}
            for line in lines:
                if line.startswith("URL-SIGIN"):
                    self.URLS_LINKS["URL-SIGIN"]=line.replace("URL-SIGIN=","").replace("\n","").strip("\"")
                elif line.startswith("URL-MAIN"):
                    self.URLS_LINKS["URL-MAIN"]=line.replace("URL-MAIN=","").replace("\n","").strip("\"")
                elif line.startswith("URL-ORDERS"):
                    self.URLS_LINKS["URL-ORDERS"]=line.replace("URL-ORDERS=","").replace("\n","").strip("\"")
                elif line.startswith("HEADLESS"):
                    self.headless=bool(int(line.replace("HEADLESS=","").replace("\n","")))
                elif line.startswith("USER_DATA_DIR"):
                    self.user_data_dir=os.path.normpath(line.replace("USER_DATA_DIR=","").replace("\n","")).strip("\"")
                elif line.startswith("STORAGE_PATH"):
                    self.storage_path=line.replace("STORAGE_PATH=","").replace("\n","").strip("\"")

settingsData=configData()


