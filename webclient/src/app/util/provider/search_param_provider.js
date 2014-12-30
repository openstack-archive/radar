angular.module('db.util').factory('$searchParams',
    function ($window, UrlUtil) {
        'use strict';

        var params = {};
        var search = $window.location.search;
        if (!!search) {
            if (search.charAt(0) === '?') {
                search = search.substr(1);
            }

            return UrlUtil.deserializeParameters(search);
        }
        return params;
    });