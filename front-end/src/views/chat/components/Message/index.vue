<script setup lang='ts'>
import { ref, computed } from 'vue'
import { NDropdown, NEllipsis } from 'naive-ui'
import AvatarComponent from './Avatar.vue'
import TextComponent from './Text.vue'
import { SvgIcon } from '@/components/common'
import { copyText } from '@/utils/format'
import { useIconRender } from '@/hooks/useIconRender'
import { t } from '@/locales'
import { useUserStore } from '@/store'

interface Props {
  dateTime?: string
  text?: string
  inversion?: boolean
  error?: boolean
  loading?: boolean
  showCandidateWaybill?: 0 | 1
}

interface Emit {
  (ev: 'regenerate'): void
  (ev: 'delete'): void
  (ev: 'sendOrderId', orderId: string): void
}

const props = defineProps<Props>()

const emit = defineEmits<Emit>()

const { iconRender } = useIconRender()

const textRef = ref<HTMLElement>()

const options = [
  {
    label: t('chat.copy'),
    key: 'copyText',
    icon: iconRender({ icon: 'ri:file-copy-2-line' }),
  },
  {
    label: t('common.delete'),
    key: 'delete',
    icon: iconRender({ icon: 'ri:delete-bin-line' }),
  },
]

function handleSelect(key: 'copyRaw' | 'copyText' | 'delete') {
  switch (key) {
    case 'copyText':
      copyText({ text: props.text ?? '' })
      return
    case 'delete':
      emit('delete')
  }
}

function handleRegenerate() {
  emit('regenerate')
}

const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)

function handleSendOrderId(orderId: string) {
  emit("sendOrderId", orderId)
}
</script>

<template>
  <div class="flex w-full mb-6 overflow-hidden" :class="[{ 'flex-row-reverse': inversion }]">
    <div
      class="flex items-center justify-center flex-shrink-0 h-8 overflow-hidden rounded-full basis-8"
      :class="[inversion ? 'ml-2' : 'mr-2']"
    >
      <AvatarComponent :image="inversion" />
    </div>
    <div class="overflow-hidden text-sm " :class="[inversion ? 'items-end' : 'items-start']">
      <p class="text-xs text-[#b4bbc4]" :class="[inversion ? 'text-right' : 'text-left']">
        {{ dateTime }}
      </p>
      <div
        class="flex items-end gap-1 mt-2"
        :class="[inversion ? 'flex-row-reverse' : 'flex-row']"
      >
        <TextComponent
          ref="textRef"
          :inversion="inversion"
          :error="error"
          :text="text"
          :loading="loading"
        />
        <div class="flex flex-col">
          <button
            v-if="!inversion"
            class="mb-2 transition text-neutral-300 hover:text-neutral-800 dark:hover:text-neutral-300"
            @click="handleRegenerate"
          >
            <SvgIcon icon="ri:restart-line" />
          </button>
          <NDropdown :placement="!inversion ? 'right' : 'left'" :options="options" @select="handleSelect">
            <button class="transition text-neutral-300 hover:text-neutral-800 dark:hover:text-neutral-200">
              <SvgIcon icon="ri:more-2-fill" />
            </button>
          </NDropdown>
        </div>
      </div>

      <div v-if="showCandidateWaybill === 1 && !inversion" class="candidate-waybill">
        <div
          v-for="item in userInfo.riderInfo.wb_list"
          class="waybill-item"
          @click="handleSendOrderId(`${item.sender_name}#${item.fetch_id}`)"
        >
          <div class="title">
            <NEllipsis>{{ `${item.sender_name}` }}</NEllipsis>
            {{ `#${item.fetch_id}` }}
          </div>
          <NEllipsis class="info-item">
            <label>餐品：</label>{{ "汉堡" }}
          </NEllipsis>
          <NEllipsis class="info-item">
            <label>配送地址：</label>{{ item.recipient_address }}
          </NEllipsis>
          <NEllipsis class="info-item">
            <label>用户尾号：</label>{{ item.recipient_phone.slice(-4) }}
          </NEllipsis>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.candidate-waybill {
  display: flex;
  height: 140px;
  max-width: 600px;
  overflow: auto;
  padding: 10px 0;
}

.waybill-item {
  cursor: pointer;
  width: 200px;
  flex-shrink: 0;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 5px;
  margin-left: 5px;
}

.waybill-item:hover {
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.08), 0 3px 6px 0 rgba(0, 0, 0, 0.06), 0 5px 12px 4px rgba(0, 0, 0, 0.04);
}

.waybill-item .title {
  font-size: 16px;
  font-weight: 500;
  display: flex;
  margin-bottom: 5px;
}
</style>