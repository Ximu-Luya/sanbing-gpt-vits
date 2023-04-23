<script setup lang='ts'>
import { ref } from 'vue'
import { NSpin } from 'naive-ui'
// import { fetchChatConfig } from '@/api'
// import pkg from '@/../package.json'

// interface ConfigState {
//   timeoutMs?: number
//   reverseProxy?: string
//   apiModel?: string
//   socksProxy?: string
//   httpsProxy?: string
// }

const loading = ref(false)

// const config = ref<ConfigState>()

// async function fetchConfig() {
//   try {
//     loading.value = true
//     const { data } = await fetchChatConfig<ConfigState>()
//     config.value = data
//   }
//   finally {
//     loading.value = false
//   }
// }

// onMounted(() => {
//   fetchConfig()
// })
</script>

<template>
  <NSpin :show="loading">
    <div class="p-4 space-y-4">
      <h2 class="text-xl font-bold">
        Version - 散兵实时交谈
      </h2>
      <div class="p-2 space-y-2 rounded-md bg-neutral-100 dark:bg-neutral-700">
        <p>
          此项目基于开源项目
          <a
            class="text-blue-600 dark:text-blue-500"
            href="https://github.com/Chanzhaoyu/chatgpt-web"
            target="_blank"
          >
            chatgpt-web
          </a>
          进行二次开发
        </p>
        <p>
          制作团队：西木工作室/西木
        </p>
        <p>
          仓库地址：
          <a
            class="text-blue-600 dark:text-blue-500" 
            target="_blank"
            href="https://github.com/Ximu-Luya/sanbing-gpt-vits"
          >
            Ximu-Luya/sanbing-gpt-vits
          </a>
        </p>
      </div>
    </div>
  </NSpin>
</template>
