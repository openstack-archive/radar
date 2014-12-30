angular.module('db.operators')
.controller('OperatorsListController',
    function ($scope, $q, $log, Operator, ngTableParams, Preference, $http, OperatorsFactory, Marker) {
        'use strict';
        $scope.count=0;
        $scope.data = []
        var marker=0;
        $log.debug('loading operators');
        $scope.pageSize = Preference.get('page_size');
        var deferred = $q.defer();

        var promise = OperatorsFactory.getCount()
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
                            var updatePromise = OperatorsFactory.updateMarker(marker)
                            updatePromise.then(
                                    function(data) {
                                        $log.debug('resolved marker')
                                    },
                                    function(error) {
                                        $log.debug('failed resolving marker: ' + error)
                                    }).then(function() {
                            var promise = OperatorsFactory.getData(Operator, marker)
                            promise.then(
                               function (data) { 
                                   $defer.resolve(data)
                               },
                               function (errorPayload) {
                                   $log.error('failure loading operators', errorPayload);
                               })})
                        }
                    }
            )
        },
       
        function (errorPayload) {
            $log.error('failure loading operator', errorPayload);
        })

	})