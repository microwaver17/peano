import { ref, type Ref } from 'vue'

const max_message = 100
const messages: Ref<string[]> = ref([])

export function addMessage(msg: string) {
  const now = new Date()
  msg = `[${now.toLocaleDateString()} ${now.toLocaleTimeString()}] ${msg}`
  messages.value.push(msg)
  messages.value = messages.value.slice(-max_message)
}

export function useMessage() {
  return messages
}
