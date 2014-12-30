/**
 * A directive that displays a list of projects in a table.
 *
 * @see ProjectListController
 */
angular.module('db.search').directive('searchResults',
    function ($log, $parse, Criteria, $injector) {
        'use strict';

        return {
            restrict: 'A',
            scope: true,
            link: function ($scope, $element, args) {

                // Extract the resource type.
                var resourceName = args.searchResource;
                var pageSize = args.searchPageSize || 20;

                $scope.isSearching = false;
                $scope.searchResults = [];

                // Watch for changing criteria
                $scope.$watchCollection($parse(args.searchCriteria),
                    function (criteria) {

                        // Extract the valid critera from the provided ones.
                        $scope.validCriteria = Criteria
                            .filterCriteria(resourceName, criteria);

                        // You have criteria, but they may not be valid.
                        $scope.hasCriteria = criteria.length > 0;

                        // You have criteria, and all of them are valid for
                        // this resource.
                        $scope.hasValidCriteria =
                            $scope.validCriteria.length ===
                            criteria.length && $scope.hasCriteria;

                        // No need to search if our criteria aren't valid.
                        if (!$scope.hasValidCriteria) {
                            $scope.searchResults = [];
                            $scope.isSearching = false;
                            return;
                        }

                        var params = Criteria.mapCriteria(resourceName,
                            $scope.validCriteria);
                        var resource = $injector.get(resourceName);

                        if (!resource) {
                            $log.error('Invalid resource name: ' +
                                resourceName);
                            return;
                        }

                        // Apply paging.
                        params.limit = pageSize;

                        resource.query(params,
                            function (results) {
                                $scope.searchResults = results;
                                $scope.isSearching = false;
                            },
                            function () {
                                $scope.isSearching = false;
                            }
                        );
                    });
            }
        };
    });