angular.module('db.services').factory('Operator',
    function (ResourceFactory) {
        'use strict';

        var resource = ResourceFactory.build(
            '/operators/:id',
            '/operators/search',
            {id: '@id'},
            {marker: '@marker'}
        );

        ResourceFactory.applySearch(
            'Operator',
            resource,
            'operator_name',
            {Text: 'q'}
        );

        return resource;
    });