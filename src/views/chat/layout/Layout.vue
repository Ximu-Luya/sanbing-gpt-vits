<script setup lang='ts'>
import { computed } from 'vue'
import { NLayout, NLayoutContent, NLayoutSider, NImage } from 'naive-ui'
import sanbing_lihui from '@/assets/sanbing_lihui.png'
// @ts-ignore
import { JsonViewer } from "vue3-json-viewer"
import "vue3-json-viewer/dist/index.css"
import { useRouter } from 'vue-router'
import Sider from './sider/index.vue'
// import Permission from './Permission.vue'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, useChatStore } from '@/store'
import { onMounted } from 'vue'

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

onMounted(() => {
  appStore.setChatDataViewerCollapsed(false)
})
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
          :width="500"
          :native-scrollbar="true"
          show-trigger="arrow-circle"
          content-style="padding: 24px;"
          bordered
          class="right-sider-container"
          @update-collapsed="handleUpdateCollapsed"
        >
          <NImage
            width="800"
            class="lihui-img"
            :src="sanbing_lihui"
          />
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

.right-sider-container{
  position: relative;
  overflow: hidden;
}

.lihui-img {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%) scale(4.5);
}
</style>