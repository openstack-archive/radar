angular.module('db.services').factory('Subscription',
    function (ResourceFactory) {
        'use strict';

        return ResourceFactory.build(
            '/subscriptions/:id',
            '/subscriptions/search',
            {id: '@id'}
        );
    });