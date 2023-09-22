from utils.selectores import localizador

label_trakingId=localizador("traking id para el rastreo","//div[contains(text(), 'ID de rastreo:')]","xpath")
button_updates=localizador("Boton de actualizaciones","a[data-ref='ppx_pt2_dt_b_pt_detail']","css")
label_shipmentDate=localizador("Fecha de envio","span[class='tracking-event-date']","css")


