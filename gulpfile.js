'use strict';

var gulp = require('gulp'),
    sass          = require('gulp-sass'),
    logger        = require('gulp-logger'),
    watch         = require('gulp-watch'),
    prefixer      = require('gulp-autoprefixer'),
    uglify        = require('gulp-uglify'),
    rigger        = require('gulp-rigger'),
    cssmin        = require('gulp-minify-css'),
    rename        = require('gulp-rename'),
    plumber       = require('gulp-plumber'),
    livereload    = require('gulp-livereload');

var path = {
    build: {
        js: 'app/static/js',
        css: 'app/static/css/',
        fonts: 'app/static/fonts/'
    },
    src: {
        js:    'src/js/*.js',
        style: 'src/scss/*.scss',
        awesomeFonts: 'bower_components/components-font-awesome/fonts/**/*.*'
    },
    watch: {
        js: 'src/js/**/*.js',
        style: 'src/scss/**/*.scss',
        awesomeFonts: 'bower_components/components-font-awesome/fonts/**/*.*'
    }
};

gulp.task('js:build', function () {
    gulp.src(path.src.js)
        .pipe(plumber())
        .pipe(logger({
            before: 'Start JS concatination',
            after: 'JS concatination complete!',
            extname: '.js',
            showChange: true
        }))
        .pipe(rigger())
        .pipe(logger({
            before: 'Start JS compress',
            after: 'JS compress complete!',
            extname: '.js',
            showChange: true
        }))
        // .pipe(uglify()) // comment for the best speed
        .pipe(rename({
            suffix: '.min'
        }))
        .pipe(gulp.dest(path.build.js))
        .pipe(livereload());
});

gulp.task('style:build', function () {
    // Load path with sass files
    gulp.src(path.src.style)
        .pipe(plumber())
        .pipe(logger({
            before: '[STYLE] Start SASS comppile',
            after: '[STYLE] SASS comppile complete!',
            extname: '.css',
            showChange: true
        }))
        .pipe(sass())
        // Add vendor prefix
        .pipe(logger({
            before: '[STYLE] Start add vendor prefix',
            after: '[STYLE] Vendor prefix complete!',
            extname: '.css',
            showChange: true
        }))
        .pipe(prefixer())
        .pipe(logger({
            before: '[STYLE] Start minification',
            after: '[STYLE] Minification complete!',
            extname: '.css',
            showChange: true
        }))
        .pipe(cssmin())
        .pipe(rename({
            suffix: '.min'
        }))
        .pipe(gulp.dest(path.build.css))
        .pipe(livereload());
});

gulp.task('awesomeFonts:build', function() {
    gulp.src(path.src.awesomeFonts)
        .pipe(plumber())
        .pipe(logger({
            before: '[FONTS] Start FontsAwesome',
            after: '[FONTS] FontsAwesome complete!',
            showChange: true
        }))
        .pipe(gulp.dest(path.build.fonts))
});

gulp.task('build', [
    'js:build',
    'style:build',
    'awesomeFonts:build',
]);

gulp.task('watch', function(){
    livereload.listen();
    watch([path.watch.style], { usePolling: true }, function(event, cb) {
        gulp.start('style:build');
    });
    watch([path.watch.js], { usePolling: true }, function(event, cb) {
        gulp.start('js:build');
    });
    watch([path.watch.awesomeFonts], function(event, cb) {
        gulp.start('awesomeFonts:build');
    });
});

gulp.task('default', ['build', 'watch']);
