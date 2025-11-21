<template>
  <view class="rollcall-page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-title">
        <text class="title-main">开始点名</text>
        <text class="title-date">{{ currentDate }}</text>
      </view>
      <view class="header-icons">
        <uni-icons type="gear-filled" size="25" @tap="handleSettings" color="#ffffff"></uni-icons>
        <uni-icons type="info-filled" size="25" @tap="handleHelp" color="#ffffff"></uni-icons>
      </view>
    </view>

    <!-- 内容区 -->
    <view class="content-area">
      <view class="rollcall-container">
        <view class="selected-list-banner" @tap="navigateToRoster">
          <view class="banner-info">
            <text class="banner-title">{{ selectedListName }}</text>
            <text class="banner-subtitle">
              {{ selectedListCount > 0 ? `共 ${selectedListCount} 人` : '请在名单管理页面选择名单' }}
            </text>
          </view>
          <view class="banner-action">
            <text>选择名单</text>
            <uni-icons type="arrowright" size="20" color="#2563eb"></uni-icons>
          </view>
        </view>

        <view class="student-display">
          <text class="student-name" :class="{ 'rotate': isRolling }">
            {{ currentStudent }}
          </text>
        </view>

        <view class="mode-buttons">
          <button
            class="mode-btn"
            :class="{ active: rollMode === 'random' }"
            @tap="rollMode = 'random'"
          >
            随机点名
          </button>
          <button
            class="mode-btn"
            :class="{ active: rollMode === 'order' }"
            @tap="rollMode = 'order'"
          >
            顺序点名
          </button>
        </view>

        <button
          class="start-btn"
          :class="{ 'rolling': isRolling }"
          @tap="toggleRolling"
        >
          {{ isRolling ? '停止点名' : '开始点名' }}
        </button>

        <view class="interval-info">
          <text>⏱️ 间隔：{{ interval }}ms</text>
        </view>

        <view class="record-preview" v-if="lastCalled">
          <text class="record-title">最后点名：</text>
          <text class="record-name">{{ lastCalled }}</text>
        </view>
      </view>
    </view>

    <view v-if="showResultForm" class="result-modal">
      <view class="result-modal__overlay" @tap="handleResultCancel"></view>
      <view class="result-modal__container">
        <view class="result-modal__header">
          <text class="result-modal__title">记录点名结果</text>
          <text class="result-modal__close" @tap="handleResultCancel">✕</text>
        </view>

        <view class="result-form">
          <view class="result-form__item">
            <text class="result-form__label">学生</text>
            <text class="result-form__student">{{ selectedStudentInfo.display }}</text>
          </view>

          <view class="result-form__item">
            <text class="result-form__label">是否到达课堂</text>
            <switch :checked="resultForm.isAttend" @change="handleAttendChange" />
          </view>

          <view class="result-form__item" v-if="resultForm.isAttend">
            <text class="result-form__label">能否重复问题</text>
            <switch :checked="resultForm.isRepeat" @change="handleRepeatChange" />
          </view>

          <view class="result-form__item" v-if="resultForm.isAttend && resultForm.isRepeat">
            <text class="result-form__label">回答评分</text>
            <picker
              class="result-form__picker"
              mode="selector"
              :range="scoreOptionTexts"
              :value="resultForm.scoreIndex"
              @change="handleScoreChange"
            >
              <view class="result-form__picker-display">
                <text>{{ scoreOptionTexts[resultForm.scoreIndex] }}</text>
                <uni-icons type="arrowdown" size="20" color="#6b7280" />
              </view>
            </picker>
          </view>
        </view>

        <view class="result-modal__actions">
          <button class="result-modal__btn result-modal__btn--cancel" @tap="handleResultCancel">
            取消
          </button>
          <button
            class="result-modal__btn result-modal__btn--confirm"
            :disabled="submittingResult"
            @tap="handleResultSubmit"
          >
            {{ submittingResult ? '提交中...' : '确认提交' }}
          </button>
        </view>
      </view>
    </view>

    <!-- 设置对话框 -->
    <SettingsModal ref="settingsModalRef" @update="handleSettingsUpdate" />
    
    <!-- 自定义底部导航栏 -->
    <CustomTabBar />
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import SettingsModal from '@/components/SettingsModal.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import { getStudentLists, saveCallRecord, getSettings, getSelectedListIndex } from '@/utils/storage'
import { submitRollResult } from '@/utils/api'

