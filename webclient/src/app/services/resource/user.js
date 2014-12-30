angular.module('db.services').factory('User',
    function (ResourceFactory) {
        'use strict';

        var resource = ResourceFactory.build(
            '/users/:id',
            '/users/search',
            {id: '@id'}
        );

        ResourceFactory.applySearch(
            'User',
            resource,
            'full_name',
            {Text: 'q'}
        );

        return resource;
    });