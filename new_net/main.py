from classes import Chemical, Reaction, Network
from utils import compete
import random

# random.seed(814486224)

chem_001 = Chemical(formula='001', initial_conc=0.004218, decay=2.721381)
chem_011 = Chemical(formula='011', initial_conc=0.155827, decay=3.738387)
chem_01 = Chemical(formula='01', initial_conc=0.045266, decay=0.873102)
chem_0011 = Chemical(formula='0011', initial_conc=0.669255, decay=3.171469, inflow=0.372868)
chem_000 = Chemical(formula='000', initial_conc=1.617242, decay=3.626139)
chem_0 = Chemical(formula='0', initial_conc=4.278178, decay=4.204123)
chem_00 = Chemical(formula='00', initial_conc=0.866823, decay=1.552885)
chem_0001 = Chemical(formula='0001', initial_conc=0.628683, decay=1.969112)
chem_1 = Chemical(formula='1', initial_conc=1.349662, decay=5.946280)
chem_0111 = Chemical(formula='0111', initial_conc=0.283833, decay=0.047865)
chem_11 = Chemical(formula='11', initial_conc=0.255579, decay=3.106958)
chem_111 = Chemical(formula='111', initial_conc=1.008871, decay=0.217617)

chemicals = [chem_001, chem_011, chem_01, chem_0011, chem_000, chem_0, chem_00, chem_0001, chem_1, chem_0111, chem_11, chem_111]

reactions = [Reaction([chem_000], [chem_0, chem_00], 36.145961, 0.718663), Reaction([chem_000, chem_0011], [chem_001, chem_0001], 0.063361, 0.001476), Reaction([chem_001, chem_011], [chem_0011, chem_01], 25.894759, 0.048347), Reaction([chem_01, chem_01], [chem_0011], 16.858558, 14.660408), Reaction([chem_00, chem_01], [chem_0001], 6.469377, 0.169316), Reaction([chem_011, chem_0011], [chem_001, chem_0111], 31.534313, 21.501031), Reaction([chem_01, chem_011], [chem_0, chem_0111], 21.921524, 0.333969), Reaction([chem_000, chem_1], [chem_0001], 7.239927, 0.000074), Reaction([chem_111, chem_011], [chem_11, chem_0111], 23.652974, 0.087727)]

dt = 0.01
duration = 1000
boluses = [200, 500, 800]

champ = Network(chemicals, reactions)
champ.evaluate(duration, boluses)

random_net = Network()
random_net.evaluate(duration, boluses, plot=True)

winner, loser = compete(random_net, champ)

print(winner)
print(loser) 

# plt.plot(stimulus, color='blue', label='Stimulus')
# plt.plot(control, color='green', label='Control')
# plt.plot(output, color='black', label='Output')
# plt.legend()
# plt.xlabel('Iteration')
# plt.ylabel('Concentration')
# plt.show()