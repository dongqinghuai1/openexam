const path = require('path')

module.exports = {
  projectName: 'edu-classroom',
  designWidth: 750,
  deviceRatio: {
    '640': 2 / 2,
    '750': 1,
    '828': 810 / 828
  },
  plugins: [],
  framework: 'react',
  sass: {
    resource: path.resolve(__dirname, 'src/styles/variables.scss')
  },
  mini: {
    postcss: {
      pxtransform: {
        enable: true,
        config: {
          selectorBlackList: ['body']
        }
      },
      url: {
        enable: true,
        config: {
          limit: 10240
        }
      }
    }
  },
  h5: {
    router: {
      mode: 'hash',
      customRoutes: {}
    },
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
        config: {
          targets: ['last 2 versions', 'not ie <= 8']
        }
      }
    }
  }
}