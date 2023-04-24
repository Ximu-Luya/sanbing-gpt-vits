<script setup lang='ts'>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { NAutoComplete, NButton, NInput, useDialog, useMessage, useNotification } from 'naive-ui'
import html2canvas from 'html2canvas'
import { Message } from './components'
import { useScroll } from './hooks/useScroll'
import { useChat } from './hooks/useChat'
import { useCopyCode } from './hooks/useCopyCode'
import { useUsingContext } from './hooks/useUsingContext'
import HeaderComponent from './components/Header/index.vue'
import { HoverButton, SvgIcon } from '@/components/common'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, useChatStore, usePromptStore } from '@/store'
import { fetchChatAPIProcess, fetchVoice } from '@/api'
import { t } from '@/locales'

let controller = new AbortController()
const notification = useNotification()

// const openLongReply = import.meta.env.VITE_GLOB_OPEN_LONG_REPLY === 'true'

const route = useRoute()
const dialog = useDialog()
const ms = useMessage()

const chatStore = useChatStore()
const appStore = useAppStore()

useCopyCode()

const { isMobile } = useBasicLayout()
const { addChat, updateChat, updateChatSome, getChatByUuidAndIndex } = useChat()
const { scrollRef, scrollToBottom } = useScroll()
const { usingContext, toggleUsingContext } = useUsingContext()

const { uuid } = route.params as { uuid: string }

const dataSources = computed(() => chatStore.getChatByUuid(+uuid))
const conversationList = computed(() => dataSources.value.filter(item => (!item.inversion && !item.error)))
// 获取Store中的AI音频服务可用性
const voiceEngineAvailable = computed(() => appStore.voiceEngineAvailable)

const prompt = ref<string>('')
const loading = ref<boolean>(false)

// 显示/隐藏包装prompt
const isHidden = ref<boolean>(true)
const shouldDisplayDataSources= computed(
  () => {
    const chatList = chatStore.getChatByUuid(+uuid)
    const wrapperChatList = chatList.map(chat => ({
      ...chat,
      showText: isHidden.value? chat.text : (chat.conversationOptions?.wrappedPrompt ?? chat.text)
    }))
    return wrapperChatList
  }
)
const chatDataViewerCollapsed = computed(() => appStore.chatDataViewerCollapsed)
function handleButtonHide(){
  appStore.setChatDataViewerCollapsed(false)
}

// 添加PromptStore
const promptStore = usePromptStore()
// 使用storeToRefs，保证store修改后，联想部分能够重新渲染
const { promptList: promptTemplate } = storeToRefs<any>(promptStore)

function handleSubmit() {
  onConversation()
}

function onConversation() {
  let message = prompt.value

  if (loading.value)
    return

  if (!message || message.trim() === '')
    return

  controller = new AbortController()

  updateUserChat(message)
  onUpdateReply(message)
}

function updateUserChat(message: string) {
  addChat(
    +uuid,
    {
      dateTime: new Date().toLocaleString(),
      text: message,
      inversion: true,
      error: false,
      conversationOptions: null,
      requestOptions: { prompt: message, options: null },
    },
  )
  scrollToBottom()
}

