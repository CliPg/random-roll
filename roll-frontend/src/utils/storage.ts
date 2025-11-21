/**
 * 本地存储工具类
 */

export interface StudentList {
  name: string
  students: string[]
  createTime: number
}

const STORAGE_KEY = 'student_lists'
const RECORDS_KEY = 'call_records'
const SETTINGS_KEY = 'app_settings'
const SELECTED_LIST_KEY = 'selected_list_index'
const WEIXIN_AUTH_CODE_KEY = 'weixin_auth_code'
const WEIXIN_AUTH_CODE_TS_KEY = 'weixin_auth_code_ts'

/**
 * 获取所有学生名单
 */
export const getStudentLists = (): StudentList[] => {
  try {
    const data = uni.getStorageSync(STORAGE_KEY)
    return data ? JSON.parse(data) : []
  } catch (error) {
    console.error('Failed to get student lists:', error)
    return []
  }
}

/**
 * 保存学生名单
 */
export const saveStudentLists = (lists: StudentList[]): void => {
  try {
    uni.setStorageSync(STORAGE_KEY, JSON.stringify(lists))
  } catch (error) {
    console.error('Failed to save student lists:', error)
  }
}

/**
 * 添加学生名单
 */
export const addStudentList = (list: StudentList): void => {
  const lists = getStudentLists()
  lists.push(list)
  saveStudentLists(lists)
}

/**
 * 删除学生名单
 */
export const deleteStudentList = (index: number): void => {
  const lists = getStudentLists()
  lists.splice(index, 1)
  saveStudentLists(lists)
}

/**
 * 清空所有名单
 */
export const clearAllLists = (): void => {
  try {
    uni.removeStorageSync(STORAGE_KEY)
    uni.removeStorageSync(SELECTED_LIST_KEY)
  } catch (error) {
    console.error('Failed to clear lists:', error)
  }
}

/**
 * 保存当前选中的名单索引
 */
export const saveSelectedListIndex = (index: number): void => {
  try {
    const safeIndex = Number.isInteger(index) ? index : -1
    uni.setStorageSync(SELECTED_LIST_KEY, safeIndex)
  } catch (error) {
    console.error('Failed to save selected list index:', error)
  }
}

/**
 * 获取当前选中的名单索引
 */
export const getSelectedListIndex = (): number => {
  try {
    const value = uni.getStorageSync(SELECTED_LIST_KEY)
    const parsed = Number(value)
    return Number.isInteger(parsed) ? parsed : -1
  } catch (error) {
    console.error('Failed to get selected list index:', error)
    return -1
  }
}

/**
 * 移除当前选中的名单索引
 */
export const removeSelectedListIndex = (): void => {
  try {
    uni.removeStorageSync(SELECTED_LIST_KEY)
  } catch (error) {
    console.error('Failed to remove selected list index:', error)
  }
}

/**
 * 保存点名记录
 */
export const saveCallRecord = (record: any): void => {
  try {
    const records = uni.getStorageSync(RECORDS_KEY) || []
    records.push(record)
    // 只保留最近100条记录
    if (records.length > 100) {
      records.shift()
    }
    uni.setStorageSync(RECORDS_KEY, records)
  } catch (error) {
    console.error('Failed to save call record:', error)
  }
}

/**
 * 获取点名记录
 */
export const getCallRecords = (): any[] => {
  try {
    return uni.getStorageSync(RECORDS_KEY) || []
  } catch (error) {
    console.error('Failed to get call records:', error)
    return []
  }
}

/**
 * 获取应用设置
 */
export const getSettings = (): any => {
  try {
    const settings = uni.getStorageSync(SETTINGS_KEY)
    return settings || { interval: 300, sound: true, vibration: true }
  } catch (error) {
    console.error('Failed to get settings:', error)
    return { interval: 300, sound: true, vibration: true }
  }
}

/**
 * 保存应用设置
 */
export const saveSettings = (settings: any): void => {
  try {
    uni.setStorageSync(SETTINGS_KEY, settings)
  } catch (error) {
    console.error('Failed to save settings:', error)
  }
}

export const saveWeixinAuthCode = (code: string): void => {
  try {
    if (typeof code === 'string' && code.trim()) {
      uni.setStorageSync(WEIXIN_AUTH_CODE_KEY, code.trim())
      uni.setStorageSync(WEIXIN_AUTH_CODE_TS_KEY, Date.now())
    }
  } catch (error) {
    console.error('Failed to save weixin auth code:', error)
  }
}

export const getWeixinAuthCodeCached = (ttlMs: number = 300000): string | null => {
  try {
    const code = uni.getStorageSync(WEIXIN_AUTH_CODE_KEY)
    const ts = uni.getStorageSync(WEIXIN_AUTH_CODE_TS_KEY)
    if (!code || !ts) return null
    const age = Date.now() - Number(ts)
    if (Number.isNaN(age) || age > ttlMs) return null
    return typeof code === 'string' ? code : null
  } catch (error) {
    console.error('Failed to get weixin auth code:', error)
    return null
  }
}

export const clearWeixinAuthCode = (): void => {
  try {
    uni.removeStorageSync(WEIXIN_AUTH_CODE_KEY)
    uni.removeStorageSync(WEIXIN_AUTH_CODE_TS_KEY)
  } catch (error) {
    console.error('Failed to clear weixin auth code:', error)
  }
}
