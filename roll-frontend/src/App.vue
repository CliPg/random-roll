<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { startWeixinAuthCodeAutoRefresh, stopWeixinAuthCodeAutoRefresh } from '@/utils/api'

onLaunch(() => {
  console.log("App Launch");
  startWeixinAuthCodeAutoRefresh()
});

onShow(() => {
  console.log("App Show");
});

onHide(() => {
  console.log("App Hide");
  stopWeixinAuthCodeAutoRefresh()
});
</script>

<style>
view {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

button {
  padding: 0;
  margin: 0;
  border: none;
  background-color: transparent;
  font-family: inherit;
}

input,
textarea {
  font-family: inherit;
}

/* 全局字体配置 */
page {
  font-size: 28rpx;
  color: #1f2937;
  background-color: #f5f5f5;
}
</style>
