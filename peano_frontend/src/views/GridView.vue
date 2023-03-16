<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch, type Ref } from 'vue'
import type { ImageDigest } from '@/api'
import { ImageService, WorkspaceService } from '@/api'
import { useCurrentWorkspace, setPreferredWorkspace } from '@/states/workspace'
import { CheckIcon, XMarkIcon, StarIcon } from "@heroicons/vue/24/outline"
import { StarIcon as SolidStarIcon } from "@heroicons/vue/24/solid"
import DetailWindow from '@/components/DetailWindow.vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRouter } from 'vue-router'
import LoadingWindow from "@/components/LoadingWindow.vue"
export interface Props {
    /** ワークスペース名 */
    wsName: string | null
    keyword: string
    orderBy: "id" | "date" | "random"
    order: "asc" | "desc"
    searchContext: "normal" | 'similar'
    /** JSONの配列 */
    imageQueryIds: string
    time: number | string
}

const props = withDefaults(defineProps<Props>(), {
    wsName: null,
    keyword: "",
    orderBy: "random",
    order: "asc",
    searchContext: "normal",
    /** JSONの配列 */
    imageQueryIds: "[]",
    time: 0
})

const router = useRouter()
const workspace = useCurrentWorkspace()
const loading = ref(false)
const gridElement = ref<HTMLElement | null>(null)
/** 画像書斎画面に表示する画像 (nullで非表示) */
const detailImageId = ref<string | null>(null)
const showAdditionalOption = ref(false)

// 表示する画像
const images: Ref<ImageDigest[]> = ref([])
const imagePaging = ref({
    loadAtOnes: 100,
})


// 可変画像幅
const thumbStyle: Ref<'grid' | 'scroll'> = ref('grid')
// const thumbStyle: Ref<'grid' | 'scroll'> = ref('scroll')
const thumbSize = ref(500)
const _nextThumbSize = ref(500)
const thumbStyleAttr = computed(() => {
    let attr = {
        width: "",
        height: "",
    }
    if (thumbStyle.value == 'grid') {
        const value = thumbSize.value / 3
        attr.width = `${value}px`
        attr.height = `${value}px`
    } else {
        const value = 1.0 * thumbSize.value / 500 * 95
        attr.width = `${value}vw`
        attr.height = `auto`
    }
    return attr
}, {})
function thumbURL(image_id: string) {
    let url = `/api/image/file?image_id=${image_id}`
    if (thumbStyle.value == 'grid') {
        url += "&image_type=thumbnail"
    } else {
        url += "&image_type=original"
    }
    return url
}
function calcWidthSimilarity(similarity: number): string {
    let value = thumbSize.value / 3.0
    const simValue = Math.abs(similarity)
    value *= simValue * simValue
    return `${value}px`
}

/**
 * 画像サイズ変更時にスクロール位置を固定する
 */
function fixScrollPosition() {
    const pos = window.scrollY
    const pos_rate = (1.0 * pos) / window.innerHeight
    thumbSize.value = _nextThumbSize.value
    nextTick(() => {
        const new_pos = window.innerHeight * pos_rate
        window.scroll(0, new_pos)
    })

    // const shift = gridElement.value!.scrollTop
    // const pos = (1.0 * shift) / gridElement.value!.scrollHeight
    // thumbSize.value = _nextThumbSize.value
    // nextTick(() => {
    //     const new_pos = gridElement.value!.scrollHeight * pos
    //     gridElement.value!.scrollTop = new_pos
    // })
}

// 画像検索
const keyword = ref('')
const orderBy: Ref<"id" | "date" | "random"> = ref('random')
const order: Ref<"asc" | "desc"> = ref('asc')
const searchContext: Ref<"normal" | 'similar'> = ref('normal')
/** 類似検索する画像ID */
const imageQueryIds = ref<Set<string>>(new Set())
const loadedCount = ref(0)

/**
 * 続きの画像画像取得 
 *  
 * imageの最後から自動で続きを取得
 * image.length == 0 なら新規画像取得になる
 */
