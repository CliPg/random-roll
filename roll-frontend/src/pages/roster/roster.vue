<template>
  <view class="roster-page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-title">
        <text class="title-main">名单管理</text>
        <text class="title-date">{{ currentDate }}</text>
      </view>
      <view class="header-icons">
        <uni-icons type="gear-filled" size="25" @tap="handleSettings" color="#ffffff"></uni-icons>
        <uni-icons type="info-filled" size="25" @tap="handleHelp" color="#ffffff"></uni-icons>
      </view>
    </view>

    <!-- 内容区 -->
    <view class="content-area">
      <view class="list-card">
        <view class="button-group">
          <button class="btn btn-primary" @tap="handleImport">
            <uni-icons type="upload" size="20" color="#ffffff"></uni-icons>
            <text> 导入名单</text>
          </button>
          <button class="btn btn-secondary" @tap="handleExport">
            <uni-icons type="download" size="20"></uni-icons>
            <text>导出</text>
          </button>
          <button class="btn btn-secondary" @tap="handleClear">
            <uni-icons type="trash" size="20"></uni-icons>
            <text>清空</text>
          </button>
        </view>

        <view class="student-lists">
          <view
            v-if="studentLists.length === 0"
            class="empty-state"
          >
            <text>暂无名单，请先导入</text>
          </view>
          <view
            v-for="(list, index) in studentLists"
            :key="index"
            :class="['list-item', { active: selectedListIndex === index }]"
            @tap="handleSelectList(index)"
          >
            <view class="list-info">
              <text class="list-name">{{ list.name }}</text>
              <text class="list-count">{{ list.students.length }}人</text>
            </view>
            <view v-if="selectedListIndex === index" class="list-status">
            </view>
            <uni-icons class="delete-btn" type="close" size="25" @tap.stop="handleDeleteList(index)"></uni-icons>
          </view>
        </view>
      </view>
    </view>

    <!-- 导入对话框 -->
    <ImportModal ref="importModalRef" @success="loadStudentLists" />
    <!-- 设置对话框 -->
    <SettingsModal ref="settingsModalRef" />
    
    <!-- 自定义底部导航栏 -->
    <CustomTabBar />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ImportModal from '@/components/ImportModal.vue'
import SettingsModal from '@/components/SettingsModal.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import { 
  getStudentLists, 
  deleteStudentList, 
  clearAllLists, 
  saveSelectedListIndex, 
  getSelectedListIndex, 
  removeSelectedListIndex,
  saveStudentLists
} from '@/utils/storage'
import { exportStudents, getMyStudentLists } from '@/utils/api'
import type { StudentList } from '@/utils/storage'
import { deleteStudentListOne, deleteStudentListAll } from '@/utils/api'

const currentDate = ref('')
const studentLists = ref<StudentList[]>([])
const importModalRef = ref<InstanceType<typeof ImportModal>>()
const settingsModalRef = ref<InstanceType<typeof SettingsModal>>()
const selectedListIndex = ref<number>(-1)

const formatDate = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const date = String(now.getDate()).padStart(2, '0')
  currentDate.value = `${year}年${month}月${date}日`
}

const syncSelectedIndex = () => {
  if (studentLists.value.length === 0) {
    selectedListIndex.value = -1
    removeSelectedListIndex()
    return
  }

  const storedIndex = getSelectedListIndex()
  if (storedIndex >= 0 && storedIndex < studentLists.value.length) {
    selectedListIndex.value = storedIndex
  } else {
    selectedListIndex.value = 0
    saveSelectedListIndex(0)
  }
}

const loadStudentLists = async () => {
  // Try to load from backend first (current user's lists). Fall back to local storage.
  try {
    const res: any = await getMyStudentLists()
    // API wrapper returns the full response object; support both shapes
    const payload = res?.data ? res : { data: res }
      if (payload && payload.data && Array.isArray(payload.data) && payload.data.length > 0) {
      // Map backend shape {description, students} -> local StudentList { name, students, createTime }
      // Backend returns student objects; convert each student to the local string label format "id·name"
      const lists = payload.data.map((item: any) => ({
        name: item.description,
        students: (item.students || []).map((s: any) => {
          if (typeof s === 'string') return s
          // expected object shape: { student_id, student_name }
          const id = s?.student_id ?? s?.id ?? ''
          const name = s?.student_name ?? s?.name ?? ''
          if (id || name) return `${id}·${name}`.replace(/^·|·$/g, '')
          // fallback to a safe string representation
          try { return JSON.stringify(s) } catch (_) { return String(s) }
        }),
        createTime: Date.now()
      }))
      studentLists.value = lists
      // persist locally
      try { saveStudentLists(lists) } catch (_) {}
      syncSelectedIndex()
      return
    }
  } catch (e) {
    // ignore and fallback to local
    console.warn('Failed to load lists from server', e)
  }

  // Fallback to local storage
  studentLists.value = getStudentLists()
  syncSelectedIndex()
}

