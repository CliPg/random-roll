<template>
  <view v-if="show" class="import-modal">
    <view class="modal-overlay" @tap="close"></view>
    <view class="modal-content">
      <view class="modal-header">
        <text class="modal-title">导入学生名单</text>
        <text class="close-btn" @tap="close">✕</text>
      </view>

      <view class="modal-body">
        <!-- 导入方式选择 -->
        <view class="import-type-tabs">
          <view 
            class="tab-item" 
            :class="{ active: importType === 'excel' }"
            @tap="importType = 'excel'"
          >
            <uni-icons type="file" size="18" :color="importType === 'excel' ? '#2563eb' : '#9ca3af'"></uni-icons>
            <text>Excel 导入</text>
          </view>
          <view 
            class="tab-item" 
            :class="{ active: importType === 'text' }"
            @tap="importType = 'text'"
          >
            <uni-icons type="compose" size="18" :color="importType === 'text' ? '#2563eb' : '#9ca3af'"></uni-icons>
            <text>文本导入</text>
          </view>
        </view>

        <!-- Excel 导入 -->
        <view v-if="importType === 'excel'" class="input-group">
          <text class="label">名单名称</text>
          <input
            v-model="formData.name"
            class="input-field"
            type="text"
            placeholder="例如：2025级操作系统"
            maxlength="50"
          />
        </view>

        <view v-if="importType === 'excel'" class="input-group">
          <text class="label">选择 Excel 文件</text>
          <view class="hint-text">Excel 文件需包含：学号、姓名、专业三列</view>
          <button class="btn-select-file" @tap="handleSelectFile">
            <uni-icons type="folder-add" size="20" color="#2563eb"></uni-icons>
            <text>{{ selectedFileName || '点击选择 Excel 文件' }}</text>
          </button>
          <view v-if="excelPreview.length > 0" class="excel-preview">
            <text class="preview-title">预览数据（前5条）：</text>
            <view class="preview-table">
              <view class="preview-row preview-header">
                <text class="preview-cell">学号</text>
                <text class="preview-cell">姓名</text>
                <text class="preview-cell">专业</text>
              </view>
              <view 
                v-for="(row, index) in excelPreview.slice(0, 5)" 
                :key="index" 
                class="preview-row"
              >
                <text class="preview-cell">{{ row.student_id || '-' }}</text>
                <text class="preview-cell">{{ row.student_name || '-' }}</text>
                <text class="preview-cell">{{ row.student_major || '-' }}</text>
              </view>
            </view>
            <text class="preview-count">共 {{ excelPreview.length }} 条数据</text>
          </view>
        </view>

        <!-- 文本导入 -->
        <template v-if="importType === 'text'">
          <view class="input-group">
            <text class="label">名单名称</text>
            <input
              v-model="formData.name"
              class="input-field"
              type="text"
              placeholder="例如：2025级操作系统"
              maxlength="50"
            />
          </view>

          <view class="input-group">
            <text class="label">学生名单</text>
            <view class="hint-text">每行输入一个学生名字（如：小明）</view>
            <textarea
              v-model="formData.students"
              class="textarea-field"
              placeholder=""
              maxlength="2000"
            />
          </view>
        </template>

        <view class="tips">
          <text v-if="importType === 'excel'">💡 提示：Excel 文件第一行应为表头（学号、姓名、专业），支持 .xlsx 和 .xls 格式</text>
          <text v-else>💡 提示：请按照每行一个名字的格式输入</text>
        </view>
      </view>

      <view class="modal-footer">
        <button class="btn-cancel" @tap="close">取消</button>
        <button class="btn-confirm" @tap="handleImport" :disabled="isImporting">
          {{ isImporting ? '导入中...' : '确认导入' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import * as XLSX from 'xlsx'
import { addStudentList } from '@/utils/storage'
import { importStudents, type StudentImportData } from '@/utils/api'
import type { StudentList } from '@/utils/storage'

const show = ref(false)
const importType = ref<'excel' | 'text'>('excel')
const selectedFileName = ref('')
const excelPreview = ref<StudentImportData[]>([])
const isImporting = ref(false)

const formData = reactive({
  name: '',
  students: ''
})

const emit = defineEmits<{
  success: []
}>()

const open = () => {
  show.value = true
  importType.value = 'excel'
}

const close = () => {
  show.value = false
  formData.name = ''
  formData.students = ''
  selectedFileName.value = ''
  excelPreview.value = []
  importType.value = 'excel'
}

// 选择 Excel 文件
const handleSelectFile = () => {
  // 微信小程序使用 chooseMessageFile，其他平台使用 chooseFile
  // #ifdef MP-WEIXIN
  uni.chooseMessageFile({
    count: 1,
    type: 'file',
    extension: ['xlsx', 'xls'],
    success: (res) => {
      const tempFiles = Array.isArray(res.tempFiles) ? res.tempFiles : [res.tempFiles]
      const file = tempFiles[0]
      if (!file) {
        uni.showToast({ title: '未选择文件', icon: 'none' })
        return
      }
      selectedFileName.value = file.name || ''
      
      // 读取文件
      const filePath = file.path || ''
      readExcelFile(filePath)
    },
    fail: (err) => {
      console.error('选择文件失败:', err)
      uni.showToast({ title: '选择文件失败', icon: 'none' })
    }
  })
  // #endif
  
  // #ifndef MP-WEIXIN
  uni.chooseFile({
    count: 1,
    extension: ['.xlsx', '.xls'],
    success: (res) => {
      const tempFiles = Array.isArray(res.tempFiles) ? res.tempFiles : [res.tempFiles]
      const file = tempFiles[0]
      if (!file) {
        uni.showToast({ title: '未选择文件', icon: 'none' })
        return
      }
      // 处理不同类型的文件对象
      const fileName = 'name' in file ? file.name : (file as any).name || ''
      const filePath = 'path' in file ? file.path : (file as any).path || ''
      
      selectedFileName.value = fileName
      readExcelFile(filePath)
    },
    fail: (err) => {
      console.error('选择文件失败:', err)
      uni.showToast({ title: '选择文件失败', icon: 'none' })
    }
  })
  // #endif
}

// 读取并解析 Excel 文件
const readExcelFile = (filePath: string) => {
  uni.showLoading({ title: '解析中...' })
  
  // 读取文件
  const fs = uni.getFileSystemManager()
  fs.readFile({
    filePath: filePath,
    encoding: 'binary',
    success: (res) => {
      try {
        // 解析 Excel
        const workbook = XLSX.read(res.data as string, { type: 'binary' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        
        // 转换为 JSON
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][]
        
        if (jsonData.length < 2) {
          uni.hideLoading()
          uni.showToast({ title: 'Excel 文件至少需要2行数据（表头+数据）', icon: 'none' })
          return
        }
        
        // 解析表头，查找学号、姓名、专业列
        const headers = (jsonData[0] as any[]).map((h: any) => String(h || '').trim().toLowerCase())
        let studentIdIndex = -1
        let studentNameIndex = -1
        let studentMajorIndex = -1
        
        // 尝试匹配表头（支持多种可能的表头名称）
        headers.forEach((header, index) => {
          if (header.includes('学号') || header.includes('student_id') || header.includes('id')) {
            studentIdIndex = index
          }
          if (header.includes('姓名') || header.includes('student_name') || header.includes('name') || header.includes('名字')) {
            studentNameIndex = index
          }
          if (header.includes('专业') || header.includes('student_major') || header.includes('major') || header.includes('专业名称')) {
            studentMajorIndex = index
          }
        })
        
        if (studentIdIndex === -1 || studentNameIndex === -1 || studentMajorIndex === -1) {
          uni.hideLoading()
          uni.showToast({ 
            title: 'Excel 必须包含：学号、姓名、专业三列', 
            icon: 'none',
            duration: 3000
          })
          return
        }
        
        // 解析数据行
        const parsedData: StudentImportData[] = []
        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i] as any[]
          const studentId = String(row[studentIdIndex] || '').trim()
          const studentName = String(row[studentNameIndex] || '').trim()
          const studentMajor = String(row[studentMajorIndex] || '').trim()
          
          // 跳过空行
          if (!studentId && !studentName && !studentMajor) {
            continue
          }
          
          if (!studentId || !studentName) {
            continue // 学号和姓名必填
          }
          
          parsedData.push({
            student_id: studentId,
            student_name: studentName,
            student_major: studentMajor || '未设置',
            description: formData.name.trim() || undefined
          })
        }
        
        if (parsedData.length === 0) {
          uni.hideLoading()
          uni.showToast({ title: '未找到有效数据', icon: 'none' })
          return
        }
        
        excelPreview.value = parsedData
        uni.hideLoading()
        uni.showToast({ title: `成功解析 ${parsedData.length} 条数据`, icon: 'success' })
      } catch (error) {
        console.error('解析 Excel 失败:', error)
        uni.hideLoading()
        uni.showToast({ title: '解析 Excel 失败，请检查文件格式', icon: 'none' })
      }
    },
    fail: (err) => {
      console.error('读取文件失败:', err)
      uni.hideLoading()
      uni.showToast({ title: '读取文件失败', icon: 'none' })
    }
  })
}

// 处理导入
const handleImport = async () => {
  if (!formData.name.trim()) {
    uni.showToast({ title: '请输入名单名称', icon: 'none' })
    return
  }

  if (importType.value === 'excel') {
    // Excel 导入
    if (excelPreview.value.length === 0) {
      uni.showToast({ title: '请先选择并解析 Excel 文件', icon: 'none' })
      return
    }
    
    isImporting.value = true
    try {
      // 构建后端期望的请求体：{ description, students: [...] }
      const dataToSend = {
        description: formData.name.trim(),
        students: excelPreview.value.map(item => ({
          student_id: item.student_id,
          student_name: item.student_name,
          student_major: item.student_major
        }))
      }

      // 调用后端接口
      await importStudents(dataToSend)
      
      // 同时保存到本地（可选，根据需求决定）
      const students = excelPreview.value.map(item => 
        `${item.student_id} · ${item.student_name}`
      )
      const newList: StudentList = {
        name: formData.name.trim(),
        students: students,
        createTime: Date.now()
      }
      addStudentList(newList)
      
      uni.showToast({ title: '导入成功', icon: 'success' })
      emit('success')
      close()
    } catch (error: any) {
      console.error('导入失败:', error)
      uni.showToast({ 
        title: error.message || '导入失败，请稍后重试', 
        icon: 'none',
        duration: 3000
      })
    } finally {
      isImporting.value = false
    }
  } else {
    // 文本导入（原有逻辑）
    if (!formData.students.trim()) {
      uni.showToast({ title: '请输入学生名单', icon: 'none' })
      return
    }

    try {
      const students = formData.students
        .split('\n')
        .map((s) => s.trim())
        .filter((s) => s.length > 0)

      if (students.length === 0) {
        uni.showToast({ title: '至少需要一个学生名字', icon: 'none' })
        return
      }

      const newList: StudentList = {
        name: formData.name.trim(),
        students: students,
        createTime: Date.now()
      }

      addStudentList(newList)
      uni.showToast({ title: '导入成功', icon: 'success' })
      emit('success')
      close()
    } catch (error) {
      uni.showToast({ title: '导入失败，请检查格式', icon: 'none' })
    }
  }
}

defineExpose({
  open,
  close
})
</script>

<style scoped>
.import-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: flex-end;
  z-index: 1000;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  width: 100%;
  background-color: white;
  border-radius: 20rpx 20rpx 0 0;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  border-bottom: 1rpx solid #e5e7eb;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1f2937;
}

