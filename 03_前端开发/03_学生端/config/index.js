module.exports = {
  projectName: 'edu-student',
  framework: 'react',
  sourceRoot: 'src',
  outputRoot: 'dist',
  compiler: 'webpack5',
  designWidth: 750,
  deviceRatio: {
    640: 2.34 / 2,
    750: 1,
    828: 1.81 / 2
  },
  plugins: [],
  mini: {},
  h5: {
    router: {
      mode: 'hash'
    },
    devServer: {
      port: 3002,
      host: '0.0.0.0'
    },
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
        config: {
          targets: ['last 2 versions', 'not ie <= 8']
        }
      },
      pxtransform: {
        enable: false
      }
    }
  }
}
