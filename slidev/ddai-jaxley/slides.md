---
# try also 'default' to start simple
theme: seriph
# some information about your slides (markdown enabled)
author: Marco Christiani
title: Jaxley
info: |
  ## Jaxley
  Jaxley for scalable sims.
layout: cmu-cover
# https://sli.dev/features/drawing
drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations.html#slide-transitions
transition: slide-left
# enable MDC Syntax: https://sli.dev/features/mdc
mdc: true
# duration of the presentation
duration: 35min
# themeConfig:
#   primary: '#C41230'     # CMU Red
#   secondary: '#6D6E71'   # Iron Gray
#   accent: '#FDB515'      # Gold Thread
themeConfig:
  # === Core Colors ===
  primary: '#C41230' # Carnegie Red
  secondary: '#6D6E71' # Iron Gray
  text: '#000000' # Black
  background: '#FFFFFF' # White
  muted: '#E0E0E0' # Steel Gray

  # === Secondary ===
  accent: '#FDB515' # Gold Thread

  scotsRose: '#EF3A47' # Scots Rose
  greenThread: '#009647' # Green Thread
  tealThread: '#008F91' # Teal Thread
  blueThread: '#043673' # Blue Thread
  skyBlue: '#007BC0' # Highlands Sky Blue

  # === Campus ===
  machineryTan: '#BCB49E' # Machinery Hall Tan
  brickBeige: '#E4DAC4' # Kittanning Brick Beige
  hornbostelTeal: '#1F4C4C' # Hornbostel Teal
  palladianGreen: '#719F94' # Palladian Green
  weaverBlue: '#182C4B' # Weaver Blue
  skiboRed: '#941120' # Skibo Red
fonts:
  sans: Open Sans
  serif: Source Serif Pro
  mono: Fira Code
  weights: '300,400,600,700'
  italic: true
---

<!-- <template v-slot:institution>
Carnegie Mellon University
</template> -->

<template v-slot:title>
Presentation Title
</template>

<template v-slot:presenter>
{{$frontmatter.author}}
</template>
<template v-slot:presenter-title>
</template>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)

ss
-->

---
layout: cmu-body
---

<!-- # V1 Jaxley: Differentiable Training of Biophysical Neural Models

* Biophysically detailed neuron models capture mechanistic dynamics but are difficult to fit or train at scale. 
* Traditional simulators do not support automatic differentiation, limiting optimization to gradient-free methods. 
* Jaxley enables differentiable simulation using JAX-based automatic differentiation and GPU acceleration. 
* This allows gradient-based optimization of large numbers of biophysical parameters in single neurons and networks. 
* The framework scales to complex morphologies and large networks, making task training and data fitting computationally practical.  -->

## V2 Biophysical Models Are Difficult to Train

* Detailed neuron models are governed by nonlinear differential equations with many parameters (channel conductances, synaptic weights, morphology). 
* These parameters are not directly measurable and must be inferred from experimental recordings. 
* Fitting requires repeated simulation, which becomes computationally expensive as parameter count increases. 
* In practice, optimization often relies on gradient-free methods that scale poorly with dimensionality. 


---
layout: cmu-body
# layout: default
transition: fade-out
---

<!-- Problem Formulation -->

<!-- * Detailed biophysical neuron models are governed by nonlinear differential equations with many free parameters (e.g., channel conductances, synaptic weights). 
* These parameters are typically not directly measurable and must be inferred from voltage or calcium recordings. 
* Parameter inference is computationally expensive because simulation must be repeated many times. 
* Without gradients, optimization relies on genetic algorithms or other black-box search methods that scale poorly with parameter dimension. 
* This limits the ability to train large, mechanistic models or use them for complex task learning.  -->

## Jaxley's Core Idea

* Enables differentiable simulation of detailed biophysical neuron and network models. 
* Built on a GPU-first stack for scalable experimentation

<center>
<strong>
Makes gradient-based fitting and task training feasible at scales previously impractical.
</strong>
</center>

<!--

Uses automatic differentiation to compute gradients with respect to biophysical parameters. 
The rest of the paper demonstrates what this makes possible.
 -->

<!--

TODO: Missing a motivating hypothetical example/scenario. 

 -->

---

## Validation: Accuracy and scalability

