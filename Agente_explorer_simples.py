# agente_explorer_simples.py

import random
from Agent import AgenteBase


class ExplorerSimples(AgenteBase):
    def __init__(self, nome, world):
        super().__init__(nome)
        self.world = world
        self.chaves = {}     # nome -> Key
        self.mapeamento = {} # chave -> tesouro (temporário)

    # -----------------------------
    # Decidir movimento
    # -----------------------------
    def decidir(self, observacao):
        # movimentos permitidos (dx, dy)
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return random.choice(movimentos)

    # -----------------------------
    # Recolher chave
    # -----------------------------
    def recolher_chave(self, key):
        # Guarda chave internamente
        self.chaves[key.name] = key

        # Mapeamento temporário:
        # K1 abre T1, K2 abre T2, K3 abre T3 (igual ao teu Simulator original)
        if key.name == "K1":
            self.mapeamento["K1"] = "T1"
        elif key.name == "K2":
            self.mapeamento["K2"] = "T2"
        elif key.name == "K3":
            self.mapeamento["K3"] = "T3"

        print(f"[{self.nome}] Apanhou chave {key.name}")

    # -----------------------------
    # Tentar abrir tesouro
    # -----------------------------
    def abrir_tesouro(self, treasure_name):
        # Verifica se alguma chave do agente abre este tesouro
        for chave, abre in self.mapeamento.items():
            if abre == treasure_name:
                print(f"[{self.nome}] Abriu tesouro {treasure_name} com {chave}")
                return True

        # Se não tiver chave correspondente → falha
        print(f"[{self.nome}] NÃO conseguiu abrir {treasure_name}")
        return False