.close-btn {
  font-size: 32rpx;
  color: #9ca3af;
  cursor: pointer;
}

.modal-body {
  flex: 1;
  padding: 24rpx;
  overflow-y: auto;
}

.input-group {
  margin-bottom: 24rpx;
}

.label {
  display: block;
  font-size: 26rpx;
  color: #374151;
  font-weight: 500;
  margin-bottom: 8rpx;
}

.hint-text {
  font-size: 22rpx;
  color: #9ca3af;
  margin-bottom: 8rpx;
  display: block;
}

.input-field {
  width: 100%;
  padding: 12rpx 16rpx;
  border: 1rpx solid #e5e7eb;
  border-radius: 8rpx;
  font-size: 26rpx;
  box-sizing: border-box;
}

.textarea-field {
  width: 100%;
  height: 200rpx;
  padding: 12rpx 16rpx;
  border: 1rpx solid #e5e7eb;
  border-radius: 8rpx;
  font-size: 26rpx;
  box-sizing: border-box;
  font-family: monospace;
}

.tips {
  background-color: #f0fdf4;
  border-left: 4rpx solid #22c55e;
  padding: 12rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  color: #15803d;
  margin-bottom: 24rpx;
}

.modal-footer {
  display: flex;
  gap: 12rpx;
  padding: 24rpx;
  border-top: 1rpx solid #e5e7eb;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 14rpx 24rpx;
  border: none;
  border-radius: 8rpx;
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-cancel {
  background-color: #f3f4f6;
  color: #374151;
}

.btn-confirm {
  background-color: #2563eb;
  color: white;
}

.btn-confirm:active {
  background-color: #1d4ed8;
}

.btn-confirm:disabled {
  background-color: #9ca3af;
  opacity: 0.6;
}

/* 导入方式选择标签 */
.import-type-tabs {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
  background-color: #f3f4f6;
  padding: 8rpx;
  border-radius: 12rpx;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #6b7280;
  transition: all 0.3s ease;
}

.tab-item.active {
  background-color: #ffffff;
  color: #2563eb;
  font-weight: 500;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

/* 文件选择按钮 */
.btn-select-file {
  width: 100%;
  padding: 20rpx;
  border: 2rpx dashed #d1d5db;
  border-radius: 12rpx;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  font-size: 26rpx;
  color: #374151;
  transition: all 0.3s ease;
}

.btn-select-file:active {
  background-color: #f3f4f6;
  border-color: #2563eb;
}

/* Excel 预览 */
.excel-preview {
  margin-top: 20rpx;
  padding: 20rpx;
  background-color: #f9fafb;
  border-radius: 12rpx;
  border: 1rpx solid #e5e7eb;
}

.preview-title {
  display: block;
  font-size: 24rpx;
  font-weight: 500;
  color: #374151;
  margin-bottom: 12rpx;
}

.preview-table {
  width: 100%;
  border: 1rpx solid #e5e7eb;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.preview-row {
  display: flex;
  border-bottom: 1rpx solid #e5e7eb;
}

.preview-row:last-child {
  border-bottom: none;
}

.preview-header {
  background-color: #f3f4f6;
  font-weight: 500;
}

.preview-cell {
  flex: 1;
  padding: 12rpx 16rpx;
  font-size: 24rpx;
  color: #1f2937;
  text-align: center;
  border-right: 1rpx solid #e5e7eb;
  word-break: break-all;
}

.preview-cell:last-child {
  border-right: none;
}

.preview-header .preview-cell {
  color: #6b7280;
  font-weight: 500;
}

.preview-count {
  display: block;
  font-size: 22rpx;
  color: #6b7280;
  text-align: center;
}
</style>
