# Questions

## 24 March 2021

1. All variables initialised at 0.05  
Correct

2. 2.5 million iterations but Figure 6 shows it as mid way  
Just a typo

3. Is C concentration correct? (page 6 says typically range between 0 and 2 but peaks at 10)  
That's fine

4. The probability of tumbling is too low to remain at areas of high M and E; even when visiting highly desirable areas, bacteria doesn't stay there at all  
Distribution - cannot tell from an individual bacterium's path

5. Do concentrations (variables in square brackets) need to be normalised or something?  
No

**Papers to read:**

- Associative Learning on a Continuum in Evolved Dynamical Neural Networks (Izquierdo, 2008)

## 31 March 2021

1. dt = 0.01?  
That's fine

2. Initial values are all 0 except for c=0.5 and h=1?  
Correct

- Autocatalytic reactions could be a form of memory where, once a bacteria is exposed to an element, it allows the autocatalytic reaction to occur
- But this isn't scalable - you'd need an element for every unique combination of reactants
- What sort of ODE's would allow a bacterium to escape a local optimum?
  - Random chance of performing antichemotaxis
  - Bacterium leaves behind "waste" products that are toxic
  - Local resources deplete
  - Predator and prey model

**Papers to read:**

- Evolving Action Selection and Selective Attention Without Actions, Attention, or Selection (Seth, 1998)
- The Microbial Genetic Algorithm (Harvey, 2009)
- Evolution of Associative Learning in Chemical Networks (McGregor, 2012)

## 7 April 2021

- Feel free to play around with parameters until you get something that works (and adopt this approach in general)
- Metabolution tumbling probability
  - No squaring [C] and [W]
  - Adjusting the 0.001 to 0.01
  - Repeat plots again to see effect
- Thesis may look like:
  1. Chapter 1: Reproducing minimal model/metabolution
  2. Chapter 2: Methods of extending to more complex behaviours that can emerge/evolve (lit review?)
  3. Chapter 3: McGregors Paper
  4. Chapter 4: Evolving a system then "embodying" it to perform associative learning vs evolving an embodied system to perform associative learning and seeing how they compares
- Concept of "embodied associative learning"

**Tasks:**

- Fully understand McGregor paper and summarise
- Watch Zoom link from Matthew
- Fix gradient-climbing