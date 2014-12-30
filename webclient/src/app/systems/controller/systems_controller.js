angular.module('db.systems')
.controller('SystemsListController',
    function ($scope, $q, $log, System, ngTableParams, Preference, $http, SystemsFactory, Marker) {
        'use strict';
        $scope.count=0;
        $scope.data = []
        var marker=0;
        $log.debug('loading systems');
        $scope.pageSize = Preference.get('page_size');
        var deferred = $q.defer();

        var promise = SystemsFactory.getCount()
        promise.then(
               function (payload) {
                   $scope.count = payload.data;
                   deferred.resolve(payload.data)
               },

               function (errorPayload) {
                   $log.error('failure loading count', errorPayload);
               }
        )
        .then(function () { 
            $scope.tableParams = new ngTableParams({
                        page: 1,            // show first page
                        count: $scope.pageSize         // count per page
                    }, {
                        counts: [],
                        total: $scope.count, // length of data
                        getData: function($defer, params) {
                            marker = (params.page() - 1) * params.count()
                            var updatePromise = SystemsFactory.updateMarker(marker)
                            updatePromise.then(
                                    function(data) {
                                        $log.debug('resolved marker')
                                    },
                                    function(error) {
                                        $log.debug('failed resolving marker: ' + error)
                                    })
                            var promise = SystemsFactory.getData(System, marker)
                            promise.then(
                               function (data) { 
                                   $defer.resolve(data)
                               },
                               function (errorPayload) {
                                   $log.error('failure loading system', errorPayload);
                               })
                        }
                    }
            )
        },
       
        function (errorPayload) {
            $log.error('failure loading system', errorPayload);
        })

	})