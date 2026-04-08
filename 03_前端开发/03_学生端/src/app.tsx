import { useLaunch } from '@tarojs/taro'
import './app.scss'

function App(props) {
  useLaunch(() => {
    console.log('Student app launched.')
  })

  return props.children
}

export default App
