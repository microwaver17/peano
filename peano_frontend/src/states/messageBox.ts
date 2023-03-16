import { ref } from 'vue'

export type MessageBoxResult = 'yes' | 'no' | 'ok' | 'cancel'

const show_dialog_scan = ref(false)
const dialog_message = ref('')
const showModeYesNo = ref(false)

let resolve: ((res: MessageBoxResult) => void) | null

export function useMessageBox() {
  return {
    show: show_dialog_scan,
    message: dialog_message,
    yesNo: showModeYesNo
  }
}

export function showMessageBox(message: string, yesno: boolean = false): Promise<MessageBoxResult> {
  dialog_message.value = message
  show_dialog_scan.value = true
  showModeYesNo.value = yesno
  const promise = new Promise<MessageBoxResult>((r) => {
    resolve = r
  })
  return promise
}

export function onMessageBoxSelected(value: MessageBoxResult) {
  if (resolve != null) {
    resolve(value)
    resolve = null
    show_dialog_scan.value = false
  }
}
