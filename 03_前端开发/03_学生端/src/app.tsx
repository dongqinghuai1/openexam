import Taro, { useLaunch } from '@tarojs/taro'
import './app.scss'

function App(props) {
  useLaunch(() => {
    const params = Taro.getLaunchOptionsSync?.().query || {}
    if (params.token) {
      Taro.setStorageSync('token', params.token)
    }
    if (params.refresh_token) {
      Taro.setStorageSync('refresh_token', params.refresh_token)
    }
    if (params.user) {
      try {
        Taro.setStorageSync('userInfo', JSON.parse(decodeURIComponent(params.user)))
      } catch (_) {}
    }
    console.log('Student app launched.')
  })

  return props.children
}

export default App
