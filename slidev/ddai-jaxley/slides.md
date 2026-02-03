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

# This is a body slide

with content

## This is an h2


---
layout: cmu-body
# layout: default
transition: fade-out
---

# Foo

Presentation slides for developers

foo bar baz

# This is an h1
## This is an h2
### This is an h3
#### This is an h4

<p>this is p</p>

- one
- two
  - 2.1
  - 2.2
    - 3.1

<!--
something
-->
