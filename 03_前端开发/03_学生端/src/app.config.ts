export default defineAppConfig({
  pages: [
    'pages/login/index',
    'pages/index/index',
    'pages/schedule/index',
    'pages/exam/index',
    'pages/recordings/index',
    'pages/scores/index',
    'pages/profile/index'
  ],
  window: {
    navigationBarTitleText: '学生端',
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
        pagePath: 'pages/schedule/index',
        text: '课表'
      },
      {
        pagePath: 'pages/exam/index',
        text: '考试'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的'
      }
    ]
  }
})
