angular.module('db.profile',
        ['db.services', 'db.templates', 'db.auth', 'ui.router', 'ui.bootstrap']
    )
    .config(function ($stateProvider, SessionResolver, $urlRouterProvider) {
        'use strict';

        // URL Defaults.
        $urlRouterProvider.when('/profile', '/profile/preferences');

        // Declare the states for this module.
        $stateProvider
            .state('profile', {
                abstract: true,
                template: '<div ui-view></div>',
                url: '/profile',
                resolve: {
                    isLoggedIn: SessionResolver.requireLoggedIn,
                    currentUser: SessionResolver.requireCurrentUser
                }
            })
            .state('profile.preferences', {
                url: '/preferences',
                templateUrl: 'app/profile/template/preferences_page.html',
                controller: 'ProfilePreferencesController'
            });
    });