angular.module('db.services').factory('Text',
    function (Criteria, $q) {
        'use strict';

        /**
         * Return a text search parameter constructed from the passed search
         * string.
         */
        return {
            criteriaResolver: function (searchString) {
                searchString = 'q=' + searchString;
                var deferred = $q.defer();

                deferred.resolve([Criteria.create('Text', searchString)]);

                return deferred.promise;
            }
        };
    });