- Accuracy: Jaxley matches NEURON voltage traces at sub-ms/sub-mV resolution. 
- GPU speedup: large parallel workloads become orders of magnitude faster.
- Gradient cost: gradients ~3-20x simulation depending on settings (can checkpoint). 
Scaling example: 2,000 morphologically detailed neurons + 1M synapses
  - Gradients w.r.t. millions of parameters on a single GPU
  - *Finite differences would be infeasible*


---

## Validation: Fitting a Single Neuron Model (Synthetic Data)
<!-- fig 2 from paper. the first example was verifying it against NEURON. -->

**Goal:** Recover biophysical parameters from voltage recordings.
- A morphologically detailed neuron model is simulated with known parameters. 
- Jaxley treats model parameters (e.g., conductances) as trainable variables. 
- The model produces a voltage trace in response to injected current.
- A loss function compares simulated voltage to the target trace.
- Gradients are computed via backpropagation through the solver. 

**Findings:** Gradient descent recovers parameters using far fewer simulations than a genetic algorithm. 

<!-- Important modeling takeaway is you must design differentiable features/losses, which leads into the next example -->
<!-- TODO: missing actual quantification and details about the biology, and a figure or two. L5 pyramidal cell -->
<!-- 
Possibly diagram smthg like "Known parameters → simulate voltage → compare to target → update parameters via gradient."

"This example establishes that gradient-based fitting works in principle."
-->
---

## V1 Fitting Real Patch-Clamp Recordings
<!-- fig 2 part b: real patch-clamp fitting needs differentiable alignment -->

**Goal:** Fit a detailed neuron model to real intracellular recordings.
**However,** small timing shifts in spike peaks cause large pointwise voltage errors, even if the model is qualitatively correct.

I.e., naive loss = pointwise voltage difference
- Highly sensitive to millisecond misalignment
- Poor gradient signal

Solution in the paper:
- Use a differentiable alignment-based loss (soft-DTW). 
- Run many (thousands) optimization restarts in parallel on GPU. 
- Select best-fitting parameter set.

**Result:** Good qualitative spike and waveform matches to experimental traces. 


---

## V2 Fitting Real Patch-Clamp Recordings

**Goal:** Fit a detailed biophysical neuron model to real intracellular voltage recordings. 

**Patch clamp recording:**

* A glass micropipette is inserted into a single neuron.
* It measures membrane voltage over time while controlled current is injected.
* Output: high-resolution voltage trace with spikes and subthreshold dynamics.

**Biophysical model (in this example):**

* Morphologically detailed neuron (multiple compartments).
* Each compartment follows Hodgkin–Huxley–type equations.
* Trainable parameters include ion channel conductances and other membrane properties. 

**Challenge:**
Naive loss = pointwise voltage difference

* Highly sensitive to millisecond spike misalignment
* Produces unstable gradients

**Solution:**

* Use differentiable alignment-based loss (soft-DTW). 
* Run ~1,000 parallel optimization restarts on GPU. 

**Result:**
Recovered parameter sets reproduce spike timing and waveform shape from experimental recordings. 

<!-- 
NOTES: need some diagrams, math, pictures, or plots to illustrate. Possible ideas:
1. Simple cartoon of patch clamp (pipette inside neuron → voltage trace).
2. Compartmental model diagram (soma + dendrites with channel icons).
3. Misaligned spikes vs aligned spikes.
. -->

---


<!-- 
Challenge: spike timing misalignment makes naive pointwise losses brittle.
Solution: use soft-DTW-based loss + large-scale parallel restarts (1,000 runs on GPU) to find good fits.
TODO: be ready to explain optimization restarts
-->

<!-- 
Figure ideas:
1. Target spike vs slightly shifted spike → large error under naive L2.
2. Soft alignment path matching spike peaks → smaller, meaningful loss.
 -->

<!-- Fig. 2 (Part C): scaling to many parameters + identifiability

Demonstration: fit 1,390 parameters (branch-wise conductances) using gradient descent + spatial smoothness regularizer. 

jaxley-paper

Then: gradient-based Hamiltonian Monte Carlo to show parameter uncertainty / degeneracy (some regions well-constrained, others not). 

jaxley-paper

Message: even if the fit is good, parameters may not be uniquely determined.
 -->