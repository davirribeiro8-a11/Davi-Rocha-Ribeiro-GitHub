from core.crud_base import CrudBase
from core.validator import Validator


class Localizacao(CrudBase):

    table = "localizacao"

    fields = [
        "rua",
        "numero",
        "andar"
    ]

    def __init__(self, rua, numero, andar):
        self.rua = rua.strip()
        self.numero = numero.strip()
        self.andar = andar.strip()

    def validate(self):
        erros = [
            Validator.required(self.rua, "Rua"),
            Validator.required(self.numero, "Número"),
            Validator.required(self.andar, "Andar"),
        ]
        return [erro for erro in erros if erro]
