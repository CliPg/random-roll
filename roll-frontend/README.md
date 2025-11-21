# 智能点名系统 - uni-app 微信小程序

一个基于 Vue 3 + TypeScript + uni-app 开发的智能随机点名系统，用于微信小程序平台。

## 🎯 功能特性

### 核心功能
- **👥 名单管理**
  - 导入学生名单（支持批量导入）
  - 删除指定名单
  - 清空所有名单
  - 本地持久化存储

- **🎤 开始点名**
  - 随机点名模式
  - 顺序点名模式
  - 可调节点名间隔
  - 显示最后点名结果

- **📊 结果统计**
  - 记录每次点名信息
  - 显示点名时间和学生信息
  - 标记学生到课状态

- **🏆 积分排行**
  - 按周/月分类统计
  - 实时排行榜展示
  - 积分兑换系统

## 🛠️ 技术栈

- **框架**: Vue 3 + TypeScript
- **平台**: uni-app (微信小程序)
- **构建工具**: Vite
- **UI 风格**: 自适应响应式设计
- **存储**: 本地存储 (localStorage)

## 📦 项目结构

```
random-roll/
├── src/
│   ├── pages/
│   │   └── index/
│   │       └── index.vue          # 主页面
│   ├── components/
│   │   ├── ImportModal.vue        # 导入对话框
│   │   └── SettingsModal.vue      # 设置对话框
│   ├── utils/
│   │   └── storage.ts             # 本地存储工具
│   ├── App.vue                    # 应用根组件
│   ├── main.ts                    # 入口文件
│   └── manifest.json              # 小程序配置
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 🚀 快速开始

### 安装依赖
```bash
pnpm install
```

### 开发模式（微信小程序）
```bash
pnpm run dev:mp-weixin
```

### 构建生成（微信小程序）
```bash
pnpm run build:mp-weixin
```

### 其他平台
- **H5**: `pnpm run dev:h5`
- **支付宝小程序**: `pnpm run dev:mp-alipay`
- **字节跳动小程序**: `pnpm run dev:mp-toutiao`

## 💾 数据存储

### 本地存储的数据结构

**学生名单** (`student_lists`):
```typescript
interface StudentList {
  name: string              // 名单名称
  students: string[]        // 学生名单
  createTime: number        // 创建时间戳
}
```

**点名记录** (`call_records`):
```typescript
interface CallRecord {
  time: string             // 点名时间
  student: string          // 学生名字
  status: string           // 到课状态
  statusClass: string      // CSS类名
}
```

**应用设置** (`app_settings`):
```typescript
interface Settings {
  interval: number         // 点名间隔(ms)
  sound: boolean          // 声音提示
  vibration: boolean      // 振动反馈
}
```

## 🎨 UI 组件说明

### ImportModal（导入对话框）
用于导入新的学生名单。支持：
- 输入名单名称
- 多行文本输入学生名字
- 自动验证和清理输入

### SettingsModal（设置对话框）
用于配置应用设置。包括：
- 调节点名间隔（50ms-1000ms）
- 启用/禁用声音提示
- 启用/禁用振动反馈

## 🔧 API 说明

### storage.ts 工具函数

```typescript
// 获取所有学生名单
getStudentLists(): StudentList[]

// 保存学生名单列表
saveStudentLists(lists: StudentList[]): void

// 添加新的学生名单
addStudentList(list: StudentList): void

// 删除指定索引的学生名单
deleteStudentList(index: number): void

// 清空所有名单
clearAllLists(): void

// 保存点名记录
saveCallRecord(record: any): void

// 获取所有点名记录
getCallRecords(): any[]

// 获取应用设置
getSettings(): any

// 保存应用设置
saveSettings(settings: any): void
```

## 📱 页面流程

### 首次使用流程
1. 打开小程序，进入"名单管理"标签页
2. 点击"导入名单"按钮
3. 输入班级名称和学生名单
4. 确认导入
5. 进入"开始点名"标签页进行点名

### 点名使用流程
1. 切换到"开始点名"标签页
2. 选择点名模式（随机/顺序）
3. 点击"开始点名"按钮
4. 名字开始滚动显示
5. 点击"停止点名"停止滚动
6. 记录自动保存

## 🎯 样式特点

- **现代化设计**: 使用蓝色和紫色渐变主题
- **响应式布局**: 适配各种屏幕尺寸
- **平滑动画**: 页面切换、名字滚动等动画效果
- **无障碍设计**: 清晰的视觉层级和易读的字体

## 📝 使用示例

### 导入名单示例
```
名单名称: 2025级操作系统

学生名单:
小明
小红
小刚
小华
小李
小张
小王
小赵
```

## 🔮 后续功能规划

- [ ] 支持从 Excel/CSV 文件导入
- [ ] 点名结果数据统计和可视化
- [ ] 学生出勤率统计
- [ ] 多选择班级管理
- [ ] 云端数据同步
- [ ] 点名音效和振动反馈
- [ ] 数据导出为 PDF
- [ ] 点名历史记录查询

## 🐛 已知问题

暂无已知问题。如遇到问题，请提交 Issue 反馈。

## 📄 许可证

MIT

## 👨‍💻 开发者

基于 uni-app 官方模板开发

---

**最后更新**: 2025年11月11日


## Modules

### roster

**功能**
- 导入名单
- 导出名单
- 清空名单
- 选择名单
- 展示名单

**实现原理**
- 展示名单
  在onMounted()的生命周期内会调用loadStudentLists()，然后通过getStudentLists()获取。getStudentLists从本地缓存取出之前保存的名单，从而获取studentLists。

- 导入名单

解析导入的excel文件，