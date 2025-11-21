<template>
	<view class="custom-tab-bar">
		<view 
			v-for="(item, index) in tabList" 
			:key="index"
			class="tab-item"
			:class="{ active: activeIndex === index }"
			@click="handleTabClick(index, item.pagePath)"
		>
			<uni-icons 
				:type="activeIndex === index ? item.selectedIcon : item.icon"
				:size="24"
				:color="activeIndex === index ? selectedColor : color"
			></uni-icons>
			<text class="tab-text">{{ item.text }}</text>
		</view>
	</view>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated, nextTick } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import uniIcons from '@dcloudio/uni-ui/lib/uni-icons/uni-icons.vue';

interface TabItem {
	pagePath: string;
	text: string;
	icon: string;
	selectedIcon: string;
}

const props = defineProps({
	color: {
		type: String,
		default: '#999999'
	},
	selectedColor: {
		type: String,
		default: '#2563eb'
	}
});

const activeIndex = ref(0);
const tabList = ref<TabItem[]>([
	{
		pagePath: 'pages/roster/roster',
		text: '名单管理',
		icon: 'person',
		selectedIcon: 'person-filled'
	},
	{
		pagePath: 'pages/rollcall/rollcall',
		text: '开始点名',
		icon: 'mic',
		selectedIcon: 'mic-filled'
	},
	{
		pagePath: 'pages/statistics/statistics',
		text: '结果统计',
		icon: 'calendar',
		selectedIcon: 'calendar-filled'
	},
	{
		pagePath: 'pages/leaderboard/leaderboard',
		text: '积分排行',
		icon: 'medal',
		selectedIcon: 'medal-filled'
	}
]);

const updateActiveIndex = () => {
	nextTick(() => {
		const pages = getCurrentPages();
		if (pages.length > 0) {
			const currentPage = pages[pages.length - 1];
			const currentRoute = currentPage.route || '';
			
			const index = tabList.value.findIndex(tab => {
				// 匹配完整的路径
				return currentRoute === tab.pagePath || currentRoute.includes(tab.pagePath.split('/').pop() || '');
			});
			
			if (index !== -1) {
				activeIndex.value = index;
			}
		}
	});
};

onMounted(() => {
	updateActiveIndex();
});

// 页面激活时更新激活状态
onActivated(() => {
	updateActiveIndex();
});

// 页面显示时更新激活状态（重要：在微信小程序中，tabBar 页面切换时会触发 onShow）
onShow(() => {
	updateActiveIndex();
});

const handleTabClick = (index: number, pagePath: string) => {
	if (activeIndex.value === index) {
		// 如果点击的是当前页面，不执行跳转
		return;
	}
	activeIndex.value = index;
	// 使用 switchTab 切换 tabBar 页面
	uni.switchTab({
		url: `/${pagePath}`,
		fail: (err) => {
			console.error('切换页面失败:', err);
			// 如果 switchTab 失败，尝试使用 navigateTo（不应该发生，但作为备用）
			uni.navigateTo({
				url: `/${pagePath}`
			});
		}
	});
};
</script>

<style scoped lang="scss">
.custom-tab-bar {
	display: flex;
	justify-content: space-around;
	align-items: center;
	height: 70px;
	padding-bottom: constant(safe-area-inset-bottom);
	padding-bottom: env(safe-area-inset-bottom);
	background-color: #ffffff;
	border-top: 1px solid #f0f0f0;
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	z-index: 99;
	box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
	padding-top: 25px;
}

.tab-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	flex: 1;
	height: 100%;
	cursor: pointer;
	transition: all 0.3s ease;
	
	&.active {
		.tab-text {
			color: v-bind('selectedColor');
			font-weight: 500;
		}
	}
}

.tab-text {
	font-size: 12px;
	margin-top: 4px;
	color: v-bind('color');
	transition: color 0.3s;
}
</style>
