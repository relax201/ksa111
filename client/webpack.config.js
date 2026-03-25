const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  // Modo de desarrollo
  mode: 'development',
  
  // Punto de entrada
  entry: './src/index.js',
  
  // Salida
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: 'bundle.js',
    publicPath: '/'
  },
  
  // Configuración del servidor de desarrollo
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    port: 3000,
    hot: true,
    historyApiFallback: true,
    
    // Add proxy for backend API
    proxy: [
      {
        context: ['/api.php'],
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    ],
    
    // Usar setupMiddlewares en lugar de onBeforeSetupMiddleware y onAfterSetupMiddleware
    setupMiddlewares: (middlewares, devServer) => {
      // Esta función será llamada por webpack-dev-server para configurar middlewares
      // pero la implementación real está en setupProxy.js
      return middlewares;
    }
  },
  
  // Reglas de módulos
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
      }
    ]
  },
  
  // Extensiones
  resolve: {
    extensions: ['.js', '.jsx']
  },
  
  // Plugins
  plugins: [
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, 'public/webpack-index.html'),
      filename: 'index.html',
      inject: 'body'
    })
  ]
};