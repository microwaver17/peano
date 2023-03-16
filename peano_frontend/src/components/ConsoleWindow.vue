<script setup lang="ts">
import { useMessage } from '@/states/message';
import { computed, nextTick, ref, watch, type Ref } from 'vue';

const message_ref = useMessage();
const message = computed(() => {
    return message_ref.value.join('\n');
});

const console_ref = ref();

const props = defineProps({
    show: Boolean
});

watch(() => props.show, () => {
    nextTick(() => {
        console_ref.value.scrollTop = console_ref.value.scrollHeight;
    });
});

watch(message_ref, () => {
    nextTick(() => {
        console_ref.value.scrollTop = console_ref.value.scrollHeight;
    });
})

</script>

<template>
    <div v-show="props.show"
        class="fixed bottom-0 right-0 w-[600px] h-60 p-2  bg-white border-gray-300 font-mono text-xs border-t-2 border-l-2 rounded-tl-md flex flex-col">
        <textarea :value="message" ref="console_ref" class="grow w-full bg-gray-100" readonly></textarea>
        <div>
            <button @click="$router.push({ name: 'home' })"> ホーム</button>
            <button @click="$router.push({ name: 'gridView' })">グリッド</button>
            <button>マルチライン</button>
        </div>
    </div>
</template>