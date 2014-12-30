angular.module('db.operators', ['ui.router', 'db.services', 'db.util', 'db.auth',
                              'ngTable'])
    .config(function ($stateProvider, $urlRouterProvider, SessionResolver) {
        'use strict';
        
        $urlRouterProvider.when('/operators', '/operators/list');

        // Set our page routes.
        $stateProvider
            .state('operators', {
                abstract: true,
                url: '/operators',
                template: '<div ui-view></div>',
                resolve: {
                    sessionState: SessionResolver.requireLoggedIn,
                    currentUser: SessionResolver.requireCurrentUser
                }
            })
            .state('operators.list', {
                url: '/list',
                templateUrl: 'app/operators/template/operator_list.html',
                controller: 'OperatorsListController'
            })
            .state('operators.detail', {
                url: '/{id:[0-9]+}',
                templateUrl: 'app/operators/template/operator_detail.html'
            });
    })