angular.module('db.services')
    .service('ResourceFactory',
    function ($q, $log, $injector, Criteria, $resource, radarApiBase,
              Preference) {
        'use strict';

        /**
         * This method is used in our API signature to return a recent value
         * for the user's pageSize preference.
         *
         * @returns {*}
         */
        function getLimit() {
            return Preference.get('page_size');

        }

        /**
         * Construct a full API signature for a specific resource. Includes
         * CRUD, Browse, and Search. If the resource doesn't support it,
         * don't use it :).
         *
         * @param searchUrl
         * @returns An API signature that may be used with a $resource.
         */
        function buildSignature(searchUrl) {
            return {
                'create': {
                    method: 'POST'
                },
                'read': {
                    method: 'GET',
                    cache: false
                },
                'update': {
                    method: 'PUT'
                },
                'delete': {
                    method: 'DELETE'
                },
                'browse': {
                    method: 'GET',
                    isArray: true,
                    responseType: 'json',
                    params: {
                        limit: getLimit
                    }
                },
                'search': {
                    method: 'GET',
                    url: searchUrl,
                    isArray: true,
                    responseType: 'json',
                    params: {
                        limit: getLimit
                    }
                }
            };
        }


        return {

            /**
             * Build a resource URI.
             *
             * @param restUri
             * @param searchUri
             * @param resourceParameters
             * @returns {*}
             */
            build: function (restUri, searchUri, resourceParameters) {

                if (!restUri) {
                    $log.error('Cannot use resource factory ' +
                        'without a base REST uri.');
                    return null;
                }

                var signature = buildSignature(radarApiBase + searchUri);
                return $resource(radarApiBase + restUri,
                    resourceParameters, signature);
            },

            /**
             * This method takes an already configured resource, and applies
             * the static methods necessary to support the criteria search API.
             * Browse parameters should be formatted as an object containing
             * 'injector name': 'param'. For example, {'Project': 'project_id'}.
             *
             * @param resourceName The explicit resource name of this resource
             * within the injection scope.
             * @param resource The configured resource.
             * @param nameField The name field to use while browsing criteria.
             * @param searchParameters The search parameters to apply.
             */
            applySearch: function (resourceName, resource, nameField,
                                   searchParameters) {

                // List of criteria resolvers which we're building.
                var criteriaResolvers = [];

                for (var type in searchParameters) {

                    // If the requested type exists and has a criteriaResolver
                    // method, add it to the list of resolvable browse criteria.
                    var typeResource = $injector.get(type);
                    if (!!typeResource &&
                        typeResource.hasOwnProperty('criteriaResolver')) {
                        criteriaResolvers.push(typeResource.criteriaResolver);
                    }
                }

                /**
                 * Return a list of promise-returning methods that, given a
                 * browse string, will provide a list of search criteria.
                 *
                 * @returns {*[]}
                 */
                resource.criteriaResolvers = function () {
                    return criteriaResolvers;
                };


                // If we found a browse parameter, add the ability to use
                // this resource as a source of criteria.
                if (!!nameField) {
                    /**
                     * Add the criteria resolver method.
                     */
                    resource.criteriaResolver =
                        function (searchString, pageSize) {
                            pageSize = pageSize || Preference.get('page_size');

                            var deferred = $q.defer();

                            // build the query parameters.
                            var queryParams = {};
                            queryParams[nameField] = searchString;
                            queryParams.limit = pageSize;

                            resource.query(queryParams,
                                function (result) {
                                    // Transform the results to criteria tags.
                                    var criteriaResults = [];
                                    result.forEach(function (item) {
                                        criteriaResults.push(
                                            Criteria.create(resourceName,
                                                item.id,
                                                item[nameField])
                                        );
                                    });
                                    deferred.resolve(criteriaResults);
                                }, function () {
                                    deferred.resolve([]);
                                }
                            );

                            return deferred.promise;
                        };
                }


                /**
                 * The criteria filter.
                 */
                resource.criteriaFilter = Criteria
                    .buildCriteriaFilter(searchParameters);

                /**
                 * The criteria map.
                 */
                resource.criteriaMap = Criteria
                    .buildCriteriaMap(searchParameters);

            }
        };
    });