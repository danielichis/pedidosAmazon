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
    url="https://script.google.com/macros/s/AKfycbxFVqbvPRV9eVlf-OfTzNGAcuXVDRTYN5YxdndwyTrIxL6Myw_lE7N9f5udjzstSWy7/exec"
    response = requests.post(url, json=data)
    postData=response.text
    print(postData)
    return postData

if __name__ == "__main__":
    updateGshhet()