import { Component, ReactNode } from 'react'
import { useLaunch } from '@tarojs/taro'
import './app.scss'

function App({ children }: { children: ReactNode }) {
  useLaunch(() => {
    console.log('App launched.')
  })

  return children
}

export default App