async function fetchChatAPIOnce(message: string) {
  let done = false // 请求是否已完成
  let currentStopIndex = 0 // 当前句号索引
  let fetchIndex = 0 // 当前音频获取序号
  let voices: string[] = [] // 音频文件路径数组
  let voicePlayIndex = 0 // 音频播放序号

  await fetchChatAPIProcess<Chat.ConversationResponse>({
    prompt: message,
    signal: controller.signal,
    onDownloadProgress: ({ event }) => {
      const xhr = event.target
      const { responseText } = xhr
      // console.log(responseText)
      // 找出待处理句子（上一个句号到句子最后。）
      const pendingSentence = responseText.substring(currentStopIndex)
      // 待处理句子中是否有句号
      if(pendingSentence.indexOf("。") >= 0) {
        // 根据句号index截取句子
        const sentence =  pendingSentence.substring(0, pendingSentence.indexOf("。") + 1)
        console.log(sentence)
        // 更新句号index索引
        currentStopIndex += sentence.length

        // 根据句子获取音频文件
        if (voiceEngineAvailable.value) {
          const index = fetchIndex
          fetchVoice(sentence).then(res => {
            // 将获取到的音频文件路径存储到voices数组中
            voices[index] = res.data[1].name
            if (index === 0) {
              // 如果当前下载的音频是第一首，则直接播放
              playVoice(0)
            }
          })
          .catch(err => {
            appStore.setVoiceEngineAvailable(false)
            console.error("AI音频生成失败：不再AI生成音频，请检查本地是否已启动AI音频服务。启动后可以在设置中再次打开AI服务开关")
            notification.error({
              content: 'AI音频生成失败',
              meta: '不再AI生成音频，请检查本地是否已启动AI音频服务。启动后可以在设置中再次打开AI服务开关',
              duration: 5000,
              keepAliveOnHover: true
            })
            console.error(err)
          })

          fetchIndex++
        } 

        // 播放指定index音频
        function playVoice(index: number) {
          // 指定index不存在，或者已经播放完成，则不再播放
          if (voices[index]) {
            console.log(`计划播放第 ${index + 1} 个音频`)
            const audio = new Audio("http://127.0.0.1:7860/file=" + voices[index]) // 播放音频
            audio.play()
            audio.onended = () => {
              // 音频播放完成后，继续播放下一个音频文件
              console.log(`第 ${index + 1} 个音频播放完毕`)
              voicePlayIndex++
              if (voicePlayIndex < fetchIndex || !done) {
                setTimeout(() => {
                  playVoice(voicePlayIndex)
                }, 500)
              }
            }
          } else {
            console.log(`第 ${index + 1} 个音频不存在，等待500毫秒`)
            setTimeout(() => {
              playVoice(index)
            }, 500) // 如果当前音频还没有下载好对应索引不存在，等待0.5秒后再次尝试播放
          }
        }
      }

      try {
        updateChat(
          +uuid,
          dataSources.value.length - 1,
          {
            dateTime: new Date().toLocaleString(),
            text: responseText ?? '',
            inversion: false,
            error: false,
            loading: false,
            conversationOptions: null,
            requestOptions: { prompt: message },
          },
        )
        scrollToBottom()
      }
      catch (error) {}
    },
  })

  // 文字请求完成标识置为true
  done = true
}

async function onUpdateReply(message: string) {
  loading.value = true
  prompt.value = ''

  const lastContext = conversationList.value[conversationList.value.length - 1]?.conversationOptions
  let options: Chat.ConversationRequest = {  
    conversationStage:lastContext?(lastContext.conversationStage??0):0,
  }

  if (lastContext && usingContext.value)
    options = { ...lastContext, ... options}

  let pureHistory = conversationList.value.map((item) => {return {user:item.requestOptions.prompt, assistant:item.text}})

  addChat(
    +uuid,
    {
      dateTime: new Date().toLocaleString(),
      text: '',
      loading: true,
      inversion: false,
      error: false,
      conversationOptions: null,
      requestOptions: { prompt: message, options: { ...options } },
    },
  )
  
  console.log('conversationList长度',conversationList.value.length)
  options = {...options, textHistory:pureHistory}
  scrollToBottom()

  console.log(options)
  try {
    appStore.setChatDataLoading(true)
    await fetchChatAPIOnce(message)
  }
  catch (error: any) {
    const errorMessage = error?.message ?? t('common.wrong')

    if (error.message === 'canceled') {
      updateChatSome(
        +uuid,
        dataSources.value.length - 1,
        {
          loading: false,
        },
      )
      scrollToBottom()
      return
    }

    const currentChat = getChatByUuidAndIndex(+uuid, dataSources.value.length - 1)

    if (currentChat?.text && currentChat.text !== '') {
      updateChatSome(
        +uuid,
        dataSources.value.length - 1,
        {
          text: `${currentChat.text}\n[${errorMessage}]`,
          error: false,
          loading: false,
        },
      )
      return
    }

    updateChat(
      +uuid,
      dataSources.value.length - 1,
      {
        dateTime: new Date().toLocaleString(),
        text: errorMessage,
        inversion: false,
        error: true,
        loading: false,
        conversationOptions: null,
        requestOptions: { prompt: message, options: { ...options } },
      },
    )
    scrollToBottom()
  }
  finally {
    // console.log('用户',conversationList.value[conversationList.value.length - 2]?.conversationOptions)
    // console.log('gpt',conversationList.value[conversationList.value.length - 1]?.conversationOptions)
    loading.value = false
    appStore.setChatDataLoading(false)
  }
}

