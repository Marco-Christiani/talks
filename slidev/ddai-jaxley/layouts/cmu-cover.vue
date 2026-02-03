<template>
  <div class="slidev-layout cover relative overflow-hidden bg-primary text-white">

    <!-- Left plaid stripe -->
    <div class="absolute left-10 top-0 h-full w-24 bg-no-repeat bg-cover" style="
        background-image: url('/assets/plaid-square.png');
        background-position: 60% 60%;
        background-size: cover;
      " />

    <!-- Main content -->
    <div class="relative mx-auto max-w-4xl pt-28 text-left">

      <!-- Institution -->
      <!-- <div class="text-lg font-serif mb-12">
        <slot name="institution" />
      </div> -->
      <!-- <div
      class="absolute left-0 top-0 h-full w-24 bg-no-repeat bg-cover"
      style="background-image: url('/assets/cmu-horiz-white-trans.svg')"
    /> -->

      <!-- Institution mark -->
      <div class="mb-14">
        <slot name="institution">
          <img src="/assets/cmu-horiz-white-trans.svg" alt="Carnegie Mellon University" class="h-10" />
        </slot>
      </div>

      <!-- Title -->
      <div class="text-5xl leading-tight font-light mb-8">
        <slot name="title" />
      </div>

      <!-- Divider -->
      <div class="h-px w-full bg-white/80 mb-6" />

      <!-- Presenter -->
      <div class="text-lg">
        <slot name="presenter" />
        <div class="italic opacity-80">
          <slot name="presenter-title" />
        </div>
      </div>

    </div>
  </div>
  <div class="absolute z-99 bottom-1 right-1">
    <JoinQRCode 
      fg="var(--cmu-text-on-primary)"
      :size="80"
      label=""
      label-position="right"
      label-class="text-xs opacity-60" 
    />
  </div>
</template>

<!-- <template>
  <div class="slidev-layout cover text-center">
    <slot />
  </div>
</template> -->

<!-- <template>
  <div class="slidev-layout split">
    <div class="left">
      <slot name="left" />
    </div>
    <div class="right">
      <slot name="right" />
    </div>
  </div>
</template> -->
