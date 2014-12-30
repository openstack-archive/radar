angular.module('db.systems')
    .factory('SystemsFactory', 
        function ($log, $q, $http) {
            var initialized=0;
            var marker=0
            $log.debug('loading systems service')
            return {
                getData: function (resource, marker) {
                    var deferred = $q.defer();
                    if (initialized == 0 ) {
                    resource.browse(
                        function (result) {
                            deferred.resolve(result);
                        }, function () {
                            deferred.resolve([]);
                        }
                    );
                    initialized = 1;                    
                
                }
                else {
                    resource.browse({marker: marker},
                            function (result) {                            
                                deferred.resolve(result);
                            }, function () {
                                deferred.resolve([]);
                            }
                        );
                }
                return deferred.promise;

            },
            
            getCount: function() {
                var deferred = $q.defer();
                $http.get('/api/v1/systems/count/')
                .then(function (result) {
                        deferred.resolve(result)
                    },
                 function (error) {
                        // We've encountered an error.
                        $log.debug('error: ' + error)

                        deferred.resolve([]);

                    })
                    return deferred.promise;
            },
            
            updateMarker: function(newMarker) {
                var deferred = $q.defer();
                deferred.promise.then(function() {
                    marker = newMarker;
                    $log.debug('marker: ' + marker)
                });
                deferred.resolve();
                return deferred.promise;
            }
        }
    })