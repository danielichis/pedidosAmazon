from src.utils.selectores import localizador

button_next=localizador("Boton siguiente","li[class='a-last']","css")
orderCards_list=localizador("Tarjetas de pedidos","div[class='order-card js-order-card']","css")
dateofCard=localizador("Fecha de pedido de la tarjeta","div[class='a-row']>div>div:nth-child(2) span","css")
amountOfCard=localizador("Monto de pedido de la tarjeta","div[class='a-row']>div:nth-child(2)>div:nth-child(2)","css")
courierOfCard=localizador("Courier de pedido de la tarjeta","span>a","css")
orderIdOfCard=localizador("Id de pedido de la tarjeta","span>bdi","css")
detailsOfCard=localizador("Detalles de pedido de la tarjeta","ul a:nth-child(1)","css")







