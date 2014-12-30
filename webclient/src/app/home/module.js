angular.module('db.home', ['db.auth', 'db.services', 'ui.router', 'db.header'])
.config(function ($stateProvider, SessionResolver) {
    'use strict';
    $stateProvider
    .state('index', {
        url: '/',
        templateUrl: 'app/home/template/welcome_page.html',
        controller: 'HomeController',        
        resolve: {
            sessionState: SessionResolver.resolveSessionState
        }
    })
})
.run(function ($log, $rootScope, $state) {
    'use strict';
    // Listen to changes on the root scope. If it's an error in the state
    // changes (i.e. a 404) take the user back to the index.
    $rootScope.$on('$stateChangeError',
        function () {
            $state.go('index');
        });
});