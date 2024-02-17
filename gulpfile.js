const { series, src, dest } = require("gulp");

// Task 1: copy bootstap's assets to /_vendor/
function bulma() {
  const files = [
    // "node_modules/bulma/css/bulma.min.css",
    "node_modules/bulma-checkradio/dist/css/bulma-checkradio.min.css",
    "node_modules/@creativebulma/bulma-divider/dist/bulma-divider.min.css",
    // "node_modules/bootstrap/dist/js/bootstrap.min.js",
  ];
  return src(files).pipe(dest("_vendor"));
}

// Task 2: copy jquery's assets to /_vendor/
function jquery() {
  const files = ["node_modules/jquery/dist/jquery.min.js"];
  return src(files).pipe(dest("_vendor"));
}

// const uglify = require("gulp-uglify");
// const concat = require("gulp-concat");

// Task 3: minify blueimp's assets and save to /_vendor/
// function blueimp() {
//   const files = [
//     "node_modules/blueimp-file-upload/js/vendor/jquery.ui.widget.js",
//     "node_modules/blueimp-file-upload/js/jquery.iframe-transport.js",
//     "node_modules/blueimp-file-upload/js/jquery.fileupload.js",
//   ];
//   return src(files)
//     .pipe(uglify())
//     .pipe(concat("jquery.fileupload.min.js"))
//     .pipe(dest("_vendor/"));
// }

exports.default = series(bulma);
