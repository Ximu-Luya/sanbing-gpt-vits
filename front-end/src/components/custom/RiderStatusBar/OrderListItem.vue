<script lang="ts" setup>
import { NPopover, NEllipsis } from 'naive-ui'
interface Props {
  order: any
}
defineProps<Props>()
</script>

<template>
  <NPopover placement="right" trigger="click">
    <template #trigger>
      <div class="order-item">
        <NEllipsis>{{ `${order.sender_name}` }}</NEllipsis>
        {{ `#${order.fetch_id}` }}
      </div>
    </template>

    <div class="order-item-tooltip">
      <div class="tooltip-item" v-for="(value, key) in order">
        {{ `${key}：${value}` }}
      </div>
    </div>
  </NPopover>
</template>

<style>
.order-item {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  border: 1px solid #e5e7eb;
  border-radius: 5px;
  margin-bottom: 5px;
  cursor: pointer;
}

.order-item:hover {
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.08), 0 3px 6px 0 rgba(0, 0, 0, 0.06), 0 5px 12px 4px rgba(0, 0, 0, 0.04);
}

.order-item-tooltip {
  max-height: 400px;
  overflow: auto;
}
</style>