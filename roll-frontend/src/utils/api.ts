// API 基础配置
// TODO: 请将 BASE_URL 替换为实际的后端 API 地址
const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:15444'

// 学生信息接口类型
export interface StudentImportData {
  student_id: string
  student_name: string
  student_major: string
  description?: string
}

export interface StudentImportRequest {
  description: string
  students: StudentImportData[]
}

// 点名结果接口类型
export interface RollResultPayload {
  student_id: string
  description?: string
  is_attend: boolean
  is_repeat: boolean
  answer_condition: number
}

// 请求封装
function request<T = any>(
  url: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any,
  headers?: Record<string, string>
): Promise<T> {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(headers || {})
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 获取微信登录 code（仅在微信小程序环境有效）
export async function getWeixinAuthCode(): Promise<string | undefined> {
  let code: string | undefined
  // #ifdef MP-WEIXIN
  try {
    const loginRes: any = await new Promise((resolve) => {
      uni.login({
        success: (res) => resolve(res),
        fail: () => resolve({})
      })
    })
    console.log('Weixin login response:', loginRes)
    if (loginRes && typeof loginRes.code === 'string') {
      code = loginRes.code
    }
  } catch (_) {
    code = undefined
  }
  // #endif
  return code
}

import { saveWeixinAuthCode } from '@/utils/storage'
let weixinAuthTimer: any | null = null

// 构建身份验证头（包含微信登录 code）
export async function buildIdentityHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {}
  // 为避免使用已经被微信标记为 "code been used" 的旧 code，
  // 在每次发起带身份的请求前都主动去获取一个新的 code。
  try {
    const newCode = await refreshWeixinAuthCode()
    console.log('Refreshed weixin auth code for request:', newCode)
    if (newCode) headers['Authorization'] = newCode
  } catch (e) {
    console.warn('refreshWeixinAuthCode failed', e)
  }
  return headers
}

// 刷新微信登录 code
export async function refreshWeixinAuthCode(): Promise<string | undefined> {
  const code = await getWeixinAuthCode()
  if (code) saveWeixinAuthCode(code)
  return code
}

// 开始自动刷新微信登录 code
export function startWeixinAuthCodeAutoRefresh(intervalMs: number = 240000): void {
  if (weixinAuthTimer) return
  weixinAuthTimer = setInterval(() => {
    refreshWeixinAuthCode()
  }, intervalMs)
  refreshWeixinAuthCode()
}

// 停止自动刷新微信登录 code
export function stopWeixinAuthCodeAutoRefresh(): void {
  if (weixinAuthTimer) {
    clearInterval(weixinAuthTimer)
    weixinAuthTimer = null
  }
}

// 导入学生名单
export async function importStudents(data: StudentImportRequest): Promise<any> {
  const headers = await buildIdentityHeaders()
  return request('/students/import', 'POST', data, headers)
}

// 提交点名结果
export async function submitRollResult(payload: RollResultPayload): Promise<any> {
  const query = Object.entries(payload)
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&')

  const url = query ? `/roll/result?${query}` : '/roll/result'
  return buildIdentityHeaders().then((headers) => request(url, 'POST', undefined, headers))
}

// 获取积分排行榜（order: 0 升序，1 降序）
export async function getPointsRank(
  order?: number,
  num?: number,
  description?: string
): Promise<{ code: number; msg: string; data: PointsRankItem[] }> {
  const params: Record<string, any> = {}
  if (order === 0 || order === 1) params.order = order
  if (typeof num === 'number' && num > 0) params.num = num
  if (description && description !== '') params.description = description
  const query = Object.entries(params)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&')
  const url = query ? `/points/rank?${query}` : '/points/rank'
  return buildIdentityHeaders().then((headers) => request(url, 'GET', undefined, headers))
}

// 积分排行接口类型
export interface PointsRankItem {
  student_id: string
  student_name: string
  credits: number
  random_rolls: string
}

export async function deleteStudentListOne(description?: string): Promise<any> {
  const query = description ? `?description=${encodeURIComponent(description)}` : ''
  const url = `/students/delete/one${query}`
  return buildIdentityHeaders().then((headers) => request(url, 'DELETE', undefined, headers))
}

export async function deleteStudentListAll(): Promise<any> {
  const url = `/students/delete/all`
  return buildIdentityHeaders().then((headers) => request(url, 'DELETE', undefined, headers))
}

// 导出学生名单，后端期望 POST { description }
export async function exportStudents(description: string): Promise<any> {
  const headers = await buildIdentityHeaders()
  const body = { description }
  return request('/students/export', 'POST', body, headers)
}

// 从后端获取一个随机学生（由后端负责权限校验与随机选择）
export async function pickRandomStudent(description: string, mode: 'random' | 'order' = 'random'): Promise<{ code: number; msg: string; data: { student_id: string; student_name: string } }> {
  const headers = await buildIdentityHeaders()
  const body = { description, mode }
  return request('/roll/random', 'POST', body, headers)
}

// 获取当前用户在后端的所有名单及学生
export async function getMyStudentLists(): Promise<{ description: string; students: any[] }[]> {
  const headers = await buildIdentityHeaders()
  return request('/students/list_all', 'POST', {}, headers)
}
