const path = require('path');

/**
 * Creates a base gulpfile that can be used by all n8n community packages.
 * @param {*} options
 * @returns
 */
function createTask(options = {}) {
	const { src = './nodes/**/*.svg', dest = './dist/icons' } = options;

	return () => {
		const gulp = require('gulp');
		return gulp.src(src).pipe(gulp.dest(dest));
	};
}

exports.build = {
	icons: createTask(),
};