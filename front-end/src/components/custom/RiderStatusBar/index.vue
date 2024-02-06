<script setup lang="ts">
import OrderListItem from './OrderListItem.vue'
import { fetchRiderInfo } from '../../../api'
import { onMounted, computed } from "vue"
import { useUserStore } from '../../../store'
import { useRoute } from 'vue-router'

const userStore = useUserStore()

const route = useRoute()

const userInfo = computed(() => userStore.userInfo)

async function getRiderInfo(rider_id?: number) {
  const { data }: any = await fetchRiderInfo(rider_id)
  
  userStore.updateUserInfo({ riderInfo: data })
}


const rider_id = computed(() => {
  const rider_id = Number(route.query.rider_id)
  return isNaN(rider_id) ? undefined : rider_id
})

onMounted(() => {
  getRiderInfo(rider_id.value)
})
</script>

<template>
  <div class="rider-status-bar">
    <div class="header">状态栏</div>
    <div class="info-box">
      <div class="info-item">
        <label>骑手id：</label>{{ userInfo.riderInfo.rider_id }}
      </div>
      <div class="info-item">
        <label>运力类型：</label>众包
      </div>
    </div>
    <div class="order-list">
      <OrderListItem
        v-for="item in userInfo.riderInfo.wb_list"
        :order="item"
      />
    </div>
  </div>
</template>

<style>
.rider-status-bar {
  display: flex;
  flex-direction: column;
  padding: 10px;
  border-top: 1px solid #e5e7eb;
}

.header {
  text-align: center;
  height: 36px;
  font-size: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid #e5e7eb;
}

.info-box {
  margin-bottom: 5px;
}
.info-box .info-item {
  color: #6B7280;
  margin-bottom: 5px;
}
.info-box .info-item label{
  color: black;
  font-weight: 500;
}

.order-list {
  max-height: 300px;
  overflow: auto;
}
</style>