import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import WorkspaceSettingView from '@/views/settings/WorkspaceSettingView.vue'
import GridView from '@/views/GridView.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'root',
      redirect: { name: 'home' }
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView
    },
    {
      path: '/view/grid',
      name: 'gridView',
      component: GridView,
      props: (router) => router.query
    },
    {
      path: '/image',
      name: 'detailWindow',
      component: GridView,
      props: (router) => router.query
    },
    {
      path: '/setting/workspace',
      name: 'workspaceSetting',
      component: WorkspaceSettingView
    }
  ]
})

export default router
