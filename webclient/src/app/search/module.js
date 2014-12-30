angular.module('db.search',
    ['ui.router', 'db.services', 'db.util', 'db.auth'])
    .config(function ($stateProvider) {
        'use strict';

        // Set our page routes.
        $stateProvider
            .state('search', {
                url: '/search?q',
                templateUrl: 'app/search/template/index.html'
            });
    });