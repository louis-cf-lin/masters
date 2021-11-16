from Network import Network

net = Network()

net.print_derivs()

for reaction in net.reactions:
  print(reaction)