<script setup lang='ts'>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { NAutoComplete, NButton, NInput, useDialog, useMessage } from 'naive-ui'
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
import { fetchChatAPIProcess } from '@/api'
import { t } from '@/locales'

let controller = new AbortController()

const openLongReply = import.meta.env.VITE_GLOB_OPEN_LONG_REPLY === 'true'

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
function handleButtonHide(event: MouseEvent){
  isHidden.value = !isHidden.value
  scrollToBottom()
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

async function onUpdateReply(message: string) {
  loading.value = true
  prompt.value = ''

  // const systemMessage = "你是一个美团客服，要处理骑手配送中遇到的问题。\n\n如果骑手遇到的问题是”顾客拒收“，处理流程如下：\n1. 建议先到达顾客位置，在顾客位置处上报”顾客拒收“\n2. 上报完成后需要将餐品保持完好并返还给商家，返还后在APP上提交返餐证明（您和店铺门头的合照，小票照片）\n3. 返餐完成后取消订单\n4. 如果出现违规，系统会自动申诉，如果申诉不通过，可以手动发起二次申诉，结果以二次申诉为准，申诉通过后会消除违规并返还配送费\n如何上报？\n1. 进入您想上报的订单的【详情页】（有订单轨迹和地图的页面）\n2. 点击左下角【遇到问题】>【顾客拒收】 ，按照页面指引提交证据后点击【确认上报】\n3. 上报完成后，请将餐品返还给商家，并上传返餐凭证，返餐完成后，您就可以在【订单详情页】取消订单了\n如何发起申诉？\n1. 进入骑手APP侧边栏，点击上方的【违规申诉】，你也可以【点击此处】快速进入违规申诉列表\n2. 找到你想申诉的罚单，点击【申诉】按钮，选择【顾客拒绝收货】申诉，提交上报证据后点击【确认申诉】\n3. 如果申诉通过，系统会为您消除违规并返还扣款，您耐心等待申诉结果即可。\n申诉小技巧：如果您有与顾客的聊天记录、返餐等证据，请在申诉时一并上传，会提高你的申诉成功率。\n其他信息：\n1. 顾客拒收不会影响派单率\n2. 其他订单不能申诉\n3. 不可以直接取消订单，需要在上报”顾客拒收“并返餐后取消订单，如果直接取消，可能会产生”骑手取消订单“违规\n\n\n\n你的对象是骑手，你需要知道骑手订单号，是否到达用户位置，是否已经上报，是否已经申诉。当上述信息不完整的时候，需要先确认缺失的信息。信息不全的时候或不正确的时候，不要给出解决方案，当收集到足够的信息再回复解决方案。每次只问用户一个问题，当用户正确回答后再问下一个问题。如果遇到骑手询问不相干的事情，请告知骑手不处理无关问题，不要做任何建议并友善结束对话"
  
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
    let lastText = ''
    const fetchChatAPIOnce = async () => {
      await fetchChatAPIProcess<Chat.ConversationResponse>({
        prompt: message,
        options,
        signal: controller.signal,
        onDownloadProgress: ({ event }) => {
          const xhr = event.target
          const { responseText } = xhr
          // Always process the final line
          const lastIndex = responseText.lastIndexOf('\n')
          let chunk = responseText
          if (lastIndex !== -1)
            chunk = responseText.substring(lastIndex)
          try {
            const data = JSON.parse(chunk)
            updateChat(
              +uuid,
              dataSources.value.length - 1,
              {
                dateTime: new Date().toLocaleString(),
                text: lastText + data.text ?? '',
                inversion: false,
                error: false,
                loading: false,
                conversationOptions: { 
                  conversationId: data.conversationId, 
                  parentMessageId: data.id, 
                  conversationStage: data.conversationStage,
                  showCandidateWaybill: data.showCandidateWaybill,
                  provideStatus: data.provideStatus,
                  waybill: data.waybill,
                },
                requestOptions: { prompt: message, options: { ...options } },
              },
            )

            // TODO： 这里的updateChatSome未生效，可以讨论一下
            // console.log('用户',conversationList.value[conversationList.value.length - 2]?.conversationOptions?.wrappedPrompt)
            updateChatSome(
              +uuid,
              dataSources.value.length - 2,
              {
                conversationOptions: { 
                  wrappedPrompt: data.wrappedPrompt
                },
              },
            )
            // console.log('用户',conversationList.value[conversationList.value.length - 2]?.conversationOptions?.wrappedPrompt)
            // console.log(data.wrappedPrompt)

            if (openLongReply && data.detail.choices[0].finish_reason === 'length') {
              options.parentMessageId = data.id
              lastText = data.text
              message = ''
              return fetchChatAPIOnce()
            }

            scrollToBottom()
          }
          catch (error) {
          //
          }
        },
      })
    }

    appStore.setChatDataLoading(true)
    await fetchChatAPIOnce()
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
    let lastText = ''
    const fetchChatAPIOnce = async () => {
      await fetchChatAPIProcess<Chat.ConversationResponse>({
        prompt: message,
        options,
        signal: controller.signal,
        onDownloadProgress: ({ event }) => {
          const xhr = event.target
          const { responseText } = xhr
          // Always process the final line
          const lastIndex = responseText.lastIndexOf('\n')
          let chunk = responseText
          if (lastIndex !== -1)
            chunk = responseText.substring(lastIndex)
          try {
            const data = JSON.parse(chunk)
            updateChat(
              +uuid,
              index,
              {
                dateTime: new Date().toLocaleString(),
                text: lastText + data.text ?? '',
                inversion: false,
                error: false,
                loading: false,
                conversationOptions: { 
                  conversationId: data.conversationId, 
                  parentMessageId: data.id, 
                  conversationStage: data.conversationStage,
                  showCandidateWaybill: data.showCandidateWaybill,
                  provideStatus: data.provideStatus,
                  waybill: data.waybill,
                },
                requestOptions: { prompt: message, options: { ...options } },
              },
            )

            updateChatSome(
              +uuid,
              index-1,
              {
                conversationOptions: { 
                  wrappedPrompt: data.wrappedPrompt
                },
              },
            )

            if (openLongReply && data.detail.choices[0].finish_reason === 'length') {
              options.parentMessageId = data.id
              lastText = data.text
              message = ''
              return fetchChatAPIOnce()
            }
          }
          catch (error) {
            //
          }
        },
      })
    }
    appStore.setChatDataLoading(true)
    await fetchChatAPIOnce()
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

const voiceButtonDisabled = computed(() => {
  return loading.value
})

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
              <span>Aha~</span>
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
          <HoverButton v-if="!isMobile" @click="toggleUsingContext">
            <span class="text-xl" :class="{ 'text-[#4b9e5f]': usingContext, 'text-[#a8071a]': !usingContext }">
              <SvgIcon icon="ri:chat-history-line" />
            </span>
          </HoverButton>
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
          <NButton type="primary" :disabled="voiceButtonDisabled">
            <template #icon>
              <span class="dark:text-black">
                <SvgIcon icon="material-symbols:auto-detect-voice" />
              </span>
            </template>
          </NButton>
          <NButton type="primary" :disabled="buttonDisabled" @click="handleSubmit">
            <template #icon>
              <span class="dark:text-black">
                <SvgIcon icon="ri:send-plane-fill" />
              </span>
            </template>
          </NButton>
          <NButton type="primary" :disabled="loading" @click="handleButtonHide">
                <span id="btn_switch_hide" class="dark:text-black">
                  {{isHidden ? "显示" : "隐藏"}}
                </span>
          </NButton>
        </div>
      </div>
    </footer>
  </div>
</template>
