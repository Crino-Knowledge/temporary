// https://github.com/michael-ciniawsky/postcss-load-config

module.exports = {
  "plugins": {
    "postcss-import": {},
    "postcss-url": {},
    // to edit target browsers: use "browserslist" field in package.json
    "autoprefixer": {},
    "postcss-plugin-px2rem": {
      // rootValue: 192, // 设计稿宽度/10，通常设置为750的一半，即37.5
      propList: ['login-page'],
      rootValue: 16,
    }
  }
}
