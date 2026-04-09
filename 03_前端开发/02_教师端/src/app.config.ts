export default defineAppConfig({
  pages: [
    'pages/login/index',
    'pages/index/index',
    'pages/schedule/index',
    'pages/students/index',
    'pages/recordings/index',
    'pages/link/index',
    'pages/profile/index'
  ],
  window: {
    navigationBarTitleText: '教师端',
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
        pagePath: 'pages/students/index',
        text: '学生'
      },
      {
        pagePath: 'pages/recordings/index',
        text: '回放'
      }
    ]
  }
})
