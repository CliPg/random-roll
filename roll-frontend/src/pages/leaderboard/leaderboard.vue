<template>
  <view class="leaderboard-page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-title">
        <text class="title-main">积分排行</text>
        <text class="title-date">{{ currentDate }}</text>
      </view>
      <view class="header-icons">
        <uni-icons type="gear-filled" size="25" @tap="handleSettings" color="#ffffff"></uni-icons>
        <uni-icons type="info-filled" size="25" @tap="handleHelp" color="#ffffff"></uni-icons>
      </view>
    </view>

    <!-- 内容区 -->
    <view class="content-area">
      <view class="leaderboard-container">
        <view class="controls">
          <view class="selected-list-info">
            <text class="selected-list-name">{{ selectedListName }}</text>
            <view class="list-right">
              <view class="order-toggle-mini">
                <uni-icons class="order-icon" type="up" size="30" :color="order === 0 ? '#2563eb' : '#9ca3af'" @tap="setOrder(0)" />
                <uni-icons class="order-icon" type="down" size="30" :color="order === 1 ? '#2563eb' : '#9ca3af'" @tap="setOrder(1)" />
              </view>
              <text class="selected-list-count">共 {{ selectedListCount }} 人</text>
              <view class="limit-input">
                <text class="limit-label">显示数量</text>
                <input class="limit-field" type="number" :value="String(customLimit)" @input="handleLimitInput" />
              </view>
            </view>
          </view>
        </view>

        <view v-if="displayRanks.length === 0" class="empty-state">
          <text>暂无数据</text>
        </view>

        <view v-else class="bar-list">
          <view v-for="(item, index) in displayRanks" :key="item.student_id + index" class="bar-item">
            <view class="bar-left">
              <text class="student-name">{{ item.student_name }}</text>
              <text class="student-id">{{ item.student_id }}</text>
            </view>
            <view class="bar-right">
              <view class="bar-track">
                <view class="bar-fill" :style="{ width: getBarWidth(item.credits) }"></view>
              </view>
              <view class="bar-meta">
                <text class="credits">{{ item.credits }} 分</text>
                <text class="rolls">随机点名 {{ item.random_rolls }} 次</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 设置对话框 -->
    <SettingsModal ref="settingsModalRef" />
    
    <!-- 自定义底部导航栏 -->
    <CustomTabBar />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import SettingsModal from '@/components/SettingsModal.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import { getPointsRank } from '@/utils/api'
import type { PointsRankItem } from '@/utils/api'
import { getStudentLists, getSelectedListIndex } from '@/utils/storage'

const currentDate = ref('')
const order = ref<0 | 1>(1)
const customLimit = ref(10)
const ranks = ref<PointsRankItem[]>([])
const displayRanks = ref<PointsRankItem[]>([])
const settingsModalRef = ref<InstanceType<typeof SettingsModal>>()
const selectedListName = ref('未选择名单')
const selectedListCount = ref(0)


const formatDate = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const date = String(now.getDate()).padStart(2, '0')
  currentDate.value = `${year}年${month}月${date}日`
}

const loadSelectedListInfo = () => {
  const lists = getStudentLists()
  const selectedIndex = getSelectedListIndex()
  if (selectedIndex >= 0 && selectedIndex < lists.length) {
    const selected = lists[selectedIndex]
    selectedListName.value = selected.name
    selectedListCount.value = selected.students.length
  } else {
    selectedListName.value = '未选择名单'
    selectedListCount.value = 0
  }
}

const parseStudentLabel = (label: any) => {
  // Accept either string labels or student objects returned by backend.
  if (typeof label !== 'string') {
    if (label && typeof label === 'object') {
      const id = String(label.student_id ?? label.id ?? '')
      const name = String(label.student_name ?? label.name ?? '')
      return { id, name }
    }
    label = String(label ?? '')
  }
  const parts = label.split('·')
  const id = parts[0]?.trim() || ''
  const name = parts.slice(1).join('·').trim() || label.trim()
  return { id, name }
}

