from Simulator import Simulator
from Sensor import SensorObservacao, SensorLivre
from Agent import AgenteFarolQLearning
import matplotlib.pyplot as plt

FICHEIRO = "world_farol.txt"

episodios = 400
max_passos = 60
qfile = "q_farol.json"

retornos = []
sucessos = []

sim = Simulator.cria(FICHEIRO)
ag = AgenteFarolQLearning("QL", alpha=0.2, gamma=0.95, epsilon=0.3,
                          epsilon_min=0.05, epsilon_decay=0.995, qfile=None, modo="LEARNING")
ag.sensores = []
ag.instala(SensorObservacao(sim.world, 0))
ag.instala(SensorLivre(sim.world, 0))
sim.agents[0] = ag

for ep in range(episodios):
    sim.world.agent_pos[0] = sim.world.spawn_agent_pos
    sim.world._terminado = False
    sim.passos = 0

    total_r = 0.0
    while sim.passos < max_passos and not sim.world.terminado():
        sim.passos += 1
        acao = ag.age()
        r = sim.world.agir(0, acao)
        total_r += r
        ag.avaliacaoEstadoAtual(r)
        sim.world.atualizacao()

    ag.fim_episodio()
    retornos.append(total_r)
    sucessos.append(1 if sim.world.terminado() else 0)

    if (ep+1) % 50 == 0:
        print(f"Ep {ep+1} | retorno={total_r:.2f} | sucesso={sum(sucessos[-50:])}/50 | eps={ag.epsilon:.3f}")

ag.save_q(qfile)

plt.figure()
plt.plot(retornos)
plt.xlabel("Episódio")
plt.ylabel("Retorno total (soma das recompensas)")
plt.title("Q-learning no Farol: curva de aprendizagem")
plt.show()

print("\n--- TESTE (greedy) ---")
sim2 = Simulator.cria(FICHEIRO)
ag2 = AgenteFarolQLearning("QL_TEST", qfile=qfile, modo="TEST", epsilon=0.0)
ag2.sensores = []
ag2.instala(SensorObservacao(sim2.world, 0))
ag2.instala(SensorLivre(sim2.world, 0))
sim2.agents[0] = ag2
sim2.executa(max_passos=80, render=True, delay=0.2)
