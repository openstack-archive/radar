angular.module('db.root',
    ['db.services', 'db.templates', 'db.header', 'db.home', 'db.dashboard', 
     'db.pages', 'db.auth', 'db.systems', 'db.operators', 'db.profile', 'db.notification', 
     'db.search', 'ui.router', 'ui.bootstrap', 'angular-data.DSCacheFactory',
     'angularMoment', 'angulartics', 'angulartics.google.analytics'])
      
    .config(function ($urlRouterProvider, $locationProvider,
                      $httpProvider) {
        'use strict';

        // Default URL hashbang route
        $urlRouterProvider.otherwise('/');

        // Override the hash prefix for Google's AJAX crawling.
        $locationProvider.hashPrefix('!');

        // Attach common request headers out of courtesy to the API
        $httpProvider.defaults.headers.common['X-Client'] = 'Dashboard';

    })
