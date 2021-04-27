import numpy as np
import random

# test = [{1,2},{2,3},{3,4}]

# chosen = random.sample(test, 1)

# print(chosen)

# test.remove(chosen[0])

# test.append(chosen[0])

# test[-1] = {5,6}

# print(test)


def guarantee():
    
    print('I am running')
    
    target = []
    
    if random.random() < 0.5:
        target = [1]
    
    if len(target) < 1:
        target = guarantee()
        
    return target
    
a = guarantee()

print(a)