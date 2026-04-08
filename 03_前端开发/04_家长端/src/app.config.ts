export default defineAppConfig({
  pages: [
    'pages/login/index',
    'pages/index/index',
    'pages/scores/index'
  ],
  window: {
    navigationBarTitleText: '家长端',
    navigationBarBackgroundColor: '#ffffff',
    navigationBarTextStyle: 'black',
    backgroundColor: '#f5f7fa'
  },
  tabBar: {
    color: '#666666',
    selectedColor: '#1677ff',
    backgroundColor: '#ffffff',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页'
      },
      {
        pagePath: 'pages/scores/index',
        text: '成绩'
      }
    ]
  }
})