const filterBySelectedList = (data: PointsRankItem[]): PointsRankItem[] => {
  const lists = getStudentLists()
  const selectedIndex = getSelectedListIndex()
  if (selectedIndex < 0 || selectedIndex >= lists.length) return data
  const selected = lists[selectedIndex]
  const idSet = new Set<string>()
  const nameSet = new Set<string>()
  selected.students.forEach((s) => {
    const { id, name } = parseStudentLabel(s)
    if (id) idSet.add(id)
    if (name) nameSet.add(name)
  })
  return data.filter((it) => idSet.has(it.student_id) || nameSet.has(it.student_name))
}

const refreshDisplay = () => {
  const filtered = filterBySelectedList(ranks.value)
  const sorted = [...filtered].sort((a, b) => {
    return order.value === 0 ? a.credits - b.credits : b.credits - a.credits
  })
  const limit = Number(customLimit.value) || 10
  displayRanks.value = sorted.slice(0, limit)
}

const fetchRanks = async () => {
  try {
    const limit = Number(customLimit.value) || 10
    // determine current selected list description to pass to API
    const lists = getStudentLists()
    const selectedIndex = getSelectedListIndex()
    const description = (selectedIndex >= 0 && selectedIndex < lists.length) ? lists[selectedIndex].name : ''

    const res = await getPointsRank(order.value, limit, description)
    const data = Array.isArray(res?.data) ? res.data : []
    ranks.value = data as PointsRankItem[]
    refreshDisplay()
  } catch (err) {
    refreshDisplay()
  }
}

const setOrder = (newOrder: 0 | 1) => {
  order.value = newOrder
  fetchRanks()
}

const handleLimitInput = (e: any) => {
  const val = Number(e.detail?.value ?? customLimit.value)
  if (!Number.isNaN(val) && val > 0) {
    customLimit.value = val
    fetchRanks()
  }
}

const getBarWidth = (credits: number) => {
  const arr = displayRanks.value
  const max = Math.max(...arr.map((i) => i.credits), 1)
  const pct = Math.round((credits / max) * 100)
  return `${pct}%`
}

const handleSettings = () => {
  settingsModalRef.value?.open()
}

const handleHelp = () => {
  uni.showModal({
    title: '使用帮助',
    content: '展示当前选中名单的积分排行与随机点名次数，支持升序/降序与数量选择。'
  })
}

onMounted(() => {
  formatDate()
  loadSelectedListInfo()
  fetchRanks()
})

onShow(() => {
  loadSelectedListInfo()
  fetchRanks()
})
</script>

<style scoped>
.leaderboard-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 50px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: #2563eb;
  color: white;
  height: 120rpx;
}

.header-title {
  display: flex;
  flex-direction: column;
}

.title-main {
  font-size: 36rpx;
  font-weight: bold;
}

.title-date {
  font-size: 20rpx;
  opacity: 0.8;
}

.header-icons {
  display: flex;
  gap: 20rpx;
  font-size: 32rpx;
}

.icon {
  cursor: pointer;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 20rpx;
}

.leaderboard-container {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.controls {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.selected-list-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-right {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.selected-list-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #1f2937;
}

.selected-list-count {
  font-size: 24rpx;
  color: #6b7280;
}

.control-row {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.order-toggle-mini {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.order-icon {
  display: flex;
  align-items: center;
}

.limit-input {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.limit-label {
  font-size: 24rpx;
  color: #6b7280;
}

.limit-field {
  width: 30rpx;
  padding: 8rpx 12rpx;
  background-color: #f3f4f6;
  border-radius: 10rpx;
  font-size: 22rpx;
  color: #1f2937;
}

.bar-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.bar-item {
  display: flex;
  gap: 16rpx;
  padding: 16rpx;
  background-color: #f9fafb;
  border-radius: 12rpx;
}

.bar-left {
  width: 30%;
  display: flex;
  flex-direction: column;
}

.student-name {
  font-size: 28rpx;
  color: #1f2937;
  font-weight: 500;
}

.student-id {
  font-size: 22rpx;
  color: #6b7280;
  margin-top: 6rpx;
}

.bar-right {
  width: 70%;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.bar-track {
  width: 100%;
  height: 28rpx;
  background-color: #e5e7eb;
  border-radius: 14rpx;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #9333ea);
}

.bar-meta {
  display: flex;
  justify-content: space-between;
  font-size: 24rpx;
  color: #374151;
}

.credits {
  font-weight: 600;
}

.rolls {
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 60rpx 20rpx;
  color: #9ca3af;
  font-size: 28rpx;
}
</style>
