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

## 14 Apil 2021

### SBS Seminarr: Prof. Edo Kussell

#### Part I - Bacterial adaptation to metabolic fluctuations

> - How do cells respond in a fluctuating environment?
> - Emerging hypothesis: gene expression levels may be tuned not only for immediate conditions, but also to provide for future generations
> - This motivates us to perform a cost-benefit analysis of phenotypic memory in fluctuating conditions
> - When does phenotypic memory provide an advantage for cells that respond to a fluctuating environment?

#### Simplest model of sensing with memory

![Simplest model of sensing with memory](./notes_images/stress-growth.png)

#### Intuitive cost-benefit analysis of memory

![Intuitive cost-benefit analysis of memory](./notes_images/cost-benefit.png)

> - **In a rapidly changing environment, memory provides a selective advantage.** tau indicates mean duration. _b_ = benefit. Bottom yellow region is cost of having gene on when not needed.

- When does phenotypic memory provide an advantage for cells that respond to a fluctuating environment?  
  _When environments fluctuate rapidly_

- How much memory should cells use? i.e. is there an optimal value of the degradation rate? How does long-term growth rate vary with increasing protein degradation?

#### In a periodic environment

![Periodic environment](./notes_images/optimal-deg-rate.png)

> - **For a perioidic environment, the optimal response is either memoryless or a constitutive, while an intermediate amount of memory is never optimal**. All rates and times are given in units of generation time. Parameters: _b_=1.0, _c_=0.3, _k_on_=0.5

- Optimal solution is one extreme or the other
  - For longer environments, rapid degradation is optimal (memoryless)
  - For shorter environments, constitutively ON is better (long-term memory)

#### In a _randomly changing environment_

![Random environment](./notes_images/optimal-deg-rate-random.png)

> - All rates and times are given in units of generation time. Parameters: _b_=1.0, _c_=0.3, _k_on_=0.5, mean tau_env = 3.5

- For random environments, the optimal strategy is to go for the middle-ground solution: that is, not to suffer the consequences of extreme responses

#### How does the response strategy depend on the environment?

![Response strategy vs environment](./notes_images/optimisation-phase-diagram.png)

> - Each point corresponds to a different type of randomly changing environment

- Even when there are some randomness (albeit very low), the optimal strategy is still one extreme or the other
- Above a **critical variability**, the strategy is a smooth continuous value for memory

#### Implications

> - Sensing with memory is a survival strategy that is optimal exclusively in random environments
> - Changes in environmental statistics can drive response network evolution through transitions that can be continuous (e.g. fine-tuning) or discontinuous (e.g. gene gain or loss)
> - Theory predicts that evolutionary dynamics can be extremely sensitive to environmental timescales

#### Part II - Ecological memory and bacterial defense mechanisms

> 1. How bacteria defend against infection by bacteriophage
> 2. Phases of bacterial host-pathogen interactions
> 3. Maintaining costly defenses across variable environments

#### Background

> - Bacteriophages are viruses that infect bacteria
> - The lambda phage binds receptors on E. coli cells, injects its DNA, produces many new phage, and eventually lyses the bacterium

![lyse](./notes_images/lyse.png)

![phage entering cell](./notes_images/phage-entering-cell.png)

- Phage primarily uses LamB to enter a cell, which grows on maltose and maltotriose

#### How do bacteria adapt in the presence of phage?

![e coli vs phage](./notes_images/ecoli-phage.png)

![e coli vs phage](./notes_images/ecoli-phage-2.png)

![resistance switching](./notes_images/resistance-switching.png)

- Why doesn't malT just completely kill off the phage? Costs and benefits

![switching phases](./notes_images/switching-phases.png)

![cyclical competition](./notes_images/cyclical-comp.png)

- Cyclical competition (e.g. rock-paper-scissors)
- What are the long-term outcomes?

![localised patches](./notes_images/localised-patches.png)

![game theory](./notes_images/game-theory.png)

#### Implications

> - The resistance switching strategy is evolutionarily stable when the switching rate is smaller than the patch clearance rate (environment -> molecular mechanism)
> - Stochastic loss of resistance in single cells maintains sufficient level of phage across the ecology to prevent sensitive strains from taking over (single-cells -> ecological dynamics)
> - The resistance switching mechanism maintains memory of the phage across the ecology (molecular mechanism -> ecological memory)

---

Iteration 6 error

```terminal
c:\masters\metabolution.py:11: RuntimeWarning: overflow encountered in double_scalars
  return 0.01 * max(-0.1 + C**2 - 0.9*W**2, 0.01)
c:\masters\metabolution.py:11: RuntimeWarning: invalid value encountered in double_scalars
  return 0.01 * max(-0.1 + C**2 - 0.9*W**2, 0.01)
c:\masters\metabolution.py:30: RuntimeWarning: overflow encountered in double_scalars
  k_f = ...
c:\masters\metabolution.py:31: RuntimeWarning: overflow encountered in double_scalars
  k_b = ...
c:\masters\metabolution.py:33: RuntimeWarning: invalid value encountered in double_scalars
  # E
  # M
  # C
  # V
  # W
  # H
  # S
```

Iteration 14 error

```terminal
c:\masters\metabolution.py:39: RuntimeWarning: invalid value encountered in double_scalars
  # F
c:\masters\metabolution.py:39: RuntimeWarning: invalid value encountered in double_scalars
  # N
```

### To do

