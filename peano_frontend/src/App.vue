<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { Bars3Icon, HomeIcon } from '@heroicons/vue/24/solid'
import ConsoleWindow from "@/components/ConsoleWindow.vue"
import MessageBox from "@/components/MessageBox.vue"
import { onMounted, ref } from 'vue'
import {
  fetchAvailableWorkspace, setCurrentWorkspace, useAvailableWorkspaces, useCurrentWorkspace
} from '@/states/workspace'
import { onMessageBoxSelected, useMessageBox } from "@/states/messageBox"


const show_console = ref(false)
const messageBox = useMessageBox()

const WsAvailable = useAvailableWorkspaces()
const WsCurrent = useCurrentWorkspace()

</script>

<template>
  <div>
    <RouterView></RouterView>
    <ConsoleWindow :show="show_console"></ConsoleWindow>
    <Bars3Icon @click="show_console = !show_console"
      class="fixed bottom-0 left-10 w-8 h-8 m-1 hover:bg-gray-200 bg-white rounded-lg">
    </Bars3Icon>
    <HomeIcon @click="$router.push({ name: 'home' })"
      class="fixed bottom-0 left-0 w-8 h-8 m-1 hover:bg-gray-200 bg-white rounded-lg">
    </HomeIcon>
    <MessageBox v-show="messageBox.show.value" :message="messageBox.message.value" :yesno="messageBox.yesNo.value"
      @selected="onMessageBoxSelected">
    </MessageBox>
  </div>
</template>

<style scoped></style>