const currentDate = ref('')
const currentStudent = ref('点击开始')
const isRolling = ref(false)
const rollMode = ref<'random' | 'order'>('random')
const lastCalled = ref('')
const interval = ref(300)
const settingsModalRef = ref<InstanceType<typeof SettingsModal>>()
const selectedListName = ref('当前未选择名单')
const selectedListCount = ref(0)

const showResultForm = ref(false)
const submittingResult = ref(false)
const scoreOptions = [0.5, 1, 1.5, 2, 2.5, 3]
const scoreOptionTexts = scoreOptions.map((score) => `${score}分`)
const resultForm = reactive({
  isAttend: true,
  isRepeat: true,
  scoreIndex: scoreOptions.length - 1
})
const selectedStudentInfo = reactive({
  id: '',
  name: '',
  display: ''
})

let rollInterval: ReturnType<typeof setInterval> | null = null
let currentIndex = 0

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
    const selectedList = lists[selectedIndex]
    selectedListName.value = selectedList.name
    selectedListCount.value = selectedList.students.length
  } else if (lists.length > 0) {
    selectedListName.value = '未选择名单'
    selectedListCount.value = 0
  } else {
    selectedListName.value = '暂无名单'
    selectedListCount.value = 0
  }
}

const resetResultForm = () => {
  resultForm.isAttend = true
  resultForm.isRepeat = true
  resultForm.scoreIndex = scoreOptions.length - 1
}

const parseStudentInfo = (studentLabel: any) => {
  // Defensive parsing: accept either a string label like "id·name" or an object { student_id, student_name }
  if (typeof studentLabel !== 'string') {
    if (studentLabel && typeof studentLabel === 'object') {
      const id = studentLabel.student_id ?? studentLabel.id ?? ''
      const name = studentLabel.student_name ?? studentLabel.name ?? ''
      const display = id || name ? `${id} · ${name}`.trim() : JSON.stringify(studentLabel)
      return { id: String(id || ''), name: String(name || ''), display }
    }
    // fallback
    studentLabel = String(studentLabel ?? '')
  }

  const parts = studentLabel.split('·')
  if (parts.length >= 2) {
    const id = parts[0].trim()
    const name = parts.slice(1).join('·').trim()
    return {
      id,
      name,
      display: `${id} · ${name}`
    }
  }
  const name = studentLabel.trim()
  return {
    id: '',
    name,
    display: name
  }
}

const openResultForm = (studentLabel: string) => {
  const parsed = parseStudentInfo(studentLabel)
  selectedStudentInfo.id = parsed.id
  selectedStudentInfo.name = parsed.name
  selectedStudentInfo.display = parsed.display
  resetResultForm()
  showResultForm.value = true
}

const toggleRolling = () => {
  const studentLists = getStudentLists()
  const selectedIndex = getSelectedListIndex()
  
  if (!isRolling.value) {
    // 开始点名
    if (studentLists.length === 0) {
      uni.showToast({ title: '请先导入名单', icon: 'none' })
      return
    }

    if (selectedIndex < 0 || selectedIndex >= studentLists.length) {
      uni.showToast({ title: '请在名单管理页面选择名单', icon: 'none' })
      return
    }

    const selectedList = studentLists[selectedIndex]
    if (!selectedList.students || selectedList.students.length === 0) {
      uni.showToast({ title: '选择的名单没有学生', icon: 'none' })
      return
    }

    loadSelectedListInfo()
    isRolling.value = true
    const students = selectedList.students

    if (rollMode.value === 'random') {
      rollInterval = setInterval(() => {
        const randomIndex = Math.floor(Math.random() * students.length)
        currentStudent.value = students[randomIndex]
      }, interval.value)
    } else {
      currentIndex = 0
      rollInterval = setInterval(() => {
        currentStudent.value = students[currentIndex % students.length]
        currentIndex++
      }, interval.value)
    }
  } else {
    // 停止点名
    isRolling.value = false
    if (rollInterval) {
      clearInterval(rollInterval)
      rollInterval = null
    }

    if (!currentStudent.value || currentStudent.value === '点击开始') {
      uni.showToast({ title: '暂无学生可记录', icon: 'none' })
      return
    }

    lastCalled.value = currentStudent.value
    openResultForm(currentStudent.value)
  }
}

