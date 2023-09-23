from typing import Literal
class localizador():
    def __init__(self, descripcion:str, selector:str, tipo:Literal["css","xpath"]):
        self.descripcion = descripcion
        self.selector = selector
        self.tipo = tipo
    def __str__(self):
        return self.selector        