async function onRegenerate(index: number) {
  if (loading.value)
    return

  controller = new AbortController()

  const { requestOptions } = dataSources.value[index]

  let message = requestOptions?.prompt ?? ''

  let options: Chat.ConversationRequest = {}

  let pureHistory = conversationList.value.map((item) => {return {user:item.requestOptions.prompt, assistant:item.text}})

  if (requestOptions.options)
    options = { ...requestOptions.options }
  
  options = {...options, textHistory:pureHistory}

  loading.value = true

  updateChat(
    +uuid,
    index,
    {
      dateTime: new Date().toLocaleString(),
      text: '',
      inversion: false,
      error: false,
      loading: true,
      conversationOptions: null,
      requestOptions: { prompt: message, ...options },
    },
  )

  try {
    appStore.setChatDataLoading(true)
    await fetchChatAPIOnce(message)
  }
  catch (error: any) {
    if (error.message === 'canceled') {
      updateChatSome(
        +uuid,
        index,
        {
          loading: false,
        },
      )
      return
    }

    const errorMessage = error?.message ?? t('common.wrong')

    updateChat(
      +uuid,
      index,
      {
        dateTime: new Date().toLocaleString(),
        text: errorMessage,
        inversion: false,
        error: true,
        loading: false,
        conversationOptions: null,
        requestOptions: { prompt: message, ...options },
      },
    )
  }
  finally {
    appStore.setChatDataLoading(false)
    loading.value = false
  }
}

function handleExport() {
  if (loading.value)
    return

  const d = dialog.warning({
    title: t('chat.exportImage'),
    content: t('chat.exportImageConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: async () => {
      try {
        d.loading = true
        const ele = document.getElementById('image-wrapper')
        const canvas = await html2canvas(ele as HTMLDivElement, {
          useCORS: true,
        })
        const imgUrl = canvas.toDataURL('image/png')
        const tempLink = document.createElement('a')
        tempLink.style.display = 'none'
        tempLink.href = imgUrl
        tempLink.setAttribute('download', 'chat-shot.png')
        if (typeof tempLink.download === 'undefined')
          tempLink.setAttribute('target', '_blank')

        document.body.appendChild(tempLink)
        tempLink.click()
        document.body.removeChild(tempLink)
        window.URL.revokeObjectURL(imgUrl)
        d.loading = false
        ms.success(t('chat.exportSuccess'))
        Promise.resolve()
      }
      catch (error: any) {
        ms.error(t('chat.exportFailed'))
      }
      finally {
        d.loading = false
      }
    },
  })
}

function handleDelete(index: number) {
  if (loading.value)
    return

  dialog.warning({
    title: t('chat.deleteMessage'),
    content: t('chat.deleteMessageConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: () => {
      chatStore.deleteChatByUuid(+uuid, index)
    },
  })
}

function handleClear() {
  if (loading.value)
    return

  dialog.warning({
    title: t('chat.clearChat'),
    content: t('chat.clearChatConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: () => {
      chatStore.clearChatByUuid(+uuid)
    },
  })
}

function handleEnter(event: KeyboardEvent) {
  if (!isMobile.value) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit()
    }
  }
  else {
    if (event.key === 'Enter' && event.ctrlKey) {
      event.preventDefault()
      handleSubmit()
    }
  }
}

