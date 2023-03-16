import { ref } from 'vue'
import { ImageService } from '@/api'

const tags = ref<string[]>([])
const tags_map_jp = ref<Record<string, string>>({})
let loaded = false

async function fetchTags() {
  const tg = await ImageService.getTagsMapJpImageTagsMapJpGet()
  tags_map_jp.value = tg
  tags.value = Object.keys(tg)
}

export function useTagsMapJp() {
  if (loaded == false) {
    fetchTags().then(() => {
      loaded = true
    })
  }
  return tags_map_jp
}
