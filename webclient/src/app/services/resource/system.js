angular.module('db.services').factory('System',
    function (ResourceFactory) {
        'use strict';

        var resource = ResourceFactory.build(
            '/systems/:id',
            '/systems/search',
            {id: '@id'},
            {marker: '@marker'}
        );

        ResourceFactory.applySearch(
            'System',
            resource,
            'name',
            {Text: 'q'}
        );

        return resource;
    });