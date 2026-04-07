import Taro from '@tarojs/taro'

const baseURL = 'http://localhost:8000/api'

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
      return res.data
    } catch (e) {
      throw e
    }
  }

  get(url: string, params?: any) {
    let query = ''
    if (params) {
      query = '?' + Object.keys(params).map(k => `${k}=${params[k]}`).join('&')
    }
    return this.request(url + query, { method: 'GET' })
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