<template>
  <view class="statistics-page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-title">
        <text class="title-main">结果统计</text>
        <text class="title-date">{{ currentDate }}</text>
      </view>
      <view class="header-icons">
        <uni-icons type="gear-filled" size="25" @tap="handleSettings" color="#ffffff"></uni-icons>
        <uni-icons type="info-filled" size="25" @tap="handleHelp" color="#ffffff"></uni-icons>
      </view>
    </view>

    <!-- 内容区 -->
    <view class="content-area">
      <view class="statistics-card">
        <text class="card-title">今日记录</text>
        <view class="records-list">
          <view v-if="callRecords.length === 0" class="empty-state">
            <text>暂无记录</text>
          </view>
          <view v-for="(record, index) in callRecords" :key="index" class="record-item">
            <view class="record-left">
              <text class="record-time">{{ record.time }}</text>
              <text class="record-student">{{ record.student }}</text>
              <text class="record-meta">{{ record.repeatText }} · {{ record.answerScoreText }}</text>
            </view>
            <view class="record-right">
              <text class="badge" :class="record.statusClass">{{ record.status }}</text>
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
import { getCallRecords } from '@/utils/storage'

interface CallRecord {
  time: string
  student: string
  status: string
  statusClass: string
  repeatText: string
  answerScoreText: string
}

const currentDate = ref('')
const callRecords = ref<CallRecord[]>([])
const settingsModalRef = ref<InstanceType<typeof SettingsModal>>()

const formatDate = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const date = String(now.getDate()).padStart(2, '0')
  currentDate.value = `${year}年${month}月${date}日`
}

const loadCallRecords = () => {
  const records = getCallRecords()
  callRecords.value = records.map((record: any) => {
    const repeatText =
      typeof record?.repeatText === 'string'
        ? record.repeatText
        : typeof record?.isRepeat === 'boolean'
          ? record.isRepeat ? '能重复问题' : '不能重复问题'
          : '未记录'

    const scoreValue =
      typeof record?.answerScore === 'number'
        ? record.answerScore
        : typeof record?.answer_condition === 'number'
          ? record.answer_condition
          : typeof record?.score === 'number'
            ? record.score
            : null

    return {
      time: record?.time || '--:--',
      student: record?.student || '未知学生',
      status: record?.status || '未记录',
      statusClass: record?.statusClass || 'badge-yellow',
      repeatText,
      answerScoreText: scoreValue !== null ? `${scoreValue}分` : '未评分'
    }
  })
}

const handleSettings = () => {
  settingsModalRef.value?.open()
}

const handleHelp = () => {
  uni.showModal({
    title: '使用帮助',
    content: '本页面显示所有点名记录。每次点名都会自动记录时间和学生信息。'
  })
}

onMounted(() => {
  formatDate()
  loadCallRecords()
})

onShow(() => {
  loadCallRecords()
})
</script>

<style scoped>
.statistics-page {
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

.statistics-card {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 20rpx;
  display: block;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx;
  background-color: #f9fafb;
  border-radius: 12rpx;
}

.record-left {
  display: flex;
  flex-direction: column;
}

.record-time {
  font-size: 24rpx;
  color: #9ca3af;
}

.record-student {
  font-size: 28rpx;
  color: #1f2937;
  margin-top: 4rpx;
}

.record-meta {
  font-size: 24rpx;
  color: #6b7280;
  margin-top: 6rpx;
}

.record-right {
  display: flex;
  gap: 12rpx;
}

.badge {
  padding: 10rpx 16rpx;
  border-radius: 22rpx;
  font-size: 26rpx;
  font-weight: 500;
}

.badge-red {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-yellow {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-green {
  background-color: #dcfce7;
  color: #15803d;
}

.empty-state {
  text-align: center;
  padding: 60rpx 20rpx;
  color: #9ca3af;
  font-size: 28rpx;
}
</style>