function handleStop() {
  if (loading.value) {
    controller.abort()
    loading.value = false
  }
}

function handleSendOrderId(orderId: string) {
  prompt.value = orderId
  handleSubmit()
}

// 可优化部分
// 搜索选项计算，这里使用value作为索引项，所以当出现重复value时渲染异常(多项同时出现选中效果)
// 理想状态下其实应该是key作为索引项,但官方的renderOption会出现问题，所以就需要value反renderLabel实现
const searchOptions = computed(() => {
  if (prompt.value.startsWith('/')) {
    return promptTemplate.value.filter((item: { key: string }) => item.key.toLowerCase().includes(prompt.value.substring(1).toLowerCase())).map((obj: { value: any }) => {
      return {
        label: obj.value,
        value: obj.value,
      }
    })
  }
  else {
    return []
  }
})
// value反渲染key
const renderOption = (option: { label: string }) => {
  for (const i of promptTemplate.value) {
    if (i.value === option.label)
      return [i.key]
  }
  return []
}

const placeholder = computed(() => {
  if (isMobile.value)
    return t('chat.placeholderMobile')
  return t('chat.placeholder')
})

const buttonDisabled = computed(() => {
  return loading.value || !prompt.value || prompt.value.trim() === ''
})

// const voiceButtonDisabled = computed(() => {
//   return loading.value
// })

const footerClass = computed(() => {
  let classes = ['p-4']
  if (isMobile.value)
    classes = ['sticky', 'left-0', 'bottom-0', 'right-0', 'p-2', 'pr-3', 'overflow-hidden']
  return classes
})

onMounted(() => {
  scrollToBottom()
})

onUnmounted(() => {
  if (loading.value)
    controller.abort()
})

