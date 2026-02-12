---
# try also 'default' to start simple
theme: seriph
# some information about your slides (markdown enabled)
author: Marco Christiani
title: "Jaxley: A Differentiable Biophysics Simulator"
info: |
  ## Jaxley: A Differentiable Biophysics Simulator
defaults:
  layout: cmu-body
  transition: fade
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
  <div>{{ $slidev.configs.title }}</div>
</template>

<template v-slot:presenter>
{{$frontmatter.author}}
</template>
<template v-slot:presenter-title>
2026-02-12
</template>

**Jaxley: Differentiable Simulation Enables Large-Scale Training of Detailed Biophysical Models of Neural Dynamics**
Deistler, Kadhim, Pals, Beck, Huang, Gloeckler, Lappalainen, Schröder, Berens, Gonçalves & Macke
*Nature Methods*, Volume 22, December 2025


---
transition: fade-out
---

<!-- 
> **Notation conventions used throughout:**
> - Speaker notes are in blockquotes
> - `[FIGURE: ...]` marks where a visual is needed
> - `[TRANSITION: ...]` marks narrative bridges between slides
-->

# Biophysical Neuron Models: What Are We Fitting?

<!-- [FIGURE: cartoon of reconstructed L5 pyramidal cell with colored regions (soma, basal dendrites, apical dendrite, axon), annotated with channel types] -->

**Free parameters** (generally not directly measurable):

- **Maximal conductances** $(\bar{g})$: how much current a channel type passes when fully open
- **Synaptic conductances**: connection strength between neurons
- **Morphological parameters**: radius, length, axial resistivity $r_a$

| Example in paper | What's being fit | Free parameters |
|---|---|---|
| Single neuron (synthetic) | Channel conductances across regions | 19 |
| Conductance profiles | Per-branch $\bar{g}$ along dendritic tree | 1,390 |
| Hybrid retina model | Synaptic + cellular parameters | 556 |
| Biophysical RNN | Synaptic weights + input weights | 109-542 |
| MNIST network | Channel conductances + synaptic weights | ~106,000 |

<!--
***Biophysical neuron models reconstruct a neuron's morphology from microscopy, divide it into **compartments**, each governed by coupled ODEs for membrane voltage and ion channel dynamics.***

- These are the "knobs" of the model. We know the equations (HH-type), but not the knob settings for any particular neuron.
- $\bar{g}$ controls whether a compartment spikes, oscillates, or stays quiet. Each channel type in each region has its own $\bar{g}$.
- $r_a$: higher means more electrical isolation between compartments
- The table is the scaling story of the paper: 19 -> 106,000
-->

---

# The Fitting Problem
<nbsp />
We want parameters $\theta$ such that simulated output $\hat{x}(\theta)$ matches observed data $x^*$:

$$\theta^* = \arg\min_\theta \; \mathcal{L}\bigl(\hat{x}(\theta),\; x^*\bigr)$$

Each evaluation of $\hat{x}(\theta)$ requires **solving a system of ODEs**.  Existing simulators are a black box - no gradients flow backward:

$$\theta \;\longrightarrow\; \boxed{\text{ODE solver}} \;\longrightarrow\; \hat{x}(\theta)$$

| Method | Cost per gradient | At $p = 100{,}000$ |
|---|---|---|
| Finite differences | $(p + 1) \times$ forward sim | ~100,001 simulations |
| Backpropagation | ~1 forward + 1 backward | ~4-21x forward sim |

<!--
**Finite differences** cost $p + 1$ simulations per gradient. **Backprop** costs ~1 fwd + 1 bwd, irr of $p$.
-  $\frac{\partial \mathcal{L}}{\partial \theta_i} \approx \frac{\mathcal{L}(\theta + \epsilon e_i) - \mathcal{L}(\theta)}{\epsilon}$
- Backprop cost is 3-20x forward sim depending on settings, but independent of parameter count
- Example: 2,000-neuron network, 3.2M parameters - finite differences >2 years, backprop 144 seconds
- Key takeaway: if we can differentiate through the ODE solver, we unlock backprop. That's what Jaxley does.
-->

---

# Jaxley: A Differentiable Biophysics Simulator

## The training loop

$$\theta_{t+1} = \theta_t - \alpha \cdot \text{update}\bigl(\nabla_\theta \mathcal{L}\bigr)$$

where $\nabla_\theta \mathcal{L}$ is computed by **backpropagating through the ODE solver**.

<!-- Forward path -->
$$\theta \;\xrightarrow{\text{simulate}}\; \boxed{\text{ODE Solver}} \;\longrightarrow\; \hat{x}(\theta) \;\longrightarrow\; \mathcal{L}\bigl(\hat{x}(\theta),\; x^*\bigr)$$

<!-- Backward path -->
$$\mathcal{L} \;\xrightarrow{\text{backprop}}\; \nabla_\theta \mathcal{L} \;\xrightarrow{\text{update}}\; \theta_{t+1} = \theta_t - \alpha \cdot \text{step}(\nabla_\theta \mathcal{L})$$

<center><em>Backward pass enabled by JAX autodiff through the ODE solver</em></center>

<!-- $$\theta \;\xrightarrow{\text{simulate}}\; \boxed{\text{ODE Solver}} \;\longrightarrow\; \hat{x}(\theta) \;\longrightarrow\; \boxed{\mathcal{L}\bigl(\hat{x},\, x^*\bigr)} \;\xrightarrow{\text{backprop}}\; \nabla_\theta \mathcal{L} \;\longrightarrow\; \theta'$$ -->

<!-- **Differentiable solvers** implemented in JAX: implicit Euler for voltage, exponential Euler for gating variables. -->

---



## Visual Overview

<figure>
  <img src="/assets/fig1.png" class="px-8 pt-5 pb-1" caption="fig1" />
  <figcaption>Figure 1. (a-c) design goals of Jaxley, (d) reconstruction of a CA1 neuron and responses to a step current, (e) simulation time for CA1 and point neurons, (f) biophysically detailed network built with reconstructions of CA1 neurons.</figcaption>
