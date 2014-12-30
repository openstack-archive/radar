angular.module('db.dashboard', ['db.auth', 'ui.router'])
.config(function ($stateProvider, SessionResolver) {
    'use strict';
    $stateProvider
    .state('dashboard', {
        url: '/dashboard',
        templateUrl: 'app/dashboard/template/dashboard_index.html',
        controller: 'DashboardController',
        resolve: {
            sessionState: SessionResolver.requireLoggedIn,
            currentUser: SessionResolver.requireCurrentUser
        }
    })
})