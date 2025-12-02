from Acao import Acao
from Observacao import Observacao

class AgenteBase:
    def __init__(self, nome):
        self.nome = nome
        self._sensor = None

    @staticmethod
    def cria(nome_do_ficheiro_parametros=None):
        raise NotImplementedError

    def instala(self, sensor):
        self._sensor = sensor

    def observacao(self, obs):
        raise NotImplementedError

    def age(self):
        raise NotImplementedError

    def avaliacaoEstadoAtual(self, recompensa: float):
        pass

    def comunica(self, mensagem: str, de_agente):
        pass

from Acao import Acao

class AgenteFarol(AgenteBase):

    MOVS = {
        "N":  (0, -1),
        "S":  (0, 1),
        "E":  (1, 0),
        "W":  (-1, 0),
    }

    def __init__(self, nome):
        super().__init__(nome)
        self._ultima_obs = None

    @staticmethod
    def cria(nome_do_ficheiro_parametros=None):
        return AgenteFarol("Explorer")

    def observacao(self, obs):
        if isinstance(obs, str):
            self._ultima_obs = obs.upper()
        else:
            # caso seja objeto Observacao
            self._ultima_obs = obs.direcao.upper()

    def age(self) -> Acao:
        """Devolve sempre um objeto Acao"""

        if self._ultima_obs is None or self._ultima_obs == "AQUI":
            return Acao(0, 0)

        dx = dy = 0
        for ch in self._ultima_obs:
            if ch in self.MOVS:
                mx, my = self.MOVS[ch]
                dx += mx
                dy += my

        # lista de movimentos ordenada por prioridade
        opcoes = [
            (dx, dy),          # diagonal principal
            (dx, 0), (0, dy),  # componentes separadas
            (1,0), (-1,0), (0,1), (0,-1), (-1,-1),  # movimentos cardinais gerais
            (0,0)              # fallback: ficar parado
        ]

        # verificar com sensor
        for mx, my in opcoes:
            if self._sensor and self._sensor.livre(mx, my):
                return Acao(mx, my)

        # fallback final
        return Acao(0, 0)
