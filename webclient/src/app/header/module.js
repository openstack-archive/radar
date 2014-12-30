angular.module('db.header', ['db.auth'])

.config(function ($stateProvider, SessionResolver) {
    'use strict';
    $stateProvider
    .state('index.header', {
        views: {
            "header@": {
                templateUrl: 'app/header/template/header_menu.html',
                controller: 'HeaderController',        
                resolve: {
                    sessionState: SessionResolver.resolveSessionState
                }
            },
        },
        
    })
})