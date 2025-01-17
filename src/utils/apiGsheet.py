import requests

def send_last_report():
    return [{
        "nombre": "Juan",
        "edad": 30,
        "sexo": "M",
        "temperatura": 36.5,
        "sintomas": "ninguno",
        "contacto": "ninguno",
        "covid": "no",
        "fecha": "2021-08-26",
        "hora": "12:00:00"
    },
    {
        "nombre": "Jose",
        "edad": 30,
        "sexo": "M",
        "temperatura": 36.5,
        "sintomas": "ninguno",
        "contacto": "ninguno",
        "covid": "no",
        "fecha": "2021-08-26",
        "hora": "12:00:00"
    }]


def updateGshhet(data=None):
    url="https://script.google.com/macros/s/AKfycbx5jvG8goRcMwd7qOw74cNs-2Fcp2WuC1MmiSh1Ht6WLS5y9tFpsg4xDWKfeGA5S7hYUg/exec"
    url2="https://script.google.com/macros/s/AKfycbzZxTrxPnDIRqSAt_7iRjkgYt9EJNRtkaHg73ZLwfnmblJ6hd2uOQVFQop77GFRtrFYag/exec"
    response = requests.post(url2, json=data)
    postData=response.text
    if response.status_code==200:
        print("Se cargó compra exitosamente al google sheets")
    else:
        print("No se cargó compra al Google sheets")
        raise Exception("Error al cargar compra")
    #print(postData)
    return postData
def updateGshhet_test():
    data=send_last_report()
    print(updateGshhet(data))

if __name__ == "__main__":
    updateGshhet_test()