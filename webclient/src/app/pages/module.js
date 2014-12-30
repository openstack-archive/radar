angular.module('db.pages',
        [ 'db.services', 'db.templates', 'db.pages', 'ui.router']
    )
    .config(function ($stateProvider) {
        'use strict';

        // Set our page routes.
        $stateProvider
            .state('page', {
                abstract: true,
                url: '/page',
                template: '<div ui-view></div>'
            })
            .state('page.about', {
                url: '/about',
                templateUrl: 'app/pages/template/about.html'
            });
    });