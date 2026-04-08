module.exports = {
  projectName: 'edu-classroom',
  sourceRoot: 'src',
  outputRoot: 'dist',
  compiler: 'webpack5',
  designWidth: 750,
  deviceRatio: {
    '640': 2 / 2,
    '750': 1,
    '828': 810 / 828
  },
  plugins: [],
  framework: 'react',
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