- Look at supplementary material for McGregor and attempt to implement
- Contact Yan Kollezhitskiy (via Slack or in-person)
- Think about:
  - Associative learning as a module (McGregor)
  - Chemotaxis as a module (min/metab)
  - Associative takes inputs S and C and outputs O
  - O gets fed into chemotaxis module
- Another idea: associative learning a temperature and moving towards it (kinda thermotaxis)

Artificial chemistries Wolfgang Banzhaf

Evolution on multiple timescales

## 28 April

- Try using k\_{favoured} = e^{-E_a} and k\_{unfavoured} = e^{-(E_A + (R\_{potential} - P\_{potential}))}
- Chemical initial concentrations should be set, and different from the current concentration

Fixes:

- Using new rate constant equations
- Fixed mirroring at ranges
- Fixed targets not incrementing

## 05 May

**Tasks:**

- Use RK4
- Refactor to separate genotype from phenotype with g2p mapping (check out attached Matthew's code)
- Confirm GA is working as hoped by giving it easy problems to solve:
  1. Fitness = sum of genes
  2. Fitness = final concentration of some specific chemical
  3. Consider adding visualisations of fitness, "gene pool" plot, or similar
- Mechanism to remove chemicals from networks
- GA exercise

## 12 May

**Progress:**

- RK4 requires additional formulation of ODE's
  - The paper used Euler so should be OK
- Decided to continue using phenotype as varying initialisation ranges make it inefficient to do g2p mapping
- Tested GA on optimising for an output chemical potential of 5
  - Without mutation, the plots match the outputs and correspond with optimisation
  - With mutation, plots show convergence
- There is a sigma\*5 probability of deleting a network

**Questions:**

- What is the mutation rate sigma?
- No adaptive mutation over time?
- What is the range for concentration? Is reflection used?
- What's a bolus and how is it implemented?

**Meeting notes:**

- Horizontal gene transfer
  - Inherit both parents' genes weighted on their fitness
  - i.e. don't completely replace genes
- Use demes
  - Compete only between neighbours
  - Visualise to see spread of "good" genes
- Use a **set** of systematically contrived tasks for deterministic evaluation
  - Store fitness so don't have to reevaluate
  - Can try creating new sets of tasks every _x_ generations
- Regererating entirely new generations and creating tasks for each new generation
- Secondary mutation rate (see Matthew's message)
  - **Every** mutatable property has some uniform chance of being mutated
- Think about combining associative learning in chemical networks with embodied chemotaxis

Dear Simon,

I hope you're well.

My name is Louis and I'm a Masters student studying under the supervision of Dr. Matthew Egbert, a former University of Sussex colleague of yours. I've been working on trying to reproduce your work in Evolution of Associative Learning in Chemical Networks (McGregor et al., 2012). I'm almost there, just missing a few key calculations and was hoping you could answer some of my questions.

1. As I understand, the favoured direction of reactions is determined by the chemical potential of the species involved. Is this just the sum of the chemical potentials of LHS species vs. RHS species? Or is it another means of determining the favoured direction?

2. From the paper, the favoured rate constant is an evolved parameter and the non-favoured rate constant is calculated using the chemical potential of the species involved. I'm currently using the following equations:

[insert equations here]

where E_a is the activation energy, R is the sum of reactants, and P is the sum of products. Given we have the favoured rate constant, and the all the chemical potentials, we can work backwards to calculate E_a, and thus, the non-favoured rate constant. Is this comparable/correct to your approach?

3. Why is the favoured rate constant an evolved parameter rather than, say, a characteristic of the chemicals involved (i.e. like the non-favoured rate constant)?

And a couple of other unrelated questions:

4. Was there a single mutation rate, sigma, that produced the champion networks? Did sigma change throughout the course of a protocol/task to help the population of networks converge?

5. The champion networks reported in the supporting text have fewer chemicals than I expected. This leads me to believe chemicals were also removed from networks during evolution, but the paper doesn't mention any mechanisms to do so. Was this the case? If so, what was the method? E.g. when reactions were removed from a network, the chemicals involved were also removed (provided they were not involved in another reaction).

Thank you for publishing your work, it's been an enjoyable challenge to code. I have appended the results of my reproducing your work with the parameters prescribed and I was happy to see comparable results to yours. Hope to hear from you soon.

Best regards,
Louis

[Attach plots]

## 26 May

- Combine associative learning with embodied approach

  - Associative learning is not relevant unless acted upon
  - Learn some association (e.g. temperature corresponds to toxin), then perform chemotaxis
  - Think about what are the actions available to an agent (most obvious is taxis)
  - Associate environment with metabolic state

- Rewatch the School of Biological Sciences talk (notes already written)
  - The dynamical plots are something I could recreate
  - Numerically map the behaviour by sampling at set intersections
- Read through [new paper](http://www.matthewegbert.com/files/EgbertDiPaoloBarandiaran2009_Chemoethology_of_an_adaptive_protocell.pdf)
- Brainstorm research questions
  - Draw out ideas on paper or whiteboard
  - Write a short "pitch" for each idea
  - Imagine what plots you would generate by the end (what are the axis labels etc.)
- 2D plot of fitness with an extra gene that tracks inheritance

## 9 June

- When to map genotype to phenotype? On every call?
- Should I write test cases?
- Is sigmoid threshold the point at which output is 0?
- Distance from circumference of center?
- Output scale?

set constants for gene index
write more classes e.g. for motor, sensors
prepareToUpdate() and update()

- Plots of sensor inputs and motor states
- Deterministic animat position and a different environment every generation
- Not spawn on top of trap
- Number of food and waters
- Scaling the environment to an appropriate range
- Consider not squashing in sigmoid function
-
