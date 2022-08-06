'use strict';

import plugins from 'gulp-load-plugins';
import yargs from 'yargs';
import browser from 'browser-sync';
import gulp from 'gulp';
import rimraf from 'rimraf';
import sherpa from 'style-sherpa';
import yaml from 'js-yaml';
import fs from 'fs';
import webpackStream from 'webpack-stream';
import webpack2 from 'webpack';
import named from 'vinyl-named';
import autoprefixer from 'autoprefixer';
import favicons from 'gulp-favicons';
import uncss from 'uncss';
import path from 'path';
import UglifyJsPlugin from 'uglifyjs-webpack-plugin';
import { BundleAnalyzerPlugin } from 'webpack-bundle-analyzer';

// Load all Gulp plugins into one variable
const $ = plugins();

// Check for --production flag
const PRODUCTION = !!yargs.argv.production;

// Check for --analyzer flag
const ANALYZER = !!yargs.argv.analyzer;

const ENV = PRODUCTION ? 'production' : 'development';

// Load settings from settings.yml
const { PORT, UNCSS_OPTIONS, PATHS, FAVICONS } = loadConfig();

function loadConfig() {
    let ymlFile = fs.readFileSync('config.yml', 'utf8');
    return yaml.load(ymlFile);
}

// Build the "dist" folder by running all of the below tasks
gulp.task(
    'build',
    gulp.series(
        clean,
        gulp.parallel(javascript, fonts, copy),
        sass,
        styleGuide
    )
);

// Build the site, run the server, and watch for file changes
gulp.task('default', gulp.series('build', server, watch));

gulp.task('clean', gulp.series(clean));

// Delete the "dist" folder and others
// This happens every time a build starts
function clean(done) {
    rimraf(PATHS.dist, done);
}

// Copy files out of the assets folder
// This task skips over the "img", "js", and "scss" folders, which are parsed separately
function copy() {
    return gulp.src(PATHS.assets).pipe(gulp.dest(PATHS.dist + '/'));
}

// Compile Sass into CSS
// In production, the CSS is compressed
function sass(done) {
    const postCssPlugins = [
        // Autoprefixer
        autoprefixer()

        // UnCSS - Uncomment to remove unused styles in production
        // PRODUCTION && uncss.postcssPlugin(UNCSS_OPTIONS),
    ].filter(Boolean);

    return gulp
        .src(['src/assets/scss/app.scss', 'src/assets/scss/editor.scss'])
        .pipe($.sourcemaps.init())
        .pipe(
            $.sass({
                includePaths: PATHS.sass
            }).on('error', $.sass.logError)
        )
        .pipe($.postcss(postCssPlugins))
        .pipe($.if(PRODUCTION, $.cleanCss({ compatibility: 'ie9' })))
        .pipe($.if(!PRODUCTION, $.sourcemaps.write()))
        .pipe(gulp.dest(`${PATHS.dist}/css`))
        .pipe(browser.reload({ stream: true }));
}

let webpackPlugins = [
    new webpack2.ProvidePlugin({
        'window.jQuery': 'jquery',
        'window.$': 'jquery',
        $: 'jquery',
        jQuery: 'jquery'
    }),
    new webpack2.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(ENV)
    })
];

if (ANALYZER) webpackPlugins.push(new BundleAnalyzerPlugin());

let webpackConfig = {
    mode: ENV,
    entry: {
        app: path.join(__dirname, 'src/assets/js/app.js')
    },
    output: {
        path: path.resolve(__dirname, 'js'),
        filename: '[name].js',
        chunkFilename: '[name].bundle.js',
        publicPath: `/${PATHS.ss_dist}/`
    },
    module: {
        rules: [
            {
                test: /.js$/,
                exclude: [/(lazysizes\.js)/, /\bcore-js\b/],
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            [
                                '@babel/preset-env',
                                {
                                    useBuiltIns: 'entry',
                                    corejs: '3.15'
                                }
                            ]
                        ],
                        compact: false
                    }
                }
            },
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: webpackPlugins,
    optimization: {
        minimizer: [new UglifyJsPlugin()],
        splitChunks: {
            cacheGroups: {
                vendor: {
                    chunks: 'all',
                    enforce: true,
                    name: 'vendor.0',
                    priority: -10,
                    test: /[\\/]node_modules[\\/](jquery|foundation-sites)[\\/]/
                },
                vendor1: {
                    chunks: 'all',
                    enforce: true,
                    name: 'vendor.1',
                    priority: -20,
                    test: /[\\/]node_modules[\\/](@swup|swup|swiper)[\\/]/
                },
                vendor2: {
                    chunks: 'all',
                    enforce: true,
                    name: 'vendor.2',
                    priority: -30,
                    test: /[\\/]node_modules[\\/](@fullcalendar)[\\/]/
                },
                vendor3: {
                    chunks: 'all',
                    enforce: true,
                    name: 'vendor.3',
                    priority: -40,
                    test: /[\\/]node_modules[\\/]/
                },
                default: {
                    minChunks: 2,
                    priority: -50,
                    reuseExistingChunk: true
                }
            }
        }
    },
    devtool: !PRODUCTION && 'source-map'
};

// Compile JS
function javascript() {
    return gulp
        .src(PATHS.entries)
        .pipe(named())
        .pipe($.sourcemaps.init())
        .pipe(webpackStream(webpackConfig, webpack2))
        .pipe(
            $.if(
                PRODUCTION,
                $.terser().on('error', e => {
                    console.log(e);
                })
            )
        )
        .pipe($.if(!PRODUCTION, $.sourcemaps.write()))
        .pipe(gulp.dest(PATHS.dist + '/js'));
}

// Processes favicons and placces into the "dist" folder
// Generages a favicon.hbs that can be included in the template.
function icons() {
    return gulp
        .src(PATHS.favicon)
        .pipe(favicons(FAVICONS))
        .pipe(gulp.dest(`${PATHS.dist}/img/favicons/`));
}

// Copy Fonts to the "dist" folder
function fonts() {
    return gulp
        .src('src/assets/fonts/**/*')
        .pipe(gulp.dest(`${PATHS.dist}/fonts`));
}

// Start a server with BrowserSync to preview the site in
function server(done) {
    browser.init(
        {
            server: {
                baseDir: PATHS.dist,
                index: 'styleguide.html'
            },
            port: PORT
        },
        done
    );
}

// Generate a style guide from the Markdown content and HTML template in styleguide/
function styleGuide(done) {
    sherpa(
        'src/styleguide/index.md',
        {
            output: PATHS.dist + '/styleguide.html',
            template: 'src/styleguide/template.hbs'
        },
        done
    );
}

// Watch for changes to static assets, Sass, and JavaScript
function watch() {
    gulp.watch('src/assets/scss/**/*.scss').on('all', gulp.series(sass));
    gulp.watch('src/assets/js/**/*.js').on(
        'all',
        gulp.series(javascript, browser.reload)
    );
    gulp.watch('src/assets/img/**/*').on(
        'all',
        gulp.series(images, browser.reload)
    );
    gulp.watch('src/styleguide/**').on(
        'all',
        gulp.series(styleGuide, browser.reload)
    );
    console.log('--------------------------------------------------');
    console.log('** Be kind to your pets! **');
    console.log('--------------------------------------------------');
}