// const wrapClass = computed(() => {
//   if (isMobile.value)
//     return ['pt-14']
//   return []
// })
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <HeaderComponent
      v-if="isMobile"
      :using-context="usingContext"
      @export="handleExport"
      @toggle-using-context="toggleUsingContext"
    />
    <main class="flex-1 overflow-hidden">
      <div
        id="scrollRef"
        ref="scrollRef"
        class="h-full overflow-hidden overflow-y-auto"
      >
        <div
          id="image-wrapper"
          class="w-full max-w-screen-xl m-auto dark:bg-[#101014]"
          :class="[isMobile ? 'p-2' : 'p-4']"
        >
          <template v-if="!dataSources.length">
            <div class="flex items-center justify-center mt-4 text-center text-neutral-300">
              <SvgIcon icon="ri:bubble-chart-fill" class="mr-2 text-3xl" />
              <span>哼，你别不知道怎么说话吧</span>
            </div>
          </template>
          <template v-else>
            <div>
              <Message
                v-for="(item, index) of shouldDisplayDataSources"
                :key="index"
                :date-time="item.dateTime"
                :text="item.showText"
                :inversion="item.inversion"
                :error="item.error"
                :loading="item.loading"
                :showCandidateWaybill="item.conversationOptions?.showCandidateWaybill"
                @regenerate="onRegenerate(index)"
                @delete="handleDelete(index)"
                @send-order-id="handleSendOrderId"
              />
              <div class="sticky bottom-0 left-0 flex justify-center">
                <NButton v-if="loading" type="warning" @click="handleStop">
                  <template #icon>
                    <SvgIcon icon="ri:stop-circle-line" />
                  </template>
                  Stop Responding
                </NButton>
              </div>
            </div>
          </template>
        </div>
      </div>
    </main>
    <!-- <div class="flex">
      <main class="flex overflow-hidden w-3/4 h-full">
        <div
          id="scrollRef"
          ref="scrollRef"
          class="h-full overflow-hidden overflow-y-auto"
        >
          <div
            id="image-wrapper"
            class="w-full max-w-screen-xl m-auto dark:bg-[#101014]"
            :class="[isMobile ? 'p-2' : 'p-4']"
          >
            <template v-if="!dataSources.length">
              <div class="flex items-center justify-center mt-4 text-center text-neutral-300">
                <SvgIcon icon="ri:bubble-chart-fill" class="mr-2 text-3xl" />
                <span>Aha~</span>
              </div>
            </template>
            <template v-else>
              <div>
                <Message
                  v-for="(item, index) of dataSources"
                  :key="index"
                  :date-time="item.dateTime"
                  :text="item.text"
                  :inversion="item.inversion"
                  :error="item.error"
                  :loading="item.loading"
                  @regenerate="onRegenerate(index)"
                  @delete="handleDelete(index)"
                />
                <div class="sticky bottom-0 left-0 flex justify-center">
                  <NButton v-if="loading" type="warning" @click="handleStop">
                    <template #icon>
                      <SvgIcon icon="ri:stop-circle-line" />
                    </template>
                    Stop Responding
                  </NButton>
                </div>
              </div>
            </template>
          </div>
        </div>
      </main>
      <div class="absolute right-0 w-1/4 h-full">
        <p>system</p>
        <NAutoComplete v-model:value="prompt" :options="searchOptions" :render-label="renderOption">
            <template #default="{ handleInput, handleBlur, handleFocus }">
              <NInput
                class="w-9/10"
                v-model:value="prompt"
                type="textarea"
                :placeholder="placeholder"
                :autosize="{ minRows: 50, maxRows: isMobile ? 25 : 50 }"
                @input="handleInput"
                @focus="handleFocus"
                @blur="handleBlur"
                @keypress="handleEnter"
              />
            </template>
          </NAutoComplete>
      </div>
    </div> -->
    <!-- <footer :class="footerClass"  class="dark:bg-black bg-white absolute bottom-0 z-10 w-full"> -->
    <footer :class="footerClass">
      <div class="w-full max-w-screen-xl m-auto">
        <div class="flex items-center justify-between space-x-2">
          <HoverButton @click="handleClear">
            <span class="text-xl text-[#4f555e] dark:text-white">
              <SvgIcon icon="ri:delete-bin-line" />
            </span>
          </HoverButton>
          <HoverButton v-if="!isMobile" @click="handleExport">
            <span class="text-xl text-[#4f555e] dark:text-white">
              <SvgIcon icon="ri:download-2-line" />
            </span>
          </HoverButton>
          <!-- <HoverButton v-if="!isMobile" @click="toggleUsingContext">
            <span class="text-xl" :class="{ 'text-[#4b9e5f]': usingContext, 'text-[#a8071a]': !usingContext }">
              <SvgIcon icon="ri:chat-history-line" />
            </span>
          </HoverButton> -->
          <NAutoComplete v-model:value="prompt" :options="searchOptions" :render-label="renderOption">
            <template #default="{ handleInput, handleBlur, handleFocus }">
              <NInput
                v-model:value="prompt"
                type="textarea"
                :placeholder="placeholder"
                :autosize="{ minRows: 1, maxRows: isMobile ? 4 : 8 }"
                @input="handleInput"
                @focus="handleFocus"
                @blur="handleBlur"
                @keypress="handleEnter"
              />
            </template>
          </NAutoComplete>
          <!-- <NButton type="primary" :disabled="voiceButtonDisabled">
            <template #icon>
              <span class="dark:text-black">
                <SvgIcon icon="material-symbols:auto-detect-voice" />
              </span>
            </template>
          </NButton> -->
          <NButton type="primary" :disabled="buttonDisabled" @click="handleSubmit">
            <template #icon>
              <span class="dark:text-black">
                <SvgIcon icon="ri:send-plane-fill" />
              </span>
            </template>
          </NButton>
          <NButton type="primary" v-if="chatDataViewerCollapsed" @click="handleButtonHide">
            <span id="btn_switch_hide" class="dark:text-black">立绘</span>
          </NButton>
        </div>
      </div>
    </footer>
  </div>
</template>
