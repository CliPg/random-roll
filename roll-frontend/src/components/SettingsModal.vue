<template>
  <view v-if="show" class="settings-modal">
    <view class="modal-overlay" @tap="close"></view>
    <view class="modal-content">
      <view class="modal-header">
        <text class="modal-title">应用设置</text>
        <text class="close-btn" @tap="close">✕</text>
      </view>

      <view class="modal-body">
        <view class="setting-item">
          <view class="setting-label">
            <text class="label-text">点名间隔</text>
            <text class="label-desc">{{ settings.interval }}ms</text>
          </view>
          <slider
            :value="settings.interval"
            :min="50"
            :max="1000"
            :step="50"
            class="slider"
            @change="settings.interval = ($event as any).detail.value"
          />
          <view class="slider-marks">
            <text>50ms</text>
            <text>1000ms</text>
          </view>
        </view>

        <view class="setting-item">
          <view class="setting-label">
            <text class="label-text">声音提示</text>
          </view>
          <switch
            :checked="settings.sound"
            class="switch"
            @change="settings.sound = ($event as any).detail.value"
          />
        </view>

        <view class="setting-item">
          <view class="setting-label">
            <text class="label-text">振动反馈</text>
          </view>
          <switch
            :checked="settings.vibration"
            class="switch"
            @change="settings.vibration = ($event as any).detail.value"
          />
        </view>

        <view class="setting-item">
          <view class="setting-label">
            <text class="label-text">关于应用</text>
            <text class="label-desc">v1.0.0</text>
          </view>
        </view>
      </view>

      <view class="modal-footer">
        <button class="btn-save" @tap="handleSave">保存设置</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { getSettings, saveSettings } from '@/utils/storage'

const show = ref(false)

const settings = reactive({
  interval: 300,
  sound: true,
  vibration: true
})

const emit = defineEmits<{
  update: [settings: typeof settings]
}>()

const open = () => {
  show.value = true
  const savedSettings = getSettings()
  Object.assign(settings, savedSettings)
}

const close = () => {
  show.value = false
}

const handleSave = () => {
  saveSettings(settings)
  emit('update', settings)
  uni.showToast({ title: '设置已保存', icon: 'success' })
  close()
}

defineExpose({
  open,
  close
})
</script>

<style scoped>
.settings-modal {
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

.setting-item {
  margin-bottom: 32rpx;
  padding: 16rpx;
  background-color: #f9fafb;
  border-radius: 12rpx;
}

.setting-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.label-text {
  font-size: 28rpx;
  color: #1f2937;
  font-weight: 500;
}

.label-desc {
  font-size: 24rpx;
  color: #9ca3af;
}

.slider {
  width: 100%;
  height: 4rpx;
  margin: 12rpx 0;
}

.slider-marks {
  display: flex;
  justify-content: space-between;
  font-size: 22rpx;
  color: #9ca3af;
}

.switch {
  transform: scale(0.8);
  transform-origin: right center;
}

.modal-footer {
  display: flex;
  gap: 12rpx;
  padding: 24rpx;
  border-top: 1rpx solid #e5e7eb;
}

.btn-save {
  flex: 1;
  padding: 14rpx 24rpx;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 8rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.btn-save:active {
  background-color: #1d4ed8;
}
</style>