async function fetchMoreImageList() {
    if (workspace.value == null) {
        return
    }
    if (searchContext.value == 'normal') {
        loading.value = true
        ImageService.getImageGet({
            wsName: workspace.value.name,
            start: loadedCount.value,
            end: loadedCount.value + imagePaging.value.loadAtOnes - 1,
            keyword: keyword.value,
            orderBy: orderBy.value,
            order: order.value
        }).then(res => {
            images.value = images.value.concat(res)
            loadedCount.value += imagePaging.value.loadAtOnes
        }).finally(() => {
            loading.value = false
        })

    } else {
        const ids = [...imageQueryIds.value]
        if (ids.length == 0) {
            return
        }
        loading.value = true
        ImageService.getSimilarImagesImageSimilarGet({
            workspace: workspace.value.name,
            start: loadedCount.value,
            end: loadedCount.value + imagePaging.value.loadAtOnes - 1,
            keyword: keyword.value,
            orderBy: "similarity",
            order: order.value,
            queryIds: ids
        }).then(res => {
            images.value = images.value.concat(res)
            loadedCount.value += imagePaging.value.loadAtOnes
        }).finally(() => {
            loading.value = false
        })
    }
}

async function copyFromPropAndSearch() {
    if (workspace.value == null && props.wsName != null) {
        workspace.value = await WorkspaceService.findWorkspaceFindGet({
            wsName: props.wsName
        })
    }
    else if (workspace.value == null && props.wsName == null) {
        await setPreferredWorkspace()
        if (workspace.value == null) {
            console.log('[GridView] ワークスペースが設定できません')
            return
        }
    }
    keyword.value = props.keyword
    orderBy.value = props.orderBy
    order.value = props.order
    searchContext.value = props.searchContext
    imageQueryIds.value = new Set(JSON.parse(props.imageQueryIds))
    images.value = []
    loadedCount.value = 0
    fetchMoreImageList()
}

// ページ遷移が行われたタイミングで検索を実行
// onBeforeRouteUpdate((to, from) => {
// })

// onMounted(copyFromProp)
watch(props, copyFromPropAndSearch, { immediate: true })

// ワークスペースが変更された時に再検索
watch(workspace, () => {
    if (workspace.value?.name == props.wsName) {
        return
    }
    images.value = []
    imageQueryIds.value = new Set()
    fetchMoreImageList()
})

/**
 * 検索
 * 
 * クエリパラメータを付けて自分自身に移動
 */
function navigateSearch() {
    router.push({
        name: 'gridView', query: {
            wsName: workspace.value?.name,
            keyword: keyword.value,
            orderBy: orderBy.value,
            order: order.value,
            searchContext: searchContext.value,
            imageQueryIds: JSON.stringify([...imageQueryIds.value]),
            time: Date.now(),
        }
    })
}

/**
 * 通常の検索
 */
function searchNormal() {
    searchContext.value = "normal"
    navigateSearch()
}

/**
 * 類似画像検索
 */
function searchSimilar() {
    // 類似検索に切り替えたときは降順（似てる順）に変更
    if (searchContext.value == "normal") {
        order.value = "desc"
    }
    searchContext.value = "similar"
    navigateSearch()
}

</script>

