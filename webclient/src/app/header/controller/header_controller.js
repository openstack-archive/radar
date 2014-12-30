angular.module('db.header').controller('HeaderController',
    function ($q, $scope, $rootScope, $state, $location, Session,
              SessionState, CurrentUser, Criteria, Notification, Priority,
              System, Operator) {
        'use strict';

        $scope.isActive = function (viewLocation) { 
            return $location.path().lastIndexOf(viewLocation, 0) === 0;
        }

        function resolveCurrentUser() {
            CurrentUser.resolve().then(
                function (user) {
                    $scope.currentUser = user;
                },
                function () {
                    $scope.currentUser = null;
                }
            );
        }

        resolveCurrentUser();

        /**
         * Load and maintain the current user.
         */
        $scope.currentUser = null;

      

        /**
         * Log out the user.
         */
        $scope.logout = function () {
            Session.destroySession();
        };

        /**
         * Initialize the search string.
         */
        $scope.searchString = '';

        /**
         * Send the user to search and clear the header search string.
         */
        $scope.search = function (criteria) {

            switch (criteria.type) {
                case 'Text':
                    $state.go('search', {q: criteria.value});
                    break;
                case 'System':
                    $state.go('systems.detail', {id: criteria.value});
                    break;
                case 'Operator':
                    $state.go('operators.detail', {id: criteria.value});
                    break;
                
            }

            $scope.searchString = '';
        };

        /**
         * Filter down the search string to actual resources that we can
         * browse to directly (Explicitly not including users here). If the
         * search string is entirely numeric, we'll instead do a
         * straightforward GET :id.
         */
        $scope.quickSearch = function (searchString) {
            var deferred = $q.defer();

            searchString = searchString || '';

            var searches = [];

            if (searchString.match(/^[0-9]+$/)) {
              
                var getSystemDeferred = $q.defer();
                var getOperatorDeferred = $q.defer();
                
                System.get({id: searchString},
                    function (result) {
                        getSystemDeferred.resolve(Criteria.create(
                            'System', result.id, result.name
                        ));
                    }, function () {
                        getSystemDeferred.resolve(null);
                    });
                
                Operator.get({id: searchString},
                        function (result) {
                            getOperatorDeferred.resolve(Criteria.create(
                                'Operator', result.id, result.name
                            ));
                        }, function () {
                            getOperatorDeferred.resolve(null);
                        });

                // If the search string is entirely numeric, do a GET.
                searches.push(getSystemDeferred.promise);
                searches.push(getOperatorDeferred.promise);

            } else {
                searches.push(System.criteriaResolver(searchString, 5));
                searches.push(Operator.criteriaResolver(searchString, 5));

            }
            $q.all(searches).then(function (searchResults) {
                var criteria = [
                    Criteria.create('Text', searchString)
                ];


                /**
                 * Add a result to the returned criteria.
                 */
                var addResult = function (item) {
                    criteria.push(item);
                };

                for (var i = 0; i < searchResults.length; i++) {
                    var results = searchResults[i];

                    if (!results) {
                        continue;
                    }

                    if (!!results.forEach) {

                        // If it's iterable, do that. Otherwise just add it.
                        results.forEach(addResult);
                    } else {
                        addResult(results);
                    }
                }

                deferred.resolve(criteria);
            });

            // Return the search promise.
            return deferred.promise;
        };

        // Watch for changes to the session state.
        Notification.intercept(function (message) {
            switch (message.type) {
                case SessionState.LOGGED_IN:
                    resolveCurrentUser();
                    break;
                case SessionState.LOGGED_OUT:
                    $scope.currentUser = null;
                    break;
                default:
                    break;
            }
        }, Priority.LAST);
    });