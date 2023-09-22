from utils.selectores import localizador

orderCards_list=localizador("Tarjetas de pedidos","div[class='order-card js-order-card']","css")
dateofCard=localizador("Fecha de pedido de la tarjeta","div[class='a-row']>div>div:nth-child(2) span","css")
amountOfCard=localizador("Monto de pedido de la tarjeta","div[class='a-row']>div:nth-child(2)>div:nth-child(2)","css")
courierOfCard=localizador("Courier de pedido de la tarjeta","div[class='a-row']>div:nth-child(3)>div:nth-child(1)>div:nth-child(2)","css")
orderIdOfCard=localizador("Id de pedido de la tarjeta","span[dir]","css")
detailsOfCard=localizador("Detalles de pedido de la tarjeta","a[class='a-link-normal']","css")





