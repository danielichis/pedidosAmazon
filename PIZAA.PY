import locale
from datetime import datetime
class Pizza:
    def __init__(self):
        self.dateConfig = {
            "DESDE": "01/12/2022",
            "HASTA": "3 de febrero de 2024",
            "fechaDetalle":"Pedido el 3 de febrero de 2024"
        }
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        self.dateFrom_date = datetime.strptime(self.dateConfig["DESDE"], '%d/%m/%Y')
        self.dateTo_date = datetime.strptime(self.dateConfig["HASTA"], '%d de %B de %Y')
        self.dateofDetails_date = datetime.strptime(self.dateConfig["fechaDetalle"].replace("Pedido el ",""), '%d de %B de %Y')
p= Pizza()
print(p.dateFrom_date)
print(p.dateTo_date)
print(p.dateofDetails_date)
print("asdasdasdas")