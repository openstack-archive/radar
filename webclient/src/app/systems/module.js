angular.module('db.systems', ['ui.router', 'db.services', 'db.util', 'db.auth',
                              'ngTable'])
    .config(function ($stateProvider, $urlRouterProvider, SessionResolver) {
        'use strict';
        
        $urlRouterProvider.when('/systems', '/systems/list');

        // Set our page routes.
        $stateProvider
            .state('systems', {
                abstract: true,
                url: '/systems',
                template: '<div ui-view></div>',
                resolve: {
                    sessionState: SessionResolver.requireLoggedIn,
                    currentUser: SessionResolver.requireCurrentUser
                }
            })
            .state('systems.list', {
                url: '/list',
                templateUrl: 'app/systems/template/systems_list.html',
                controller: 'SystemsListController'
            })
            .state('systems.detail', {
                url: '/{id:[0-9]+}',
                templateUrl: 'app/systems/template/system_detail.html'
            });
    })