</figure>

<!-- 
a, Schematic of goal: training biophysically detailed neural systems. 
b, Schematic of method: our simulator, Jaxley, can simulate biophysically detailed neural systems, and it can also perform backprop. 
c, Jaxley can parallelize simulations on (multiple) GPUs/TPUs, and it can just-in-time (JIT) compile code. 
d, Reconstruction of a CA1 neuron and responses to a step current obtained with the Neuron simulator and with Jaxley. Inset is a zoom-in view of the peak of the action potential. Scale bars, 3 ms and 30 mV. 
e, Left: time to run 10,000 simulations with Neuron on a CPU and with Jaxley on a GPU. Right: Simulation time (top) for the CA1 neuron shown in d and for a point neuron, as a function of the number of simulations. Bottom: same as top, for computing the gradient with backprop. f, Biophysically detailed network built from reconstructions of CA1 neurons (left) and its neural activity in response to step currents to the first layer (right). Runtimes were evaluated on an A100 GPU. M, million; ML, machine learning; Sim., simulation.
-->


---
layout: default
---

# Agenda

<Toc columns=2 />


---

# Addressing instability of biophysical model training
<nbsp />
<!-- These are not standard off-the-shelf - the authors developed or adapted them for the specific challenges of biophysical model training. -->

<v-click>

**1. Inverse sigmoid:** maps any bounded interval to $(-\infty, +\infty)$ and normalizes parameter scales ($l, u$ bounds).
$$T(\theta) = -\log\!\left(\frac{1}{(\theta - l)\,/\,(u - l)} - 1\right)$$
<!-- where $l, u$ are the lower and upper bounds. -->
</v-click>

<!-- [FIGURE: two small histograms side by side -- "Before transformation" showing parameters clustered at different scales (e.g., $r_a \in [100, 1000]$ vs $\bar{g}_{\text{Na}} \in [0, 0.1]$) and "After transformation" showing both centered and spread similarly around 0. Reproduce the idea from Extended Data Fig. 1a.] -->
<v-click>

**2. Polyak-style gradient descent**

$$\text{step} = \gamma \cdot \frac{\nabla \mathcal{L}}{\|\nabla \mathcal{L}\|^\beta}\text{ with }\beta \in [0.8, 0.99]$$
</v-click>

<v-click>

**3. Multilevel checkpointing**

Backpropagation through a long ODE solve requires storing all intermediate states (e.g., voltages and gating variables at every timestep).

Jaxley supports selective recomputation of intermediate states during the backward pass, trading compute time for memory.

</v-click>

<!-- 
[click]
Parameter transformations address both boundedness and scale mismatch.
- biophysical parameters are bounded (e.g., $\bar{g}_{\text{Na}} \in [0.05, 0.5]$ S/cm²)
- but gradient descent operates best in unconstrained space. 

[click]
- Loss landscape of biophysical models is highly non-convex and gradients can vary wildly between steps
SGD stalls or overshoots for some biophysical loss surfaces which have plateaus & ridges
- $\beta$ exponent prevents any single gradient component from dominating the update.
- **adaptive annealing:** in some applications, can be multiplied by $\mathcal{L}$ for automatically reducing the step:
$$\text{step} = \gamma \cdot \frac{\mathcal{L} \cdot \nabla \mathcal{L}}{\|\nabla \mathcal{L}\|^\beta}$$
-->

---
layout: two-cols-header
---

<style>
.two-cols-header {
    grid-template-columns: 2fr 1fr !important;
}
</style>

# Validation: Accuracy and Scalability

Jaxley matches NEURON at sub-ms, sub-mV resolution on morphologically detailed neurons.

<!-- [FIGURE: Fig. 1d -- overlaid NEURON and Jaxley traces with inset at action potential peak] -->

- **GPU speedup:** ~2 orders of magnitude for parallel workloads
- **Gradient cost:** 3--20x forward simulation (but independent of parameter count)

<br>
<br>
::left::

2,000 neurons, 1M synapses, 3.92M ODE states

| Operation | Time (single A100 GPU) |
|---|---|
| Forward simulation (200 ms) | 21 seconds |
| Backprop w.r.t. 3.2M parameters | 144 seconds |
| Finite differences (estimated) | **>2 years** |

::right::

<figure>
  <img src="/assets/fig1d.png" class="px-5 pt-5 pb-1" caption="fig1d" />
  <figcaption>Figure 1d. Reconstruction of a CA1 neuron and responses to a step current</figcaption>
</figure>


<!--
- Accuracy validated on CA1 pyramidal cell and 4 layer 5 neurons from Allen Cell Types Database
- Extended Data Fig. 2 shows spike time and amplitude correlation across morphologies
- GPU speedup comes from parallelizing across stimuli, parameter sets, or compartments
- 8,000 time steps at dt=0.025ms for the 200ms simulation
- Checkpointing mitigates memory cost of storing intermediate states for backprop
-->

---
routeAlias: fig1-slide
---

# Example 1: Fitting a Single Neuron (Synthetic Data)
<nbsp />

**Model:** L5 pyramidal cell -- reconstructed morphology, 9 ion channel types, **19 free parameters.**

**Data:** Synthetic somatic voltage from known ground-truth parameters + step current.

<!-- [FIGURE: Fig. 2a morphology + Fig. 2b voltage traces -- ground truth (black), GD fits (blue), with summary statistic windows] -->

**Constraint:** Spike count is discrete (zero gradient).

Use differentiable surrogates -- mean and s.d. of voltage in two time windows:

$$\mathcal{L}(\theta) = \text{MAE}\!\left(\frac{\mu_{\text{sim}}}{8.0},\; \frac{\mu_{\text{data}}}{8.0}\right) + \text{MAE}\!\left(\frac{\sigma_{\text{sim}}}{4.0},\; \frac{\sigma_{\text{data}}}{4.0}\right)$$

