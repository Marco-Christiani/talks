<template>
    <div class="slidev-layout">
        <div class="absolute top-6 right-8 text-sm text-gray-400">
        <!-- <div class="absolute top-10 right-13 text-sm text-gray-400"> -->

        <!-- <div class="absolute bottom-6 right-6 text-sm font-light"> -->
        <!-- <div class="absolute bottom-6 left-6 text-sm text-gray-400"> -->
            <SlideCurrentNo /><span class="text-xs">/<SlidesTotal /></span>
        </div>

        <!-- <div class="absolute z-99 top-1 right-1"> -->
            <!-- <p style="color: var(--slidev-theme-primary)">foo</p> -->
            <!-- <JoinQRCode :size="60" /> -->
            <!-- <JoinQRCode :size="60" fg="--cmu-primary"  -->

            <!-- <JoinQRCode 
                fg="var(--cmu-text)"
                :size="50"
                label=""
                label-position="right"
                label-class="text-xs opacity-60" 
             /> -->

            <!-- <JoinQRCode :size="60" fg="var(--slidev-theme-primary)" /> -->
            <!-- <JoinQRCode :size="60" fg="var(--cmu-primary)" /> -->
            <!-- <JoinQRCode :size="60" fg="var(--cmu-text)" /> -->
            <!-- <JoinQRCode :size="60" fg="var(--cmu-text)" bg="var(--cmu-bg)" /> -->
        <!-- </div> -->

        <!-- Main content -->
        <div class="">
            <slot />
        </div>

        <!-- Bottom row -->
        <div class="absolute left-0 right-0 bottom-6 ml-4">
            <div class="flex items-end gap-6 pl-10 pr-10">
            <!-- <div class="flex items-end gap-6 pr-10"> -->
                <!-- strip that ends at logo -->
                <div class="h-2 flex-1 mb-2 bg-no-repeat" style="
                background-image: url('/assets/plaid-square.png');
                background-repeat: no-repeat;
                background-size: cover;
                background-position: 60% 60%;
            " />
                <img src="/assets/cmu-square-red-trans.png" class="h-16" />
            </div>
        </div>
    </div>
</template>