const handleAttendChange = (event: any) => {
  resultForm.isAttend = !!event.detail.value
  if (!resultForm.isAttend) {
    resultForm.isRepeat = false
  }
}

const handleRepeatChange = (event: any) => {
  resultForm.isRepeat = !!event.detail.value
}

const handleScoreChange = (event: any) => {
  const index = Number(event.detail?.value ?? resultForm.scoreIndex)
  if (!Number.isNaN(index) && index >= 0 && index < scoreOptions.length) {
    resultForm.scoreIndex = index
  }
}

const handleResultCancel = () => {
  showResultForm.value = false
}

const handleResultSubmit = async () => {
  if (!selectedStudentInfo.display) {
    uni.showToast({ title: '学生信息缺失', icon: 'none' })
    return
  }

  const score = resultForm.isAttend && resultForm.isRepeat ? scoreOptions[resultForm.scoreIndex] : null
  // attach the currently selected list's name as the description (class identifier)
  const studentLists = getStudentLists()
  const selectedIndex = getSelectedListIndex()
  const currentDescription = (selectedIndex >= 0 && selectedIndex < studentLists.length) ? studentLists[selectedIndex].name : selectedListName.value

  const payload = {
    student_id: selectedStudentInfo.id || selectedStudentInfo.name,
    description: currentDescription,
    is_attend: resultForm.isAttend,
    is_repeat: resultForm.isRepeat,
    answer_condition: score
  }

  submittingResult.value = true
  const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  const record = {
    time,
    student: selectedStudentInfo.display,
    status: resultForm.isAttend ? '到课' : '缺课',
    statusClass: resultForm.isAttend ? 'badge-green' : 'badge-red',
    repeatText: resultForm.isAttend ? (resultForm.isRepeat ? '能重复问题' : '不能重复问题') : '未记录',
    answerScore: score
  }
  saveCallRecord(record)
  try {
    await submitRollResult({
      ...payload,
      answer_condition: payload.answer_condition ?? 0
    })
  } catch (error) {
    console.error('提交点名结果失败:', error)
  } finally {
    uni.showToast({ title: '已记录', icon: 'success' })
    showResultForm.value = false
    submittingResult.value = false
  }
}

const handleSettings = () => {
  settingsModalRef.value?.open()
}

const handleSettingsUpdate = (newSettings: any) => {
  interval.value = newSettings.interval
}

const handleHelp = () => {
  uni.showModal({
    title: '使用帮助',
    content: '1. 选择点名模式（随机/顺序）\n2. 点击开始点名\n3. 点击停止点名结束\n4. 系统自动记录点名结果'
  })
}

const navigateToRoster = () => {
  uni.switchTab({
    url: '/pages/roster/roster'
  })
}

onMounted(() => {
  formatDate()
  const settings = getSettings()
  interval.value = settings.interval
  loadSelectedListInfo()
})

onShow(() => {
  loadSelectedListInfo()
})

onUnmounted(() => {
  if (rollInterval) {
    clearInterval(rollInterval)
    rollInterval = null
  }
})
</script>


<style scoped>
.rollcall-page {
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

.rollcall-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30rpx 20rpx;
}

