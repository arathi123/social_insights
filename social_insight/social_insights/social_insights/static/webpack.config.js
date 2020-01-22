var path = require('path');
var webpack = require('webpack');

module.exports = {
  entry: './js/index',
  output: {
    filename: 'browser-bundle.js',
    publicPath: '/static/'
  },
  devtool: 'source-map',
  resolve: {
    extensions: ['', '.js', '.jsx','.json']
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        include: path.join(__dirname, 'js'),
        query: {
          presets: ['es2015', 'react'],
        }
      },
      {
        test:/\.json$/,
        loader: 'json-loader',
        exclude: /node_modules/,
        include: path.join(__dirname, 'js')
      },
      { 
        test: /\.css$/, 
        loader: "style-loader!css-loader" 
      },
      {
        test: /\.(ttf|eot|svg|gif|woff(2)?)(\?[a-z0-9=&.]+)?$/,
        loader: 'file-loader' 
      }
    ]
  }
};
