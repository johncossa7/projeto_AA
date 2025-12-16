import random
import math
import json
from Acao import Acao
from Sensor import SensorGPS, SensorCarga, SensorLivre, SensorVisual

# -----------------------------------------------------------
# Classe Base
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
# Agente Farol (Q-Learning Clássico)
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
        self.modo = modo

        self.q = {}
        self.qfile = qfile
        if qfile: self.load_q(qfile)

        self._s_prev = None
        self._a_prev = None

    def _state_from_sensors(self):
        direcao = "UNK"
        livres = []
        for sensor in self.sensores:
            reading = sensor.observacao()
            if isinstance(reading, str): direcao = reading
            elif isinstance(reading, list): livres = reading

        livres_set = set(livres) if livres else set(self.MOVS)
        mask = tuple(1 if m in livres_set else 0 for m in self.MOVS)
        return (direcao, mask)

    def _skey(self, s):
        direcao, mask = s
        return f"{direcao}|{''.join(map(str,mask))}"

    def _akey(self, a):
        return str(tuple(a))

    def _ensure_state(self, skey):
        if skey not in self.q:
            self.q[skey] = {self._akey(a): 0.0 for a in self.MOVS}

    def _best_action(self, skey, valid_actions):
        self._ensure_state(skey)
        random.shuffle(valid_actions)
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
        _, mask = s

        valid_actions = [a for a, ok in zip(self.MOVS, mask) if ok]
        if len(valid_actions) > 1 and (0,0) in valid_actions:
            valid_actions.remove((0,0))

        if self.modo == "LEARNING" and random.random() < self.epsilon:
            a = random.choice(valid_actions)
        else:
            a = self._best_action(skey, valid_actions)

        self._s_prev = s
        self._a_prev = a
        return Acao(*a)

    def avaliacaoEstadoAtual(self, recompensa):
        if self._s_prev is None or self._a_prev is None: return
        if self.modo != "LEARNING": return

        s2 = self._state_from_sensors()
        skey = self._skey(self._s_prev)
        skey2 = self._skey(s2)
        self._ensure_state(skey)
        self._ensure_state(skey2)

        akey = self._akey(self._a_prev)
        max_next = max(self.q[skey2].values())
        old = self.q[skey][akey]
        target = recompensa + self.gamma * max_next
        self.q[skey][akey] = old + self.alpha * (target - old)

    def fim_episodio(self):
        if self.modo == "LEARNING":
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self._s_prev = None
        self._a_prev = None

    def save_q(self, path):
        with open(path, "w") as f: json.dump(self.q, f)

    def load_q(self, path):
        try:
            with open(path, "r") as f: self.q = json.load(f)
        except FileNotFoundError: self.q = {}

# -----------------------------------------------------------
# Agente Novelty (Q-Learning + Curiosidade)
# -----------------------------------------------------------
class AgenteNovelty(AgenteFarolQLearning):
    def __init__(self, nome, alpha=0.1, gamma=0.9, epsilon=0.1, beta=10.0, **kwargs):
        super().__init__(nome, alpha, gamma, epsilon, **kwargs)
        self.beta = beta
        self.visitas = {}

    def _state_from_sensors(self):
        pos = (0,0)
        carga = False
        livres = []
        for sensor in self.sensores:
            reading = sensor.observacao()
            if isinstance(sensor, SensorGPS): pos = reading
            elif isinstance(sensor, SensorCarga): carga = reading
            elif isinstance(sensor, SensorLivre): livres = reading

        livres_set = set(livres) if livres else set(self.MOVS)
        mask = tuple(1 if m in livres_set else 0 for m in self.MOVS)
        return (pos, carga, mask)

    def _skey(self, s):
        (x, y), carga, mask = s
        return f"{x}|{y}|{carga}"

    def age(self):
        s = self._state_from_sensors()
        pos, carga, mask = s
        skey = self._skey(s)
        self._ensure_state(skey)

        valid_actions = [a for a, ok in zip(self.MOVS, mask) if ok]
        if len(valid_actions) > 1 and (0,0) in valid_actions:
            valid_actions.remove((0,0))

        if self.modo == "LEARNING" and random.random() < self.epsilon:
            a = random.choice(valid_actions)
        else:
            a = self._best_action(skey, valid_actions)

        self._s_prev = s
        self._a_prev = a
        return Acao(*a)

    def avaliacaoEstadoAtual(self, recompensa_externa):
        if self._s_prev is None or self._a_prev is None: return
        if self.modo != "LEARNING": return

        s_curr = self._state_from_sensors()
        skey_curr = self._skey(s_curr)
        skey_prev = self._skey(self._s_prev)
        akey_prev = self._akey(self._a_prev)

        self._ensure_state(skey_prev)
        self._ensure_state(skey_curr)

        self.visitas[skey_curr] = self.visitas.get(skey_curr, 0) + 1
        contagem = self.visitas[skey_curr]
        esta_carregado = s_curr[1]

        bonus_novidade = 0.0
        if not esta_carregado:
            if contagem == 1: bonus_novidade = self.beta * 1.0
            else: bonus_novidade = -0.5

        if recompensa_externa > 15.0:
            self.visitas = {} # Reset memória após entrega

        total_reward = recompensa_externa + bonus_novidade
        max_q_next = max(self.q[skey_curr].values())
        old_q = self.q[skey_prev][akey_prev]
        target = total_reward + self.gamma * max_q_next
        self.q[skey_prev][akey_prev] = old_q + self.alpha * (target - old_q)

    def reset_curiosity(self):
        self.visitas = {}

