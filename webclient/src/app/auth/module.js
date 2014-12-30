angular.module('db.auth', [ 'db.services', 'db.templates', 'ui.router',
        'db.util', 'LocalStorageModule'])
    .config(function ($stateProvider, SessionResolver) {
        'use strict';

        // Declare the states for this module.
        $stateProvider
            .state('auth', {
                abstract: true,
                template: '<div ui-view></div>',
                url: '/auth'
            })
            .state('auth.authorize', {
                url: '/authorize?error&error_description',
                templateUrl: 'app/auth/template/busy.html',
                controller: 'AuthAuthorizeController',
                resolve: {
                    isLoggedOut: SessionResolver.requireLoggedOut
                }
            })
            .state('auth.deauthorize', {
                url: '/deauthorize',
                templateUrl: 'app/auth/template/busy.html',
                controller: 'AuthDeauthorizeController',
                resolve: {
                    isLoggedIn: SessionResolver.requireLoggedIn
                }
            })
            .state('auth.token', {
                url: '/token?code&state&error&error_description',
                templateUrl: 'app/auth/template/busy.html',
                controller: 'AuthTokenController',
                resolve: {
                    isLoggedOut: SessionResolver.requireLoggedOut
                }
            })
            .state('auth.error', {
                url: '/error?error&error_description',
                templateUrl: 'app/auth/template/error.html',
                controller: 'AuthErrorController'
            });
    })
    .run(function ($rootScope, SessionState, Session, PermissionManager,
                   RefreshManager, Notification, Priority) {
        'use strict';

        // Initialize our permission manager.
        PermissionManager.initialize();

        // Always record the logged in state on the root scope.
        Notification.intercept(function (message) {
            switch (message.type) {
                case SessionState.LOGGED_IN:
                    $rootScope.isLoggedIn = true;
                    break;
                case SessionState.LOGGED_OUT:
                    $rootScope.isLoggedIn = false;
                    break;
                default:
                    break;
            }
        }, Priority.LAST);

        RefreshManager.scheduleRefresh();
    });