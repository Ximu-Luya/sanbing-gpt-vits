<script setup lang='ts'>
import { computed } from 'vue'
import { NLayout, NLayoutContent, NLayoutSider, NSpin } from 'naive-ui'
// @ts-ignore
import { JsonViewer } from "vue3-json-viewer"
import "vue3-json-viewer/dist/index.css"
import { useRoute, useRouter } from 'vue-router'
import Sider from './sider/index.vue'
// import Permission from './Permission.vue'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, useChatStore } from '@/store'

const router = useRouter()
const appStore = useAppStore()
const chatStore = useChatStore()
// const authStore = useAuthStore()

router.replace({ name: 'Chat', params: { uuid: chatStore.active } })

const { isMobile } = useBasicLayout()

const collapsed = computed(() => appStore.siderCollapsed)

// const needPermission = computed(() => !!authStore.session?.auth && !authStore.token)

const getMobileClass = computed(() => {
  if (isMobile.value)
    return ['rounded-none', 'shadow-none']
  return ['border', 'rounded-md', 'shadow-md', 'dark:border-neutral-800']
})

const getContainerClass = computed(() => {
  return [
    'h-full',
    { 'pl-[260px]': !isMobile.value && !collapsed.value },
  ]
})

const chatDataViewerCollapsed = computed(() => appStore.chatDataViewerCollapsed)

function handleUpdateCollapsed() {
  appStore.setChatDataViewerCollapsed(!chatDataViewerCollapsed.value)
}

const route = useRoute()

const uuid = computed(() => {
  return route.params.uuid
})

const chatDataLoading = computed(() => appStore.chatDataLoading)

const currentConversationData = computed(
  () => {
    if(chatDataLoading.value) return []

    const chatList = chatStore.getChatByUuid(+uuid)
    const wrapperChatList = chatList.map(chat => ({
      ...chat
    }))
    return wrapperChatList
  }
)
</script>

<template>
  <div class="h-full dark:bg-[#24272e] transition-all" :class="[isMobile ? 'p-0' : 'p-4']">
    <div class="h-full overflow-hidden flex" :class="getMobileClass">
      <NLayout class="z-40 transition" :class="getContainerClass" has-sider>
        <Sider />
        <NLayoutContent class="h-full">
          <RouterView v-slot="{ Component, route }">
            <component :is="Component" :key="route.fullPath" />
          </RouterView>
        </NLayoutContent>
      </NLayout>
      <NLayout class="z-40 transition" style="flex-grow: 0;overflow: visible;" has-sider sider-placement="right">
        <NLayoutContent />
        <NLayoutSider
          :collapsed="chatDataViewerCollapsed"
          collapse-mode="transform"
          :collapsed-width="0"
          :width="320"
          :native-scrollbar="true"
          show-trigger="arrow-circle"
          content-style="padding: 24px;"
          bordered
          @update-collapsed="handleUpdateCollapsed"
        >
          <NSpin :show="chatDataLoading">
            <JsonViewer :value="currentConversationData" copyable :expand-depth="3" expanded/>
          </NSpin>
        </NLayoutSider>
      </NLayout>
    </div>
    <!-- <Permission :visible="needPermission" /> -->
  </div>
</template>

<style>
.jv-code {
  padding: 0 !important;
}

.n-layout-scroll-container {
  overflow: visible !important;
}
</style>