.selected-list-banner {
  width: 100%;
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 20rpx;
  margin-bottom: 24rpx;
  border: 2rpx solid rgba(37, 99, 235, 0.2);
  box-shadow: 0 6rpx 16rpx rgba(37, 99, 235, 0.12);
  transition: transform 0.2s ease;
}

.selected-list-banner:active {
  transform: scale(0.98);
}

.banner-left {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 70rpx;
  height: 70rpx;
  border-radius: 50%;
  background-color: rgba(37, 99, 235, 0.12);
  margin-right: 20rpx;
}

.banner-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.banner-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
}

.banner-subtitle {
  font-size: 24rpx;
  color: #6b7280;
}

.banner-action {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #2563eb;
  font-weight: 500;
}

.student-display {
  width: 100%;
  background: linear-gradient(135deg, #3b82f6 0%, #9333ea 100%);
  border-radius: 30rpx;
  padding: 80rpx 40rpx;
  text-align: center;
  margin-bottom: 40rpx;
  box-shadow: 0 10rpx 30rpx rgba(59, 130, 246, 0.3);
}

.student-name {
  font-size: 80rpx;
  font-weight: bold;
  color: white;
  display: block;
  word-break: break-all;
}

@keyframes rotate {
  0% {
    transform: rotateY(0deg);
  }
  50% {
    transform: rotateY(180deg);
  }
  100% {
    transform: rotateY(360deg);
  }
}

.student-name.rotate {
  animation: rotate 0.1s ease-in-out;
}

.mode-buttons {
  display: flex;
  gap: 20rpx;
  margin-bottom: 40rpx;
  width: 100%;
}

.mode-btn {
  flex: 1;
  padding: 16rpx 20rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 20rpx;
  background-color: white;
  color: #6b7280;
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.3s ease;
}

.mode-btn.active {
  background-color: #dbeafe;
  color: #2563eb;
  border-color: #2563eb;
}

.start-btn {
  width: 200rpx;
  padding: 20rpx 40rpx;
  background-color: #f97316;
  color: white;
  border: none;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 40rpx;
  animation: pulse 2s infinite;
}

.start-btn.rolling {
  background-color: #ef4444;
  animation: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.interval-info {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 26rpx;
  color: #6b7280;
  margin-bottom: 30rpx;
}

.record-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #f0fdf4;
  border-left: 4rpx solid #22c55e;
  border-radius: 12rpx;
  padding: 20rpx;
  width: 100%;
  margin-top: 30rpx;
}

.record-title {
  font-size: 24rpx;
  color: #6b7280;
}

.record-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #22c55e;
  margin-top: 8rpx;
}

.result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 2000;
}

.result-modal__overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.result-modal__container {
  position: relative;
  width: 100%;
  max-height: 80vh;
  background-color: #ffffff;
  border-radius: 24rpx 24rpx 0 0;
  padding: 30rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.result-modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-modal__title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1f2937;
}

.result-modal__close {
  font-size: 32rpx;
  color: #9ca3af;
}

.result-form {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.result-form__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24rpx;
}

.result-form__label {
  font-size: 28rpx;
  color: #374151;
  font-weight: 500;
}

.result-form__student {
  font-size: 28rpx;
  color: #2563eb;
  font-weight: 600;
}

.result-form__picker {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.result-form__picker-display {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 12rpx 20rpx;
  border-radius: 16rpx;
  background-color: #f3f4f6;
  font-size: 26rpx;
  color: #1f2937;
}

.result-modal__actions {
  display: flex;
  gap: 16rpx;
}

.result-modal__btn {
  flex: 1;
  padding: 16rpx 24rpx;
  border-radius: 16rpx;
  border: none;
  font-size: 28rpx;
  font-weight: 600;
  transition: all 0.2s ease;
}

.result-modal__btn--cancel {
  background-color: #f3f4f6;
  color: #374151;
}

.result-modal__btn--confirm {
  background: linear-gradient(135deg, #2563eb, #9333ea);
  color: #ffffff;
}

.result-modal__btn--confirm:disabled {
  opacity: 0.6;
}
</style>
