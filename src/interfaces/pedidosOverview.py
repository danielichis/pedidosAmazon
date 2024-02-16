from pedidosAmazon.src.utils.selectores import localizador

button_next=localizador("Boton siguiente","li[class='a-last']","css")
orderCards_list=localizador("Tarjetas de pedidos","div[class*='a-box-group a-spacing-base']","css")
orderCards_list2=localizador("Tarjetas de pedidos","div[id='ordersContainer']>div[class*='js-order-card']","css")
dateofCard=localizador("Fecha de pedido de la tarjeta","div[class='a-row']>div:nth-child(1)>div:nth-child(2) span","css")
amountOfCard=localizador("Monto de pedido de la tarjeta","div[class='a-row']>div:nth-child(2)>div:nth-child(2)","css")
courierOfCard=localizador("Courier de pedido de la tarjeta","div[id*='a-popover-shippingAddress']>span span","css")
orderIdOfCard=localizador("Id de pedido de la tarjeta","span[dir='ltr'],span>bdi","css")
detailsOfCard=localizador("Detalles de pedido de la tarjeta","ul a:nth-child(1)","css")







