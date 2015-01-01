var proxySnippet = require('grunt-connect-proxy/lib/utils').proxyRequest;
var config = {
	    livereload: {
	        port: 35729
	    }
	};
var lrSnippet = require('connect-livereload')(config.livereload);
module.exports = function(grunt) { 
	var mountFolder = function (connect, dir) {
	    'use strict';
	    return connect.static(require('path').resolve(dir));
	};
	var proxySnippet = require('grunt-connect-proxy/lib/utils').proxyRequest;
    var dir = {
    		source: './src',
            theme: './src/theme',
            test: './test',
            build: './build',
            report: './reports',
            bower: './bower_components'
        };
    
    var proxies = {
	        localhost: {
	            context: '/api/v1',
	            host: '0.0.0.0',
	            port: 8080,
	            https: false,
	            rewrite: {
	                '^/api/v1': '/v1'
	            }
	        }
	    };
    
	grunt.initConfig({
	  pkg: grunt.file.readJSON('package.json'),

      concat: {
          dist: {
              src: [
                  dir.source + '/app/**/module.js',
                  dir.source + '/app/**/*.js'
              ],
              dest: dir.build + '/js/dashboard.js'
          }
      },
      copy: {
          build: {
              files: [
                  {
                      expand: true,
                      dot: true,
                      cwd: dir.source,
                      dest: dir.build,
                      src: [
                          '*.html',
                          'robots.txt',
                          'config.json'
                      ]
                  },
                  {
                	  expand: true,
                      dot: true,
                      cwd: dir.source + '/theme',
                      dest: dir.build,
                      src: [
                          '**/*.{txt,eot,ttf,woff}'
                      ]
                  },
                  {
                	  expand: true,
                      dot: true,
                      cwd: dir.source + '/theme/js',
                      dest: dir.build + '/js',
                      src: [
                          'jquery.js'
                      ]
                  }
                  ]
          },
      },
      html2js: {
          options: {
              module: 'db.templates',
              base: dir.source
          },
          main: {
              src: [dir.source + '/app/*/template/**/**.html'],
              dest: dir.build + '/js/templates.js'
          }
      },
      
      cssmin: {
    	  build: {
    		  options: {
    			  report: "min"
    		  },
    	    src: [dir.source + '/theme/css/**/*.css'],
    	    dest: dir.build + '/styles/main.css',
    	    }
      },
    	  
      useminPrepare: {
    	  html: [dir.source + '/index.html'],
    	  options: {
    		  dest: dir.build,
    		  flow: {
                  steps: {
                      'js': ['concat'],
                  },
                  post: []
              }
    	    }
    	
      },
      usemin: {
          html: [
              dir.build + '/index.html'
          ],
          options: {
              dirs: [dir.output]
          }
      },
      connect: {
          options: {
              hostname: '0.0.0.0'
          },
          livereload: {
              options: {
                  port: 9000,
                  middleware: function (connect) {
                      return [
                          lrSnippet,
                          mountFolder(connect, dir.build),
                          proxySnippet
                      ];
                  }
              },
              proxies: [proxies.localhost]
          },
          dist: {
              options: {
                  port: 9000,
                  keepalive: true,
                  middleware: function (connect) {
                      return [
                          mountFolder(connect, dir.build),
                          proxySnippet
                      ];
                  }
              },
              proxies: [proxies.localhost]
          }
      },
      open: {
          server: {
              url: 'http://0.0.0.0:9000'
          }
      },
      watch: {
    	  livereload: {
              options: {
                  livereload: config.livereload.port
              },
              files: [
                  dir.source + '/**/*.*'
              ]
          }
      }

	});
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-angular-templates');
  grunt.loadNpmTasks('grunt-html2js');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-usemin');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-connect-proxy');
  grunt.loadNpmTasks('grunt-open');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.registerTask('build', ['html2js','cssmin','useminPrepare','concat','copy','usemin']);
  grunt.registerTask('default', ['html2js','cssmin','useminPrepare','concat','copy','usemin','serve']);
  grunt.registerTask('publish', ['copy']);
  grunt.registerTask('serve', function (target) {
	    grunt.task.run([
'configureProxies:livereload',
'connect:livereload',
'open', 'watch']);
  });
};