const handleImport = () => {
  importModalRef.value?.open()
}

const handleExport = () => {
  // 导出当前选中名单
  const lists = getStudentLists()
  const idx = getSelectedListIndex()
  if (idx < 0 || idx >= lists.length) {
    uni.showToast({ title: '请先选择名单', icon: 'none' })
    return
  }
  const desc = lists[idx].name
  uni.showLoading({ title: '导出中...' })
  exportStudents(desc).then((res) => {
    uni.hideLoading()
    const data = res?.data || []
    if (!Array.isArray(data) || data.length === 0) {
      uni.showToast({ title: '没有数据可导出', icon: 'none' })
      return
    }
    // Convert to CSV
    const headers = ['student_id', 'student_name', 'student_major', 'credits', 'random_rolls', 'description']
    const csvRows = [headers.join(',')]
    data.forEach((row: any) => {
      const vals = headers.map((h) => {
        const v = row[h] ?? ''
        // escape double quotes
        return `"${String(v).replace(/"/g, '""')}"`
      })
      csvRows.push(vals.join(','))
    })
    const csvContent = csvRows.join('\n')

    // For web: create blob and download
    try {
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a: any = document.createElement('a')
      a.href = url
      a.download = `${desc || 'students'}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      uni.showToast({ title: '导出成功', icon: 'success' })
    } catch (e) {
      // Fallback: copy CSV to clipboard (mobile/web may differ)
      try {
        uni.setClipboardData({ data: csvContent })
        uni.showToast({ title: 'CSV 已复制到剪贴板', icon: 'success' })
      } catch (err) {
        uni.showToast({ title: '导出失败', icon: 'none' })
      }
    }
  }).catch((err) => {
    uni.hideLoading()
    uni.showToast({ title: err?.message || '导出失败', icon: 'none' })
  })
}

const handleClear = () => {
  uni.showModal({
    title: '确认清空',
    content: '是否清空所有名单？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteStudentListAll()
          clearAllLists()
          studentLists.value = []
          selectedListIndex.value = -1
          uni.showToast({ title: '已清空', icon: 'success' })
        } catch (error) {
          uni.showToast({ title: '后端清空失败', icon: 'none' })
        }
      }
    }
  })
}

const handleSelectList = (index: number) => {
  if (selectedListIndex.value === index) {
    selectedListIndex.value = -1
    removeSelectedListIndex()
    uni.showToast({ title: '已取消选择', icon: 'none' })
  } else {
    selectedListIndex.value = index
    saveSelectedListIndex(index)
    uni.showToast({ title: `已选择：${studentLists.value[index].name}` , icon: 'none' })
  }
}

const handleDeleteList = (index: number) => {
  uni.showModal({
    title: '确认删除',
    content: `是否删除名单"${studentLists.value[index].name}"？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteStudentListOne(studentLists.value[index].name)
          deleteStudentList(index)
          loadStudentLists()
          uni.showToast({ title: '删除成功', icon: 'success' })
        } catch (error) {
          uni.showToast({ title: '后端删除失败', icon: 'none' })
        }
      }
    }
  })
}

const handleSettings = () => {
  settingsModalRef.value?.open()
}

const handleHelp = () => {
  uni.showModal({
    title: '使用帮助',
    content: '1. 在此页面导入学生名单\n2. 进入"开始点名"进行点名\n3. 在"结果统计"查看记录\n4. 在"积分排行"查看排行'
  })
}

onMounted(() => {
  formatDate()
  loadStudentLists()
})
</script>

<style scoped>
.roster-page {
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

.list-card {
  background-color: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.button-group {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
  flex-wrap: wrap;
}

.btn {
  flex: 1;
  min-width: 150rpx;
  padding: 16rpx 20rpx;
  border: none;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1rpx solid #e5e7eb;
}

.student-lists {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background-color: #f9fafb;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.list-item.active {
  border: 2rpx solid #2563eb;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(37, 99, 235, 0.12));
  box-shadow: 0 8rpx 18rpx rgba(37, 99, 235, 0.12);
}

.list-item.active .list-name {
  color: #1d4ed8;
}

.list-item.active .list-count {
  color: #2563eb;
}

.list-item:active {
  background-color: #f3f4f6;
}

.list-info {
  display: flex;
  flex-direction: column;
}

.list-status {
  display: flex;
  align-items: center;
  margin-right: 4rpx;
}


.list-name {
  font-size: 28rpx;
  font-weight: 500;
  color: #1f2937;
}

.list-count {
  font-size: 24rpx;
  color: #9ca3af;
  margin-top: 4rpx;
}

.delete-btn {
  font-size: 28rpx;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 60rpx 20rpx;
  color: #9ca3af;
  font-size: 28rpx;
}
</style>
