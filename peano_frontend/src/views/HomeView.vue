<script setup lang="ts">
import { addMessage } from "@/states/message"
import { onMounted, ref, type Ref } from "vue"
import { useAvailableWorkspaces, fetchAvailableWorkspace, useCurrentWorkspace } from '@/states/workspace'
import { showMessageBox } from '@/states/messageBox'
import { CommandService } from '@/api'

// 表示するワークスペース
const wsAvailables = useAvailableWorkspaces()
const wsCurrent = useCurrentWorkspace()
onMounted(() => {
    fetchAvailableWorkspace()
})

async function doScan() {
    if (wsCurrent.value == null) {
        return
    }

    const res = await showMessageBox(`${wsCurrent.value.name}のスキャンを開始しますか？<br>長い時間がかかる可能性があります。`, true)
    if (res != "yes") {
        return
    }

    CommandService.doDirscanCommandDirscanScanPost({ wsName: wsCurrent.value.name })
}
async function stopScan() {
    CommandService.stopDirscanCommandDirscanScanStopPost().then(() => {
        showMessageBox('中止しました。')
    })
}
async function doML() {
    if (wsCurrent.value == null) {
        return
    }

    const res = await showMessageBox(`${wsCurrent.value.name}の推論を開始しますか？<br>長い時間がかかる可能性があります。`, true)
    if (res != "yes") {
        return
    }

    CommandService.doMlscanCommandMlscanScanPost({ wsName: wsCurrent.value.name })
}
async function stopML() {
    CommandService.stopMlscanCommandMlscanScanStopPost().then(() => {
        showMessageBox('中止しました。')
    })
}
async function doMLPreprocess() {
    if (wsCurrent.value == null) {
        return
    }

    const res = await showMessageBox("前処理を開始しますか？<br>長い時間がかかる可能性があります。", true)
    if (res != "yes") {
        return
    }

    CommandService.doPreprocessCommandMlscanPreprocessPost({ wsName: wsCurrent.value.name })
}

async function fixDb() {
    CommandService.fixDbCommandDbFixPost()
    showMessageBox('実行しました。')
}
</script>

<template>
    <div class="fixed inset-0 m-5">
        <h2>ワークスペース選択</h2>
        <div class="mb-6 flex items-center">
            <select class="w-80 block" v-model="wsCurrent">
                <option :value="null" disabled>選択してください</option>
                <option v-for="aws in wsAvailables" :value="aws" :key="aws.name">
                    {{ aws.name }}
                </option>
            </select>
            <button @click="fetchAvailableWorkspace">更新</button>
        </div>
        <h2>ビュー</h2>
        <div class="mb-6">
            <button @click="$router.push({ name: 'gridView' })">グリッド</button>
            <button @click="addMessage('bbb')">マルチライン</button>
        </div>
        <h2>コマンド</h2>
        <div class="mb-6">
            <div class="flex items-center mb-1">
                <label class="w-24">スキャン</label>
                <button @click="doScan">実行</button>
                <button @click="stopScan" class="btn-red">中断</button>
            </div>
            <div class="flex items-center">
                <label class="w-24">推論</label>
                <button @click="doML">実行</button>
                <button @click="stopML" class="btn-red">中断</button>
                <button @click="doMLPreprocess" class="btn-green">前処理</button>
            </div>
            <div class="flex items-center">
                <label class="w-24">データベース</label>
                <button @click="fixDb">整合性チェック</button>
            </div>
        </div>
        <h2>設定</h2>
        <button @click="$router.push({ name: 'workspaceSetting' })">ワークスペース</button>
        <button>DB概覧</button>
        <button>画像の無視設定</button>
    </div>
</template>

<style scoped></style>