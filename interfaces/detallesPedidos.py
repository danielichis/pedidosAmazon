from utils.selectores import localizador

directions_list=localizador("Lista de direcciones","div[class='displayAddressDiv'] li","css")
digitCards=localizador("Tarjetas de digitos","h5+div img+span","css")

summaryConcept_list=localizador("Lista de conceptos de resumen","div[id='od-subtotals'] div[class='a-row']","css")
nameOfSummaryConcept=localizador("Nombre de concepto de resumen","div:nth-child(1)","css")
valueOfSummaryConcept=localizador("Valor de concepto de resumen","div:nth-child(2)","css")

products_list=localizador("Lista de productos","div.a-fixed-left-grid","css")
priceOfProduct=localizador("Precio de producto","span[class='a-size-small a-color-price']","css")
conditionOfProduct=localizador("Condicion de producto","span[class='a-color-secondary']","css")
sellerOfProduct=localizador("Vendedor de producto","//span[contains(text(),'Vendido por:')]","css")
quantityOfProduct=localizador("Cantidad de producto","span[class='item-view-qty']","css")
nameOfProduct=localizador("Nombre de producto","div.a-fixed-left-grid div.a-row:first-child a","css")
dateOfDetailsProduct=localizador("Fecha de detalles de producto","//*[@id='orderDetails']//span[@class='order-date-invoice-item'][1]","xpath")

button_traking=localizador("Boton de traking","//a[contains(., 'Rastrear paquete')]","xpath")

button_pdf=localizador("Boton de pdf","//a[contains(., 'Ver o Imprimir Recibo')]","xpath")


