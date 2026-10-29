from models.crud_base import CrudBase


class LocalizacaoModel(CrudBase):
    def __init__(self):
        super().__init__(
            tabela="localizacao",
            chave_primaria="id_localizacao",
            campos=[
                "nome",
                "setor",
                "corredor",
                "prateleira",
                "observacao"
            ]
        )