**Result:** GD converges in **9 steps** (median), **~10x fewer simulations** than genetic algorithm.

<!--
Layer 5 Pyramidal Cells are the primary output neurons of the cerebral cortex, responsible for transmitting information from the neocortex to various subcortical regions, including the striatum, thalamus, and spinal cord.

- L5PC: large cortical neuron -- soma, basal dendrites, long apical dendrite, axon
- 9 channels: 2 sodium (fast spike upstroke), 5 potassium (repolarization, adaptation), 2 calcium, plus leak
- Division by 8.0 and 4.0 standardizes different statistic types to similar scales
- GA (IBEA) uses 10 simulations per iteration; GD uses 1 sim + 1 backprop -> ~10x fewer sims
- Even at 19 params, GD is already more efficient. Advantage grows with parameter count.
- Loss design is a real constraint -- rules out many standard electrophysiology summary statistics
-->

---
routeAlias: fig2-slide
---

## Example 1: Figures

<nbsp/>
<br />
<center>
<figure>
  <img src="/assets/fig2.png" class="w-150" caption="fig2" />
  <figcaption>
  Fig. 2: Inferring single-neuron models with gradient descent.
   (a) L5PC morphology. (b) Synthetic voltage (black) and gradient descent fits (blue). (c) Loss: GD (blue) vs GA (black). (d) Fits to Allen Cell Types patch-clamp recordings. (e-i) Conductance profile recovery (1,390 params) with posterior uncertainty. (j-m) Nonlinear dendritic computation task.</figcaption>

</figure>
</center>
<!-- [FIGURE: Fig. 2c -- loss curves, GD (blue) vs GA (black)] -->

<!-- 
**Takeaway: a single biophysical neuron, with the right channel densities and morphological parameters, can implement a computation that a single linear unit cannot. And gradient descent can find those parameters automatically.**

- b: top shows summary statistic windows on voltage trace. Best fit dark blue, independent runs light blue. Scale bars 20ms, 30mV.
- c: individual GD runs (light blue), their minimum (dark blue), vs minimum across 10 GA runs (black).
- d: morphologies + recordings from Allen Cell Types DB, step current responses. Scale bars 200ms, 30mV. More in Extended Data Fig. 5.
- e: synthetic conductance profile along L5PC morphology.
- f: simulated voltages at 1.5ms and 2.5ms given ground-truth profile.
- g: predicted voltages from GD fit.
- h: ground-truth profile (black) vs 90% CI from gradient-based HMC (blue).
- i: loss curves, GD vs GA.
- j: nonlinearly separable input amplitudes (left), simplified 12-compartment morphology (right).
- k: voltage traces of learned model.
- l: decision surface showing nonlinear single-neuron computation.
- m: minimum loss across 10 runs, GD vs GA.

**Panel j (task definition):** two axes $x_1$ and $x_2$ represent amplitude of step current injected into dendrite 1 / 2. colored dots are the training examples:

- **Blue dots** (labeled -70 mV): both dendrites receive intermediate stimulation. The target is that the soma should stay at resting potential (not spike).
- **Yellow dots** (labeled 35 mV): one dendrite receives strong stimulation and the other receives weak (or vice versa). The target is that the soma should depolarize / spike.

The right side of panel j shows the morphology: a soma (the fork in the middle) with two dendrites, one receiving $x_1$ and one receiving $x_2$. The somatic voltage is recorded.

**Panel k - what the trained neuron does:** volage traces at soma for diff inputs. The yellow trace spikes (one dendrite strong, other weak - correctly classified as 35 mV class). The blue trace stays near -80 mV (both dendrites intermediate -correctly classified as -70 mV class). The neuron learned to only fire when the inputs are asymmetric.

**Panel l - the decision surface:** They swept $x_1$ and $x_2$ and recorded somatic voltage (color).
- yellow/green regions = where neuron spikes (high voltage), dark purple regions = where it stays quiet (low voltage). 
- The shape is clearly nonlinear - there's no straight line dividing the spiking from non-spiking regions. 
- The neuron uses its dendritic nonlinearities (ion channels, morphology) to implement what is effectively a nonlinear classifier.

**Panel m - training speed comparison:** Gradient descent finds lower-loss solutions faster, same story as the other experiments.

-->


---

# Example 2: Fitting Real Patch-Clamp Recordings

## The spike alignment problem
<br>

- Real neurons fire at slightly variable times
- Small timing shifts → large pointwise errors → misleading gradients

*A 1 ms shift of a 100 mV spike leads to errors of order $10^4\;\text{mV}^2$ under L2* (<Link to="l2-spike-long" title="details" />)

<!-- [FIGURE: cartoon - offset spike trains. Panel A: large L2 error. Panel B: DTW aligns, small error.] -->

<v-click>
<Link to="dtw-long" title="Dynamic time warping (DTW)"/> aligns two time series before measuring distance &mdash; but the discrete min over paths is not differentiable.
</v-click>
<br/>
<v-click>

<Link to="soft-dtw-long" title="Soft-DTW"/> relaxes min to soft-min (log-sum-exp), with cost:

$$c(x_i, \hat{x}_j) = |x_i - \hat{x}_j| + |i - j|$$

$|i-j|$ penalizes excessive temporal warping.

</v-click>

<v-click>

**Experiment/Results:**
 - 4 morphologies, 25 trainable parameters per cell.
 - **1,000 parallel GD runs on GPU**, fits reproduce firing rate, spike shape, adaptation.
</v-click>

<!-- [FIGURE: Fig. 2d - morphologies with overlaid recordings (black) and fits (blue)] -->

