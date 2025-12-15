import random
import json
from Acao import Acao

# -----------------------------------------------------------
# 1. AgenteBase
# -----------------------------------------------------------
class AgenteBase:
    def __init__(self, nome):
        self.nome = nome
        self.sensores = []

    def instala(self, sensor):
        self.sensores.append(sensor)

    def age(self): raise NotImplementedError
    def avaliacaoEstadoAtual(self, recompensa): pass

# -----------------------------------------------------------
# 2. AgenteFarol OTIMIZADO (Modo Labirinto)
# -----------------------------------------------------------
class AgenteFarolQLearning(AgenteBase):
    MOVS = [(1,0), (-1,0), (0,1), (0,-1), (0,0)]

    def __init__(self, nome, alpha=0.2, gamma=0.95, epsilon=0.2,
                 epsilon_min=0.05, epsilon_decay=0.995, qfile=None, modo="LEARNING"):
        super().__init__(nome)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.modo = modo  # "LEARNING" ou "TEST"

        self.q = {}  # dict: state_str -> dict(action_str -> value)
        self.qfile = qfile
        if qfile:
            self.load_q(qfile)

        # para update
        self._s_prev = None
        self._a_prev = None

    def _state_from_sensors(self):
        direcao = ""
        livres = []

        for sensor in self.sensores:
            reading = sensor.observacao()
            if isinstance(reading, str):
                direcao = reading
            elif isinstance(reading, list):
                livres = reading

        # filtrar livres só para MOVS (cruz + 0)
        livres_set = set(livres) if livres else set(self.MOVS)
        mask = tuple(1 if m in livres_set else 0 for m in self.MOVS)

        if direcao == "":
            direcao = "UNK"

        return (direcao, mask)

    def _skey(self, s):
        # chave estável para dict/json
        direcao, mask = s
        return f"{direcao}|{''.join(map(str,mask))}"

    def _akey(self, a):
        return str(tuple(a))  # "(1, 0)" etc.

    def _ensure_state(self, skey):
        if skey not in self.q:
            self.q[skey] = {self._akey(a): 0.0 for a in self.MOVS}

    def _best_action(self, skey, valid_actions):
        self._ensure_state(skey)
        best_a = valid_actions[0]
        best_v = -float("inf")
        for a in valid_actions:
            v = self.q[skey][self._akey(a)]
            if v > best_v:
                best_v = v
                best_a = a
        return best_a

    def age(self):
        s = self._state_from_sensors()
        skey = self._skey(s)
        self._ensure_state(skey)

        # ações válidas (só as com mask=1)
        _, mask = s
        valid_actions = [a for a, ok in zip(self.MOVS, mask) if ok]
        if len(valid_actions) > 1 and (0,0) in valid_actions:
            valid_actions.remove((0,0))

        # epsilon-greedy no modo LEARNING; greedy no modo TEST
        if self.modo == "LEARNING" and random.random() < self.epsilon:
            a = random.choice(valid_actions)
        else:
            a = self._best_action(skey, valid_actions)

        # guardar para update
        self._s_prev = s
        self._a_prev = a

        return Acao(*a)

    def avaliacaoEstadoAtual(self, recompensa):
        # se ainda não há transição anterior, não atualiza
        if self._s_prev is None or self._a_prev is None:
            return

        if self.modo != "LEARNING":
            return

        # estado atual (s')
        s2 = self._state_from_sensors()
        skey = self._skey(self._s_prev)
        skey2 = self._skey(s2)
        self._ensure_state(skey)
        self._ensure_state(skey2)

        akey = self._akey(self._a_prev)

        # Q-learning update:
        # Q(s,a) <- Q(s,a) + alpha*(r + gamma*max_a' Q(s',a') - Q(s,a))
        max_next = max(self.q[skey2].values())
        old = self.q[skey][akey]
        target = recompensa + self.gamma * max_next
        self.q[skey][akey] = old + self.alpha * (target - old)

    def fim_episodio(self):
        # reduzir epsilon após episódio
        if self.modo == "LEARNING":
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self._s_prev = None
        self._a_prev = None

    def save_q(self, path):
        with open(path, "w") as f:
            json.dump(self.q, f)

    def load_q(self, path):
        try:
            with open(path, "r") as f:
                self.q = json.load(f)
        except FileNotFoundError:
            self.q = {}
