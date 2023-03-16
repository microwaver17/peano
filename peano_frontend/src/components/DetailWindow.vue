<script setup lang="ts">
import { ImageService } from '@/api'
import type { Image as Image } from '@/api'
import { computed, onBeforeUpdate, onMounted, ref, watch } from 'vue'
import { useTagsMapJp } from '@/states/tags'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRouter } from 'vue-router'
import { HandThumbUpIcon } from '@heroicons/vue/24/solid'

const props = defineProps<{
    id: string | null
}>()
const emits = defineEmits<{
    (e: 'close'): void,
    (e: 'select'): void,
}>()
const router = useRouter()

const image = ref<Image | null>(null)
const tagMapJp = useTagsMapJp()
watch(props, async () => {
    if (props.id == null) {
        image.value = null
        return
    }
    image.value = await ImageService.findImageFindGet({ imageId: props.id })
})

onBeforeRouteLeave((to, from) => {
    if (props.id != null) {
        emits('close')
        return false
    }
})
onBeforeRouteUpdate((to, from) => {
    if (props.id != null) {
        emits('close')
        return false
    }
})
</script>

<template>
    <div>
        <div v-if="image != null" class="fixed inset-0 bg-white drop-shadow-lg">
            <div @click="emits('close')" class="absolute top-0 bottom-0 left-0 right-72   flex justify-center">
                <img :src="`/api/image/file?image_id=${image.id}&image_type=original`" class="max-h-full object-contain">
            </div>

            <div class="absolute top-10 bottom-0 right-0 w-72 px-1 flex flex-col gap-0.5 bg-slate-100 overflow-y-scroll">
                <div class="pill">ID: {{ image.id }}</div>
                <div class="pill ">Source: {{ image.source_type }}</div>
                <div class="pill  break-words">Path: {{ image.path }}</div>
                <div class="pill">Date: {{ image.metadata.last_updated }}</div>
                <div class="pill">ML推論: {{ image.metadata.ml == null ? '未完了' : '完了' }}</div>

                <h5>MLタグ</h5>
                <div v-if="image.metadata.ml != null" class="flex flex-col gap-0.5">
                    <div v-for="tag in image.metadata.ml.tags" class="" :key="tag.name">
                        <div class="flex flex-wrap">
                            <div class="pill mr-2">{{ tag.name }}</div>
                            <div class="pill mr-2" v-if="tag.name in tagMapJp">{{ tagMapJp[tag.name] }}</div>
                            <div class="pill">{{ tag.weight.toFixed(3) }}</div>
                        </div>
                    </div>
                </div>
                <div v-else>なし</div>

            </div>
            <div class="absolute top-0 right-0 w-72 h-8 flex">
                <button class="bg-white p-1.5 w-10 h-full flex items-center justify-center ">
                    <HandThumbUpIcon class="text-amber-300 hover:text-amber-200"></HandThumbUpIcon>
                </button>
                <button @click="emits('select')" class="grow h-full btn-green ">選択</button>
                <button @click="emits('close')" class="grow h-full ">閉じる</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.pill {
    @apply bg-blue-100 text-xs font-mono
}
</style>