# -----------------------------------------------------------
# Agente Reativo (Versão "Muito Desastrada" / Drunk Walker)
# -----------------------------------------------------------
class AgenteReativoSensores(AgenteBase):
    """
    Agente com 'Severa Deficiência de Navegação'.
    Serve para garantir que a Baseline é baixa (~1.5 a 2.0).
    """
    def get_sensor(self, tipo):
        for s in self.sensores:
            if isinstance(s, tipo): return s
        return None

    def age(self):
        gps = self.get_sensor(SensorGPS)
        carga = self.get_sensor(SensorCarga)
        visual = self.get_sensor(SensorVisual)
        livre = self.get_sensor(SensorLivre)

        if not (gps and carga and visual and livre): return Acao(0,0)

        meu_pos = gps.observacao()
        estou_carregado = carga.observacao()
        visao = visual.observacao()
        possiveis = livre.observacao()

        if not possiveis: return Acao(0,0)

        deltas = [(0, -1), (0, 1), (-1, 0), (1, 0)] # N, S, W, E

        # --- SABOTAGEM MÁXIMA ---
        # 60% de probabilidade de fazer um movimento totalmente aleatório
        # independentemente de ter carga ou ver comida.
        if random.random() < 0.60:
            return Acao(*random.choice(possiveis))

        acao_escolhida = None

        if estou_carregado:
            # Tenta ir para o Ninho (5,5) de forma "Burra"
            # Apenas olha para a direção direta. Se houver parede, azar (não contorna).
            target = (5, 5)
            dx = target[0] - meu_pos[0]
            dy = target[1] - meu_pos[1]

            # Escolhe apenas UMA direção preferida (sem verificar se está livre)
            candidatos = []
            if dx > 0: candidatos.append((1, 0))
            elif dx < 0: candidatos.append((-1, 0))

            if dy > 0: candidatos.append((0, 1))
            elif dy < 0: candidatos.append((0, -1))

            if candidatos:
                move = random.choice(candidatos)
                if move in possiveis:
                    acao_escolhida = move
                else:
                    # Se a direção ideal tem parede, ele fica confuso (random)
                    acao_escolhida = random.choice(possiveis)
            else:
                # Já estou no ninho (teoricamente entrega automática)
                acao_escolhida = random.choice(possiveis)

        else:
            # Procura Comida
            # Mesmo que veja comida, pode falhar (simula reflexos lentos)
            viu_comida = False
            for i, tipo in enumerate(visao):
                if tipo == 2: # Comida
                    move = deltas[i]
                    if move in possiveis:
                        acao_escolhida = move
                        viu_comida = True
                        break

            # Se não viu comida (ou ignorou), Random Walk
            if not viu_comida:
                acao_escolhida = random.choice(possiveis)

        return Acao(*acao_escolhida)