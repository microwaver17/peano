import { ref, type Ref } from 'vue'
import type { Workspace } from '@/api'
import { WorkspaceService } from '@/api'

const currentWorkspace: Ref<Workspace | null> = ref(null)
const availableWorkspaces: Ref<Record<string, Workspace>> = ref({})

export function useCurrentWorkspace() {
  return currentWorkspace
}

export function useAvailableWorkspaces() {
  return availableWorkspaces
}

export function setCurrentWorkspace(workspace: Workspace) {
  currentWorkspace.value = workspace
}

export async function fetchAvailableWorkspace() {
  const res = await WorkspaceService.getWorkspaceGet()
  availableWorkspaces.value = res
}

export async function setPreferredWorkspace() {
  await fetchAvailableWorkspace()
  const keys = Object.keys(availableWorkspaces.value)
  if (keys.length > 0) {
    setCurrentWorkspace(availableWorkspaces.value[keys[0]])
  }
}
