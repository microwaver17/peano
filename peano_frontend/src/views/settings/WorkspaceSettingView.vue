<script setup lang="ts">
import type { ApiError, Workspace } from '@/api'
import { computed, ref, watch, onMounted, type Ref } from 'vue'
import { useAvailableWorkspaces, fetchAvailableWorkspace } from '@/states/workspace'
import { showMessageBox } from '@/states/messageBox'
import { WorkspaceService } from "@/api"
import MessageBox from '@/components/MessageBox.vue'

const showMesBox = ref(false)
const mesBoxMes = ref("")

// 表示するワークスペース
const availables = useAvailableWorkspaces()
const selectedIdx: Ref<number | null> = ref(null)
onMounted(() => {
    refreshWorkspaceList()
})


// フォームデータ
const formWorkspace = ref({
    name: "",
    scanDirsStr: "",
    ignorePatsStr: "",
})
watch(selectedIdx, () => {
    if (selectedIdx.value == null) {
        formWorkspace.value = {
            name: "",
            scanDirsStr: "",
            ignorePatsStr: "",
        }
        return
    }
    const selected = availables.value[selectedIdx.value]
    formWorkspace.value.name = selected.name
    formWorkspace.value.scanDirsStr = selected.scan_directories!.join('\n')
    formWorkspace.value.ignorePatsStr = selected.ignore_patterns!.join('\n')
})

function refreshWorkspaceList() {
    fetchAvailableWorkspace()
}

async function apply(type: 'mod' | 'add' | 'del') {
    const conf = await showMessageBox('実行しますか？', true)
    if (conf != "yes") {
        return
    }

    const name = formWorkspace.value.name

    const sds = formWorkspace.value.scanDirsStr.trim()
    const ips = formWorkspace.value.ignorePatsStr.trim()
    const scansDirList = sds == "" ? [] : sds.split('\n')
    const ignorePatsList = ips == "" ? [] : ips.split('\n')
    const workspace: Workspace = {
        ignore_patterns: ignorePatsList,
        name: name,
        scan_directories: scansDirList,
        scan_remotes: {},
    }
    let pms
    if (type == 'mod') {
        pms = WorkspaceService.updateWorkspaceUpdatePost({ requestBody: workspace })
    } else if (type == 'del') {
        pms = WorkspaceService.deleteWorkspaceDeletePost({ requestBody: workspace })
    } else {
        pms = WorkspaceService.createWorkspaceCreatePost({ requestBody: workspace })
    }
    pms.then((res) => {
        if (res.result == true) {
            showMessageBox("成功しました")
        } else {
            showMessageBox("失敗しました<br>" + res.reason)
        }
    }).catch((e: ApiError) => {
        let err = String(e)
        if ('body' in e && 'detail' in e.body) {
            err = e.body.detail
        }
        console.log(e.body)
        showMessageBox("エラー<br>" + String(err))
    })
}

</script>

<template>
    <div class="fixed inset-0 m-5">
        <h2 class="mb-6">ワークスペース設定</h2>
        <div class="flex items-center justify-between w-[700px] p-4 mb-4 border-2 border-gray-400">
            <select v-model="selectedIdx" class="w-80 block">
                <option :value="null" disabled>選択してください</option>
                <option v-for="(aws, idx) in availables" :value="idx" :key="aws.name">
                    {{ aws.name }}
                </option>
            </select>
            <div>
                <button @click="apply('del')" class="btn-red">削除</button>
                <button @click="refreshWorkspaceList">リスト更新</button>
            </div>
        </div>
        <div class="flex flex-col w-[700px] p-4 border-2 border-gray-400 ">
            <div class="flex justify-between items-center mb-2">
                <label>ワークスペース名</label>
                <input v-model="formWorkspace.name" class="w-8/12">
            </div>
            <div class="flex justify-between items-center mb-2">
                <label>スキャンディレクトリ</label>
                <textarea v-model="formWorkspace.scanDirsStr" class="w-8/12 h-32 font-mono"></textarea>
            </div>
            <div class="flex justify-between items-center mb-2">
                <label>リモートスキャン<br>"(site): (query)"</label>
                <textarea class="w-8/12 h-32 font-mono"></textarea>
            </div>
            <div class="flex justify-between items-center mb-2">
                <label>無視パターン（正規表現）</label>
                <textarea v-model="formWorkspace.ignorePatsStr" class="w-8/12 h-32 font-mono"></textarea>
            </div>
            <div class="flex">
                <button @click="apply('mod')">変更</button>
                <button @click="apply('add')" class="btn-green">追加</button>
            </div>
        </div>
    </div>
</template>