<!--
- 25 = 19 original + 6 for experimental variability: Ca channel time constants (5x), Na activation shift (10mV), K reversal [-100,-70]mV, Na reversal [40,60]mV
- soft-DTW: gamma→0 recovers standard DTW; gamma>0 gives smooth differentiable loss
- Two-stage: fit first 200ms, then refine on full 1,150ms trace
- Final selection uses 5 non-differentiable features (spike count, amplitude/timing of first 2 spikes) — for selection only, not gradient
- 1,000 restarts is honest about non-convexity; GPU parallelization makes it practical
- Competitive with GA at same compute budget (1,000 parallel × 50 iterations)
-->

---

# Scaling Parameters and Degeneracy
1,390 branch-wise conductances

Same L5PC, but now a **separate $\bar{g}$ per branch** -- models continuous variation of channel density along the dendrite. Smoothness prior:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{data}} + \lambda \sum_{b=1}^{B} \bigl(\bar{g}_b - \bar{g}_{\text{parent}(b)}\bigr)^2$$

<!-- [FIGURE: Fig. 2i -- loss curves, GD vs GA] -->

<v-click>

**Result:** GD converges in ~100 iterations. GA has **100x higher loss** after 500 iterations.

## A good fit $\neq$ unique parameters

Gradient-based **Hamiltonian Monte Carlo** samples the posterior over all 1,390 parameters:
- Some conductances **tightly constrained** (e.g., $\bar{g}_{\text{NaT}}$ apical, ~400 μm from soma)
- Others **weakly constrained** -- data is consistent with a wide range

</v-click>

<!-- [FIGURE: Fig. 2h -- ground truth (black) with 90% posterior CI (blue) for NaT and KTst] -->

<!--
In slide 5, the L5PC model had 19 parameters -- g per channel type per region. (e.g., one value for "sodium conductance in the soma," one for "potassium conductance in the apical dendrite," etc.). 
This means every branch in the apical dendrite shares the same sodium conductance. (Roughly, as in real neurons, channel density varies along the dendritic tree)
In this experiment, they make a separate g parameter for every individual branch in the morphological tree, for every channel type.
- The apical dendrite has 3 channel types and many branches, the axon has 7 channel types and many branches, totaling 1,390 individual parameters.
- Now the model can capture the fact that sodium conductance might be high near the soma and low far away, or vice versa.

- "parent(b)" = the branch that b connects to, closer to the soma. Penalty = squared difference in conductance between adjacent branches.
- lambda=0.001 -- weak regularization, just enough to encourage smoothness
- Ground truth: conductance profiles sampled from Gaussian process as function of distance from soma
- 10 channel types across apical dendrite and axon → 1,390 params
- Data: voltage at every branch from 5ms step current (full dendritic voltage imaging)
- Regularizer: lambda=0.001, encourages neighboring branches to have similar conductances -- biologically motivated

Gradient-based Bayesian inference reveals **which parameters the data actually constrains**:

> A single best-fit can mislead. Understanding *what the data can tell you* requires examining the full posterior.

- Bayesian inference done via Hamiltonian Monte Carlo (HMC) -- an MCMC method that uses gradients to eff explore high-dim param spaces
- HMC: 200 chains, 500 iterations each, parallelized on A100 GPU using BlackJAX library
- HMC is itself enabled by Jaxley's gradients -- you couldn't do this with NEURON
- Degeneracy is a fundamental property of these systems (Prinz et al 2004), not a failure of the method
- HMC simulates Hamiltonian dynamics in parameter space, using the gradient of the log-posterior as a "force." This lets it make large, informed moves rather than small random ones, which is critical in 1,390 dimensions.
-->

---

# Beyond Fitting: Task-Driven Biophysical Models
<nbsp />
So far: given data, find parameters. Now: given a **task**, find parameters that make a biophysical network **perform a computation**.


<v-click>

### A. Nonlinear dendritic computation

Single neuron, soma + two dendrites, 72 parameters. Learns XOR-like pattern separation: spike only when one dendrite is driven strongly and the other weakly. (<Link to="fig2-slide" title="more" />)
<!-- [FIGURE: Fig. 2j input classes + Fig. 2l decision surface] -->

</v-click>
<v-click>

### B. Biophysical RNNs for working memory

20-50 HH-type neurons with dendrites and conductance-based synapses.
cs
- **Evidence integration:** noisy input over 500 ms (20,000 steps) → classify sign → **99.9% accuracy**
- **Delayed match-to-sample:** remember stimulus across ~500 ms delay → curriculum learning

</v-click>

<v-click>

### C. MNIST with biophysical neurons

784 input → 64 morphologically detailed hidden (CA1 reconstructions) → 10 output. **~106k parameters**, no artificial nonlinearities.

- **94.2% test accuracy** (above linear, below MLP)
- Adversarial robustness **comparable to MLP** -- contradicts prior claims

</v-click>

<!--
[click]
Same loop (simulate → loss → backprop → update), but loss is task performance
- A: demonstrates single-neuron dendritic nonlinearity is trainable end-to-end. Hypothesis from theoretical neuroscience (Poirazi et al 2003) now directly optimizable.

[click]
- B: previous task-trained RNNs used rate-based or simplified spiking neurons. Jaxley enables full biophysical detail → can study channel-level contributions to cognition.
- B evidence integration: generalizes to longer durations, produces sigmoidal psychometric curve. 109 trainable params (input, recurrent, readout weights).
- B delayed match-to-sample: 542 params, 50 recurrent neurons, curriculum learning increases delay from U[50,150] to U[450,550] ms. Network uses transient coding.

[click]
- C: 55k channel conductances + 51k synaptic weights. Simulated 10ms per image. Hidden neurons develop digit-selective tuning (Extended Data Fig. 9).
- C adversarial: used gradient descent on input to find minimal perturbation changing classification. Biophysical net similarly vulnerable -- contradicts Zhang et al 2023.
- Adversarial result is a genuine scientific finding enabled by gradient access, not just a capability demo.
-->

---

# Hybrid Retina Model

When Does Biophysical Detail Help?

