angular.module('db.operators')
    .factory('OperatorsFactory', 
        function ($log, $q, $http, Marker) {
            var initialized=0;
            var baseMarker=0
            var marker=0
            $log.debug('loading operators service')
            return {
                getData: function (resource) {
                    var deferred = $q.defer();
                    if (initialized == 0 ) {
                    resource.browse(
                        function (result) {
                            baseMarker = Marker.setMarker(result)
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
                $http.get('/api/v1/operators/count/')
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
                    marker = baseMarker + newMarker;
                    $log.debug('marker: ' + marker)
                });
                deferred.resolve();
                return deferred.promise;
            }
           
        }
    })