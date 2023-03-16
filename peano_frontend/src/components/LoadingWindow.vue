<script setup lang="ts">
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
</script>

<template>
    <div>
        <!-- <div class="fixed inset-0 bg-white opacity-40">
                                                                                                        </div> -->
        <div
            class="fixed bottom-4 left-4 w-[300px] flex items-center justify-center bg-slate-50 p-3 rounded-3xl drop-shadow-xl">
            <ArrowPathIcon class="w-10 h-10 mr-2"></ArrowPathIcon>
            <span class="text-3xl pb-2">Loading...</span>
        </div>
    </div>
</template>