**Data:** Two-photon calcium imaging of a retinal ganglion cell. ~15,000 stimulus--response pairs
**Model:** Hybrid -- statistical front-end (photoreceptors + bipolar cells) feeds into a **biophysical RGC** (6 ion channels, reconstructed morphology). **556 trainable parameters.**

<!-- [FIGURE: Fig. 3a schematic -- Stimulus → PRs → BCs → biophysical RGC → calcium output. Keep simple.] -->

### Key finding: inductive bias

| | Large dataset | Small dataset |
|---|---|---|
| MLP | Higher train correlation | Overfits -- poor test |
| Hybrid | Lower train correlation | Better test generalization |

Mechanistic structure acts as a **regularizer** -- constrains outputs to be biophysically plausible.

Bonus: trained model reproduces **compartmentalized calcium responses** (local stimulation doesn't propagate through entire tree) — not explicitly trained for, emerges from structure.

<!--
- Hybrid = statistical components for known early processing + mechanistic RGC for the part we want to understand
- Statistical: photoreceptors = Gaussian spatial filter (σ=50μm), bipolar cells = point neurons with measured nonlinearity on hexagonal grid (40μm spacing)
- 556 params: 287 synaptic conductances + 12 channel conductances (6 soma + 6 dendrite) + 147 branch radii + 147 axial resistivities
 - (checkerboard noise → dendritic calcium at 232 sites
- Calcium readout: intracellular Ca from model's calcium channel, convolved with double-exponential kernel (rise 5ms, decay 100ms) to model calcium indicator dynamics
- Test correlation: avg 0.25, max 0.51 across 146/147 positive recording sites
- Fig 3f shows the crossover: hybrid wins on test when training data < ~256 points
- Compartmentalized response matches Ran et al 2020 experimental observations
- ML analogy: biophysical structure is like conv structure for vision — constrains the hypothesis space in a domain-appropriate way
- Trained with truncated BPTT (gradient reset every 50ms) to handle vanishing/exploding gradients

**Let's step back and consider what assumptions underlie everything we've seen**
-->

---

# Assumptions and Limitations

<style>
  th {
    font-size: 1.1em;
  }
  strong {
    font-size: 1.1em;
  }
  tr {
    font-size: 0.6em;
  }
  td {
    padding-top: 0.5em;
    padding-bottom: 0.5em;
  }
</style>


| Category | Assumption | Why needed | Or else | Paper's mitigation |
|---|---|---|---|---|
| **Mathematical** | Loss function must be differentiable | Gradient signal for backprop | Gradients are zero or undefined (e.g., spike count) | Differentiable surrogates: voltage statistics, soft-DTW |
| | ODE solver must be accurate enough | Gradients reflect biology, not solver artifacts | Fitting to numerical errors, misleading parameter estimates | Validated against NEURON at sub-ms/sub-mV |
| | Parameters must be bounded and scaled | Stable optimization | Divergence, one parameter type dominates updates | Inverse sigmoid transformation |
| **Optimization** | Loss landscape is non-convex | Multiple local minima exist | Single runs may find poor solutions | Parallel restarts (up to 1,000 on GPU), Polyak SGD |
| | Backprop memory is manageable | Must store or recompute intermediate states | Cannot train long simulations or large networks | Multilevel checkpointing |
| | Long time horizons cause gradient pathology | Vanishing/exploding gradients through many time steps | Cannot train on behavioral timescales (seconds) | Truncated BPTT (used in retina model), acknowledged as open challenge |
| **Interpretive** | Parameter degeneracy | Many parameter sets produce similar outputs | Over-interpreting specific fitted values | Bayesian inference via HMC; ensemble methods |
| | Mechanistic inductive bias is appropriate | Biophysical structure constrains the model | If structure is wrong, model underfits or misleads | Validated on retina: helps in low-data regime |


<!--
walk through one example per category.i
Mathematical: "spike count isn't differentiable, so they had to design surrogate losses."
Optimization: "1,000 parallel restarts is an honest acknowledgment of non-convexity."
Interpretive: "a good fit doesn't mean the parameters are correct -- that's why they ran HMC."
The timescale mismatch is the biggest open challenge: biophysics operates at sub-millisecond resolution, but cognitive tasks operate over seconds. Backpropagating through millions of time steps is where this framework hits its limits. 

**What else can we do with Jaxley?**
-->

<!-- # Applications: Neurostimulation and Experiment Design

## The bridge

The paper optimizes **parameters** given fixed inputs (stimuli). But differentiable simulation also enables optimizing **inputs** given fixed (or fitted) parameters:

$\nabla_{\text{stimulus}} \mathcal{L}(\text{output}) \quad \text{is computable with the same machinery}$

The paper explicitly identifies future applications: "maximally excitable stimuli" and "optimally discriminative experiments."

## Three concrete application directions

**1. Patient-specific stimulation design**

- Fit a biophysical model to a patient's recordings (as demonstrated in the paper)
- Define an objective over the fitted model (e.g., activate target neurons, minimize off-target activation, minimize energy)
- Optimize stimulation waveform parameters via gradient descent on the fitted model

**2. Gradient-based waveform optimization**

- Objective examples: selective fiber recruitment in peripheral nerve stimulation, minimizing charge delivery for a given activation threshold, shaping temporal patterns of activation
- Jaxley provides the differentiable backbone; the extension needed is coupling an **extracellular field model** to the compartmental neuron model

**3. Experiment design to resolve parameter degeneracy**

- The HMC posterior (slide 7) reveals which parameters are well-constrained and which are not
- Choose the next stimulation protocol to **maximally reduce posterior uncertainty**
- This is Bayesian optimal experiment design, and it requires gradients through both the model and the posterior — exactly what Jaxley provides

## Limitations to state clearly

- Real neurostimulation requires extracellular field coupling (volume conduction), which is not yet in Jaxley
- Long-horizon optimization (chronic stimulation protocols) faces the same timescale challenge discussed earlier
- Non-convexity means optimized waveforms should be validated, not blindly trusted -->

<!-- > **Speaker notes:** The paper doesn't do stimulation but I'm extrapolating from the framework's capabilities. The key idea is that differentiable simulation is a general tool: anything that can be framed as "optimize X subject to a simulated biophysical system" benefits from gradients. The extracellular field coupling limitation is real and worth flagging — it's an engineering extension, not a fundamental barrier, but it's not trivial. -->


---

# Closed-Loop Stimulation via Differentiable Simulation
Extending the paper's evidence-integration RNN

Take the trained biophysical RNN -- 20 conductance-based biophysical neurons (multi-channel ion dynamics, conductance-based synapses) + 2 readout cells. **Freeze all network parameters.**

Train a small **stimulation policy** $\pi_\phi$: at each timestep, observes readout voltages + normalized time, outputs a scalar gain $g_t$ that scales the stimulus injected in the input compartment (basal branch).

$$I_i(t) \propto g_t \cdot s(t) \cdot w_i, \quad g_t = \pi_\phi(v_{\text{readout}}(t),\; t/T) $$

where $s(t)$ is the evidence waveform and $w_i$ are fixed per-cell input weights.

**Objective:** task performance + stimulation efficiency

<!-- $$\mathcal{L} = \mathcal{L}_{\text{CE}}(\text{readout},\; \text{label}) + \lambda \sum_t g_t^2$$ -->
$$
\mathcal{L}=\mathcal{L}_{CE}+\lambda_g\sum_t g_t^2+\lambda_I\sum_t \Big(\tfrac{1}{N}\sum_i I_i(t)^2\Big)
$$

Trained end-to-end with BPTT through the full biophysical simulation.

<!--
- This is our extension, not in the original paper. We reproduced their evidence-integration codepath end-to-end first.
- The recurrent units are NOT simple single-compartment HH -- they're multi-channel biophysical cells with apical/basal dendrites and conductance-based synapses.
- Policy: observes 2 readout voltages + normalized time → scalar gain. Very few parameters.
- The reported policy was trained with --cost gain --lambda-u 0.1 (gain energy penalty). We also trained with --cost current --lambda-u 5000 and got similar behavior.
- Table reports mean injected-current power at eval time (measured quantity), even though training penalized gain magnitude. Both decrease together since I ∝ g.
- $i$ corresponds to cell $i$ (currently we dont have policy weights per cell, just a scalar)
- "Model-based deterministic policy optimization" -- differentiable simulator IS the environment model.
- 100% on 200 trials consistent with authors' 0.999 accuracy under same trial generator.
- Key advantage over RL: exact, low-variance gradients. No REINFORCE needed.
- Limitation: 500ms horizon. Longer protocols face same timescale challenges from paper's discussion.
- Extensions: multi-electrode policies, state-dependent waveform shaping, uncertainty-aware control.

- Policy model - tiny 2-layer MLP mapping 3 inputs → 1 gain.
  - input x_t = [v_readout0(t), v_readout1(t), t/T] (3 scalars)
  - hidden: 16 tanh units
  - output: 1 scalar logit
  - gain: g_t = sigmoid(logit) * g_max
-->

---

# Closed-Loop Stimulation via Differentiable Simulation

Results
<center>
<figure>
  <img src="/assets/my_policy_fig.png" class="w-110 pt-0 pb-1" caption="custom policy" />
  <figcaption>
  Two example trials under the learned policy. Top: noisy evidence stimulus 
(negative mean = label 0, positive = label 1). Middle: policy gain gt learned 
to keep stimulation low (~0.1-0.25 vs baseline 1.0). Bottom: readout neuron 
voltages separate correctly by the response window (gray).
  </figcaption>
</figure>

</center>

<style>
  th {
    font-weight: 600;
    font-size: 1.0em;
    padding-top: 0.2em !important;
    padding-bottom: 0.2em !important;
  }
  tr {
    font-size: 0.6em;
  }
  td {
    padding-top: 0.5em !important;
    padding-bottom: 0.5em !important;
  }
</style>

<div class="mx-auto w-65% mt-2">

| | Accuracy | Mean current power |
|---|---|---|
| Fixed baseline ($g=1$) | 99.9% | $1.57 \times 10^{-5}$ |
| Learned policy | **100%** (200 trials) | $4.83 \times 10^{-7}$ (**~30× reduction**) |
</div>

<!-- *Task performance preserved while substantially reducing stimulation effort.* -->


<!--
- This is our extension, not in the original paper. We reproduced their evidence-integration codepath end-to-end first.
- The recurrent units are NOT simple single-compartment HH - they're multi-channel biophysical cells with apical/basal dendrites and conductance-based synapses.
- Policy: observes 2 readout voltages + normalized time → scalar gain. Very few parameters.
- The reported policy was trained with --cost gain --lambda-u 0.1 (gain energy penalty). We also trained with --cost current --lambda-u 5000 and got similar behavior.
- Table reports mean injected-current power at eval time (measured quantity), even though training penalized gain magnitude. Both decrease together since I ∝ g.
- "Model-based deterministic policy optimization" - differentiable simulator IS the environment model.
- 100% on 200 trials consistent with authors' 0.999 accuracy under same trial generator.
- Key advantage over RL: exact, low-variance gradients. No REINFORCE needed.
- Limitation: 500ms horizon. Longer protocols face same timescale challenges from paper's discussion.
- Extensions: multi-electrode policies, state-dependent waveform shaping, uncertainty-aware control.
-->


---
layout: section
---

# How Jaxley Works: Autodiff and Compilation in JAX

<!-- JAX (XLA) provides both **reverse-mode** (VJP) and **forward-mode** (JVP) automatic differentiation, and does so in a clever way. -->

---

# Vector-Jacobian Products
<nbsp />
The full computation is a chain:

$$\theta \;\xrightarrow{\;f\;}\; \hat{x}(\theta) \;\xrightarrow{\;\mathcal{L}\;}\; \text{scalar}$$

By the chain rule:

$$\nabla_\theta \mathcal{L} = J_f^\top \; \nabla_{\hat{x}} \mathcal{L}$$

The VJP computes $v^\top J$ for a given $v \in \mathbb{R}^m$ — **without forming $J$**.

Setting $v = \nabla_{\hat{x}} \mathcal{L}$ gives the full gradient $\nabla_\theta \mathcal{L} \in \mathbb{R}^n$ in one backward pass, regardless of $n$.

- **Cost:** $O(1)$ backward passes for the full gradient
- **Memory:** must store intermediate states (the "tape") — hence checkpointing

<v-click>
<center><em>This is reverse-mode autodiff.</em></center>
</v-click>

<!--
- $J_f$ is Jacobian of simulator (m outputs x n parameters) -- big, never materialized
- $\nabla_{\hat x} L$ is cheap to compute (gradient of loss w.r.t. its input, e.g. just the residual for MSE)
- The VJP propagates this vector backward through each layer of the computation without forming $J$
- For Jaxley: $f$ is the ODE solver, $\theta$ includes all conductances/synaptic weights, $\hat x$ is the voltage trace
- Cost is O(1) in n because you're doing one backward pass regardless of how many parameters exist
- Memory: for an ODE solve with T timesteps, naive backprop stores all T intermediate states. Checkpointing trades recomputation for memory.
-->

---

# Jacobian-Vector Products
<nbsp />

Given a function $f: \mathbb{R}^n \to \mathbb{R}^m$ with Jacobian $J \in \mathbb{R}^{m \times n}$, the JVP computes:

$$J v \text{ for a given vector } v \in \mathbb{R}^n$$

This propagates a **tangent vector** (directional derivative) forward alongside the primal computation.

- **Cost:** $O(1)$ per tangent direction, but need $n$ passes for full Jacobian
- **Memory:** no tape needed — only current state plus tangent
- **When it wins over VJP:** few input directions, many outputs, or when you need $Jv$ directly

<v-click>

<center><em>This is forward-mode autodiff</em></center>

</v-click>

<v-click>

> **In the paper:** Lyapunov exponents (Fig. 4c) require iterating $q_{t+1} = \frac{Df|_{x_t} \, q_t}{\|Df|_{x_t} \, q_t\|}$ — a JVP at every timestep. Forward mode computes this naturally without storing the full trajectory.

</v-click>

<!--
- VJP (previous slide): efficient when few outputs, many params → training
- JVP: efficient when few input directions, many outputs → analysis
- Lyapunov exponent measures sensitivity to initial conditions (positive = chaotic, negative = stable)
- The algorithm: propagate a perturbation vector forward, renormalize at each step, measure growth rate
- $Df|_{x_t}$ is the Jacobian of one solver step evaluated at state $x_t$
- JAX makes this trivial: `jax.jvp(step_fn, (x_t,), (q_t,))` gives both f$(x_t)$ and $Df·q_t$ in one call
- You could also compute Lyapunov exponents with VJP but you'd need to store the full forward trajectory — JVP avoids this entirely
- This is an example of differentiable simulation enabling analysis, not just training
-->

---

# XLA compilation and structured control flow
<nbsp />
JAX's `jit` system compiles Python functions to optimized XLA (Accelerated Linear Algebra) kernels.

- For Jaxley, this means the entire ODE solver can be lowered to GPU- and TPU-native code.
  - I.e., tridiagonal solve for implicit Euler at every time step

**Structured control flow:**
- The ODE solver must iterate sequentially through thousands of time steps. A naive loop would:
  - prevent compilation (separate kernel launches)
  - break the computation graph (often cannot autodiff a loop)

<!--
This is why Jaxley can JIT-compile the entire simulation + backprop pipeline -- there are no Python-level loops to break the trace.
VJP is efficient when you have many parameters and one scalar output (training) -- backprop.
JVP is efficient when you have few input directions and many outputs (analysis) -- Lyapunov exponents, sensitivity analysis, and optimal experiment design.
JAX gives you both through the same interface, which is why Jaxley can serve both training and analysis use cases.
The `scan` point is important for anyone who's tried to write differentiable ODE solvers in PyTorch — dynamic control flow makes this much harder there. JAX's functional design and XLA compilation make the ODE solver a first-class differentiable program.
-->

---

# XLA compilation and structured control flow
<nbsp />

**Scans**
- `jax.lax.scan` replaces the loop with a **compiled sequential scan**
  - executes as a single fused device op, preserves the graph for autodiff, enables checkpointing, and more

```
# representative structure
def step_fn(state, input_t):
    new_state = implicit_euler_step(state, input_t)
    return new_state, new_state.voltage

final_state, voltages = jax.lax.scan(step_fn, init_state, inputs)
```

**Parallelization via `jax.vmap`:**

`vmap` (vectorized map) automatically transforms a function that processes one simulation into a function that processes a **batch** in parallel. Jaxley uses this for:
- **Stimulus parallelization:** run the same model on many different inputs
- **Parameter parallelization:** run many parameter configurations simultaneously (enables the 1,000 parallel restarts)

No code changes required -- `vmap` handles the batching automatically by adding a batch dimension to all arrays.


---

# Summary

Jaxley enables:

1. **Differentiable simulation** of biophysically detailed neuron and network models via JAX autodiff
2. **GPU-scalable training** from single neurons (19 parameters) to networks (106,000 parameters)
3. **Data-driven fitting** to voltage and calcium recordings, competitive with or exceeding genetic algorithms
4. **Task-driven training** of biophysical RNNs for cognitive tasks (working memory, decision-making)
5. **Gradient-enabled analysis** including Bayesian inference, Lyapunov exponents, and adversarial robustness

Key assumptions:

- Loss functions must be differentiable
- Non-convex landscapes require restarts (at least it can be parallel)
<!-- - Parameter degeneracy means fitted values need posterior analysis, not point interpretation -->
<!-- - Timescale mismatch between biophysics (ms) and behavior (s) is representative of the kind of challenge one might fact when using biophysical modelling. -->

Open directions:

<!-- - Extracellular stimulation and field coupling models -->
- Scaling to longer behavioral timescales
- Combining with forward-mode autodiff and evolutionary methods
<!-- - Integration with connectomics and transcriptomics data for cell-type-specific models -->

<!--
 (1) differentiable simulation is a genuine paradigm shift for biophysical modeling, 
(2) it enables things that were previously infeasible (fitting 100k parameters, task-training biophysical networks), and 
(3) it comes with real assumptions and limitations that are important to understand.
-->

---
layout: section
---

# Extra

---
routeAlias: l2-spike-long
---

Voltage goes from roughly -70 mV to +30 mV and back in about 1-2 ms. So the spike amplitude is about 100 mV peak-to-peak.

If the model's spike is shifted by 1 ms relative to the data's spike, then at the time points around the peaks, one trace is at +30 mV and the other is at -70 mV (or vice versa). The pointwise L2 error at those time points:

$$(30 - (-70))^2 = (100)^2 = 10{,}000 \;\text{mV}^2$$

And one timestep later the situation reverses, the data is back down but the model is now at its peak:

$$((-70) - 30)^2 = (-100)^2 = 10{,}000 \;\text{mV}^2$$

So you get two adjacent time points each contributing $\sim 10^4 \;\text{mV}^2$ to the loss, even though the model is producing the right spike shape at essentially the right time -- just offset by one millisecond.

For comparison, if both traces are at resting potential (−70 mV) and differ by 1 mV, the error is $(1)^2 = 1 \;\text{mV}^2$. So a 1 ms timing shift creates an error that's $\sim 10{,}000\times$ larger than a 1 mV amplitude error. 

<!-- This is why pointwise losses produce misleading gradients for spiking data -- the optimizer sees "this is catastrophically wrong" when really it's "this is almost right but slightly early." -->

---
routeAlias: dtw-long
---

## Dynamic time warping (DTW)

DTW finds an optimal **alignment** between two time series before measuring their distance. It allows one series to be locally stretched or compressed to match the other.

Given two sequences $x = (x_1, \ldots, x_N)$ and $\hat{x} = (\hat{x}_1, \ldots, \hat{x}_M)$, DTW finds an alignment path $\pi = \bigl((i_1, j_1), \ldots, (i_K, j_K)\bigr)$ that minimizes:

$$\text{DTW}(x, \hat{x}) = \min_{\pi} \sum_{k=1}^{K} c(x_{i_k},\, \hat{x}_{j_k})$$

subject to monotonicity and boundary constraints on the path.

**Problem:** The $\min$ over discrete paths is **not differentiable**.

---
routeAlias: soft-dtw-long
---

## Soft-DTW: a differentiable relaxation

Replace the hard $\min$ with a soft minimum (log-sum-exp):

$$\text{soft-DTW}_\gamma(x, \hat{x}) = \min_\gamma \sum_{k} c(x_{i_k},\, \hat{x}_{j_k})$$

where $\min_\gamma$ denotes the soft-min operator with smoothing parameter $\gamma$
- As $\gamma \to 0$, this recovers standard DTW.
- For $\gamma > 0$, the loss is smooth and differentiable, providing gradient signal even when spikes are slightly misaligned.

The paper uses the cost function:

$$c(x_i, \hat{x}_j) = |x_i - \hat{x}_j| + |i - j|$$

The second term $|i - j|$ penalizes large temporal warps, preventing the alignment from distorting the trace too much.

---

## B1: Soft-DTW -- Full Recursion

The DTW distance is computed via dynamic programming. Define the cost matrix $C_{ij} = c(x_i, \hat{x}_j)$ and the cumulative distance matrix:

$D_{ij} = C_{ij} + \min\{D_{i-1,j},\; D_{i,j-1},\; D_{i-1,j-1}\}$

Soft-DTW replaces $\min$ with $\text{softmin}_\gamma$:

$D^\gamma_{ij} = C_{ij} + \text{softmin}_\gamma\{D^\gamma_{i-1,j},\; D^\gamma_{i,j-1},\; D^\gamma_{i-1,j-1}\}$

where $\text{softmin}_\gamma(a_1, \ldots, a_k) = -\gamma \log \sum_i e^{-a_i/\gamma}$.

The gradient $\nabla_{\hat{x}} \text{soft-DTW}_\gamma$ flows through this recursion, providing a smooth signal even for temporally misaligned events.


---

## B2: Checkpointing -- Memory vs Compute Tradeoff

Standard backprop through $T$ time steps requires storing $O(T)$ intermediate states.

**Single-level checkpointing:** Store every $k$-th state. During backprop, recompute from the nearest checkpoint. Memory: $O(T/k)$. Extra compute: $O(k)$ per segment.

**Multilevel checkpointing:** Apply recursively -- checkpoint the checkpoints. Achieves $O(\log T)$ memory with $O(\log T)$ overhead per step. For a 200 ms simulation at $\Delta t = 0.025$ ms (8,000 steps), this reduces memory from storing 8,000 states to storing ~13.

---

## B3: Where Gradients Help vs Where They Don't

| Scenario | Backprop (reverse) | Forward-mode | Evolutionary |
|---|---|---|---|
| Many parameters, scalar loss | Best | Expensive | Expensive |
| Few parameters, high-dim output | Expensive (memory) | Best | Moderate |
| Highly non-convex, few params | Good with restarts | Good with restarts | May be competitive |
| Non-differentiable objectives | Cannot use | Cannot use | Works |
| Very long time horizons | Gradient pathology | Same issue | No gradient needed |

The paper's discussion notes that evolutionary algorithms and forward-mode autodiff can sometimes match or beat backprop, and Jaxley supports GPU-accelerated implementations of both.
