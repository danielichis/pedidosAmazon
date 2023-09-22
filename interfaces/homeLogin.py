from utils.selectores import localizador

boton_de_pedidos=localizador("Boton para entrar a mis pedidos","a[id='nav-orders']>span[class='nav-line-2']", "css")
boton_de_pedidos2=localizador("Boton para entrar a mis pedidos","//span[text()='y Pedidos']","xpath")

print(boton_de_pedidos.tipo)
