const path = require('path')
const MiniCSSExtractPlugin = require('mini-css-extract-plugin')
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin')
const TerserWenpackPlugin = require('terser-webpack-plugin')
var webpack = require('webpack');

const isDev = process.env.NODE_ENV === 'development'
const isProd = !isDev
const optimization = () => {
    const config = {}
    if (isProd) {
        config.minimizer = [
            new CssMinimizerPlugin(),
            new TerserWenpackPlugin()
        ]
    }
    return config
}
module.exports = {
    entry: './src/index.js',
    mode: 'development',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'users/static/users/js'),
    },
    optimization: optimization(),
    plugins: [
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
        }),
        new MiniCSSExtractPlugin({
            filename: 'styles2.css'
        })
    ],
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    {
                        loader: MiniCSSExtractPlugin.loader
                    },
                    'css-loader'
                ]
            },
            {
                test: /\.(ttf|woff|woff2|eot)$/,
                use: ['file-loader']
            }
        ]
    }
};