<template>
    <div>
        <!-- 画像一覧グリッド-->
        <div ref="gridElement" class="pt-10" :class="thumbStyle == 'grid' ? 'pr-36' : 'pr-0'">
            <div class="flex flex-wrap justify-center mt-5">
                <div v-for="image in images" :key="image.id">
                    <div @click="detailImageId = image.id" class="m-0.5 select-none bg-gray-200">
                        <img :style="thumbStyleAttr" :class="thumbStyle == 'scroll' ? 'object-contain' : 'object-cover'"
                            :src="thumbURL(image.id)" loading="lazy">
                        <div class="opacity-only-pc absolute inset-0 opacity-0 hover:opacity-70">
                            <CheckIcon @click.stop="imageQueryIds.add(image.id)"
                                class="absolute bottom-0 right-0 bg-white  hover:bg-gray-300 w-8 h-8 ">
                            </CheckIcon>
                        </div>
                        <!-- <SolidStarIcon class="absolute bottom-0 left-0 w-4 h-4 text-amber-300"> </SolidStarIcon> -->
                        <!-- <StarIcon class="absolute bottom-0 left-0 w-4 h-4 text-rose-400"> </StarIcon> -->
                    </div>
                    <div v-show="image.similarity != null" class="h-4 bg-slate-200"
                        :style="{ width: thumbStyleAttr.width }">
                        <div :style="{ width: calcWidthSimilarity(image.similarity ? image.similarity : 0) }"
                            class="absolute top-0 bottom-0 left-0 bg-indigo-300"></div>
                        <div class="text-xs h-4 leading-4 font-mono text-right">{{ image.similarity ?
                            image.similarity.toFixed(5) : 0 }}</div>
                    </div>
                </div>
            </div>

            <div v-show="images.length > 0" class="flex justify-center">
                <button @click="fetchMoreImageList" class="w-11/12 h-12 text-lg">続きを読み込む</button>
            </div>
        </div>

        <!-- 選択中の画像 -->
        <div v-show="thumbStyle == 'grid'"
            class="fixed top-0 right-0 bottom-0  pt-10 w-36 bg-slate-100 drop-shadow-md border-l border-blue-100">
            <div class="h-full flex flex-col items-center py-2">
                <label>選択中画像</label>
                <div class="flex flex-col grow items-center overflow-y-scroll no-scroll-bar mt-2 mb-2">
                    <div v-for="image_id in [...imageQueryIds].reverse()" :key="image_id">
                        <div @click="detailImageId = image_id" class="p-1 w-36 h-36 select-none bg-gray-200">
                            <img class="w-full h-full object-cover" :src="thumbURL(image_id)" loading="lazy">
                            <div class="opacity-only-pc absolute inset-0 opacity-0 hover:opacity-70">
                                <XMarkIcon @click.stop="imageQueryIds.delete(image_id)"
                                    class="absolute bottom-0 right-0 bg-white  hover:bg-gray-300 w-8 h-8 ">
                                </XMarkIcon>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 入力フォーム -->
        <div @keypress.enter.prevent="navigateSearch"
            class="search-bar flex items-center fixed top-0 left-0 right-0 bg-slate-100 drop-shadow-md border-b border-blue-100">

            <input type="search" v-model="keyword" class="w-60 text-xs">
            <select v-model="orderBy">
                <option value="id">ID</option>
                <option value="date">日付</option>
                <option value="random">ランダム</option>
            </select>
            <select v-model="order">
                <option value="asc">↑昇順</option>
                <option value="desc">↓降順</option>
            </select>
            <div class="grow"></div>
            <div class="px-1 text-blue-900">{{ workspace?.name }}</div>
            <button @click="searchNormal" class="">通常検索</button>
            <button @click="searchSimilar" class=" btn-green">類似検索</button>
            <button @click="showAdditionalOption = !showAdditionalOption" class="btn-gray">設定</button>
        </div>
        <div v-show="showAdditionalOption"
            class="search-bar flex items-center fixed top-10 right-0 p-2 border-2 border-t-0 border-blue-100 drop-shadow-md  bg-slate-100">
            <select v-model="thumbStyle">
                <option value="grid">グリッド</option>
                <option value="scroll">スクロール</option>
            </select>
            <input @input="fixScrollPosition" type="range" min="100" max="1000" v-model="_nextThumbSize">
        </div>

        <DetailWindow :id="detailImageId" @close="detailImageId = null"
            @select="(imageQueryIds.add(detailImageId!)) && (detailImageId = null)">
        </DetailWindow>
        <LoadingWindow v-show="loading"></LoadingWindow>
        <!-- <LoadingWindow v-show="true"></LoadingWindow> -->
    </div>
</template>

<style scoped lang="postcss">
.search-bar {

    input,
    label,
    select,
    button {
        @apply mx-1 my-1 leading-5 text-sm
    }
}

@media (hover: none) {
    .opacity-only-pc:hover {
        opacity: 0;
    }
}
</style>
