import Taro from '@tarojs/taro'

const baseURL = 'http://127.0.0.1:8000/api'

const unwrap = (data: any) => {
  if (data && typeof data === 'object' && 'data' in data && Object.keys(data).length <= 4) {
    return data.data
  }
  return data
}

const buildQuery = (params?: Record<string, any>) => {
  if (!params) return ''
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    searchParams.append(key, String(value))
  })
  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

class Request {
  async request(url: string, options: any = {}) {
    const token = Taro.getStorageSync('token')
    const header = {
      'Content-Type': 'application/json',
      ...options.header,
    }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    try {
      const res = await Taro.request({
        url: baseURL + url,
        header,
        ...options,
      })
      if (res.statusCode >= 400) {
        const message = unwrap(res.data)?.error || unwrap(res.data)?.message || '请求失败'
        throw new Error(message)
      }
      return unwrap(res.data)
    } catch (e) {
      throw e
    }
  }

  get(url: string, params?: any) {
    return this.request(url + buildQuery(params), { method: 'GET' })
  }

  post(url: string, data?: any) {
    return this.request(url, { method: 'POST', data })
  }

  put(url: string, data?: any) {
    return this.request(url, { method: 'PUT', data })
  }

  delete(url: string) {
    return this.request(url, { method: 'DELETE' })
  }
}

export default new Request()
