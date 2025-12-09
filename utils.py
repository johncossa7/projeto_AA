import random
from Agent import AgenteFarol
from Sensor import SensorObservacao, SensorLivre
from Simulator import Simulator

def fitness(agente, world_file, max_passos=50, render=False):
    sim = Simulator.cria(world_file)

    # Reinstalar sensores para o novo mundo
    agente.sensores = []
    agente.instala(SensorObservacao(sim.world, 0))
    agente.instala(SensorLivre(sim.world, 0))

    sim.agents[0] = agente
    sim.world.agent_pos[0] = sim.world.spawn_agent_pos
    chegou = False

    for passo in range(1, max_passos + 1):
        acao = agente.age()
        sim.world.agir(0, acao)

        if render: sim.world.render()

        if sim.world.agent_pos[0] == sim.world.farol_pos:
            chegou = True
            break

    ax, ay = sim.world.agent_pos[0]
    fx, fy = sim.world.farol_pos
    print (ax, ay, fx, fy)
    dist_final = abs(fx - ax) + abs(fy - ay)

    if chegou:
        return max_passos - passo
    else:
        return max_passos - dist_final

def crossover(pai1, pai2):
    filho = AgenteFarol("filho")
    filho.pesos = {a: random.choice([pai1.pesos[a], pai2.pesos[a]]) for a in pai1.MOVS}
    return filho

def mutacao(agente, taxa=0.1, amplitude=1.0):
    for a in agente.MOVS:
        if random.random() < taxa:
            agente.pesos[a] += random.uniform(-amplitude, amplitude)
            agente.pesos[a] = max(min(agente.pesos[a], 5), -5)

def evoluir(world_file, populacao=10, geracoes=20, max_passos=50, ficheiro_melhor=None):
    popul = []
    if ficheiro_melhor:
        try:
            popul.append(AgenteFarol("MelhorGlobal", ficheiro_pesos=ficheiro_melhor))
        except FileNotFoundError: pass

    while len(popul) < populacao:
        popul.append(AgenteFarol(f"Agente{len(popul)}"))

    melhor_global_valor = None
    melhor_global_agente = None

    for g in range(geracoes):
        scores = [(fitness(ag, world_file, max_passos), ag) for ag in popul]
        scores.sort(key=lambda x: x[0], reverse=True)

        melhor_atual_valor = scores[0][0]
        melhor_atual_agente = scores[0][1]

        if melhor_global_valor is None or melhor_atual_valor > melhor_global_valor:
            melhor_global_valor = melhor_atual_valor
            melhor_global_agente = melhor_atual_agente

        print(f"Geração {g+1} | Melhor fitness: {melhor_atual_valor:.2f} | Melhor global: {melhor_global_valor:.2f}")

        # Elitismo: Mantém o melhor
        top = [ag for _, ag in scores[:populacao//2]]
        nova_popul = [melhor_atual_agente]

        while len(nova_popul) < populacao:
            pai1, pai2 = random.sample(top, 2)
            filho = crossover(pai1, pai2)
            mutacao(filho)
            nova_popul.append(filho)
        popul = nova_popul

    if melhor_global_agente:
        melhor_global_agente.salvar_pesos(ficheiro_melhor or "melhor_agente.json")
    return melhor_global_agente