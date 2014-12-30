angular.module('db.services').factory('httpCacheHandler',
    function ($q, $cacheFactory) {
        'use strict';

        var $httpDefaultCache = $cacheFactory.get('$http');

        return {
            /**
             * Handle a success response.
             */
            response: function (response) {
                var method = response.config.method;
                var url = response.config.url;
                var obj = response.data;

                // Ignore GET methods.
                switch (method) {
                    case 'POST':
                        if (obj.hasOwnProperty('id')) {
                            $httpDefaultCache.put(url + '/' + obj.id, obj);
                        }
                        break;
                    case 'PUT':
                        $httpDefaultCache.put(url, obj);
                        break;
                    case 'DELETE':
                        $httpDefaultCache.remove(url);
                        break;
                    default:
                        break;
                }

                return response;
            }
        };
    })
    // Attach the HTTP interceptor.
    .config(function ($httpProvider) {
        'use strict';
        $httpProvider.interceptors.push('httpCacheHandler');
    });