<script setup lang="ts">
import { computed } from 'vue'
import type { MessageBoxResult } from "@/states/messageBox"

const props = defineProps({
    message: String,
    yesno: { type: Boolean, default: false },
    prompt: { type: Boolean, default: false },
})
const emit = defineEmits<{
    (e: 'selected', value: MessageBoxResult): void,
    (e: 'inputted', value: string): void,
}>()
</script>

<template>
    <div>
        <div class="fixed inset-0 flex justify-center items-center">
            <div class="border border-gray-500 bg-white drop-shadow-xl  p-4 rounded-md">
                <div v-html="props.message"></div>
                <div v-if="props.yesno">
                    <button @click="emit('selected', 'yes')">はい</button>
                    <button @click="emit('selected', 'no')" class="btn-gray">いいえ</button>
                </div>
                <div v-else>
                    <button @click="emit('selected', 'ok')">OK</button>
                </div>
            </div>
        </div>
    </div>
</template>