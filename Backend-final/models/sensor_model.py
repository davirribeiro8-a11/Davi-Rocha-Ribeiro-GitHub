from models.crud_base import CrudBase
from core.database import conectar


class SensorModel(CrudBase):
    def __init__(self):
        super().__init__(
            tabela="cadastro_sensor",
            chave_primaria="id_sensor",
            campos=[
                "nome",
                "tipo_sensor",
                "codigo_sensor",
                "id_localizacao",
                "id_produto",
                "status"
            ]
        )

    def registrar_dados_sensor(self, dados):
        """
        Registra leitura enviada por sensor.
        Pode ser usado futuramente por IoT ou mobile.
        """
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
            INSERT INTO dados_sensor
            (id_sensor, valor, unidade)
            VALUES (%s, %s, %s)
        """

        valores = (
            dados.get("id_sensor"),
            dados.get("valor"),
            dados.get("unidade")
        )

        cursor.execute(sql, valores)
        conexao.commit()

        cursor.close()
        conexao.close()