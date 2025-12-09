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
class AgenteFarol(AgenteBase):
    # Restrição: Apenas movimentos em cruz (Sem diagonais)
    MOVS = [(1,0), (-1,0), (0,1), (0,-1), (0,0)]

    def __init__(self, nome, ficheiro_pesos=None):
        super().__init__(nome)
        self.pesos = {a: random.uniform(-1,1) for a in self.MOVS}
        self.ultimo_movimento = (0, 0)

        self.ficheiro_pesos = ficheiro_pesos
        if ficheiro_pesos:
            self.carregar_pesos(ficheiro_pesos)

    def age(self):
        # 1. Ler sensores
        direcao_farol = ""
        movimentos_livres = []

        if not self.sensores:
            return Acao(0,0)

        for sensor in self.sensores:
            reading = sensor.observacao()
            if isinstance(reading, str):
                direcao_farol = reading
            elif isinstance(reading, list):
                movimentos_livres = reading

        # 2. Filtrar movimentos
        # Se o SensorLivre falhar, usa todos. Se funcionar, usa só os livres.
        opcoes_validas = movimentos_livres if movimentos_livres else self.MOVS
        possible_moves = [m for m in self.MOVS if m in opcoes_validas]

        # Remover (0,0) se houver outras opções para evitar preguiça
        if len(possible_moves) > 1 and (0,0) in possible_moves:
            possible_moves.remove((0,0))

        if not possible_moves:
            return Acao(0,0)

        # --- ALTERAÇÃO 1: AUMENTAR EXPLORAÇÃO (20%) ---
        # Aumentado de 0.10 para 0.20 para ajudar a sair de mínimos locais (fitness 284)
        if random.random() < 0.20:
            acao = random.choice(possible_moves)
            self.ultimo_movimento = acao
            return Acao(*acao)

        # 4. Decisão Racional
        dx_target, dy_target = 0, 0
        if direcao_farol:
            if "N" in direcao_farol: dy_target -= 1
            if "S" in direcao_farol: dy_target += 1
            if "E" in direcao_farol: dx_target += 1
            if "W" in direcao_farol: dx_target -= 1

        melhor_score = -float("inf")
        melhor_acao = possible_moves[0]

        for a in possible_moves:
            dx, dy = a
            score = self.pesos[a]

            # Recompensa Direção
            # Nota: Mesmo sem diagonais no MOVS, isto funciona porque aproxima num dos eixos
            if (dx == dx_target and dy == dy_target):
                score += 0.5
            elif (dx != 0 and dx == dx_target) or (dy != 0 and dy == dy_target):
                score += 0.5

            # --- ALTERAÇÃO 2: REDUZIR PENALIZAÇÃO (-1.0) ---
            # Reduzido de -2.5 para -1.0.
            # Permite recuar se estiver num beco sem saída, sem bloquear.
            last_dx, last_dy = self.ultimo_movimento
            if dx == -last_dx and dy == -last_dy and (dx != 0 or dy != 0):
                score -= 1.0

            if score > melhor_score:
                melhor_score = score
                melhor_acao = a

        self.ultimo_movimento = melhor_acao
        return Acao(*melhor_acao)

    def salvar_pesos(self, ficheiro=None):
        f = ficheiro or self.ficheiro_pesos
        if f:
            with open(f, "w") as file:
                json.dump({str(k): v for k,v in self.pesos.items()}, file)

    def carregar_pesos(self, ficheiro):
        try:
            with open(ficheiro, "r") as f:
                dados = json.load(f)
                self.pesos = {}
                for k, v in dados.items():
                    key_tuple = tuple(map(int, k.replace('(','').replace(')','').split(',')))
                    self.pesos[key_tuple] = v
        except FileNotFoundError:
            pass # Inicia com pesos aleatórios se não existir ficheiro