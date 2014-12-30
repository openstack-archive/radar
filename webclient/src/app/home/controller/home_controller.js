angular.module('db.home')
    .controller('HomeController',
        function ($state, $log, sessionState, SessionState) {
            'use strict';
            $log.debug('Home Controller loading.  Session state: ' + sessionState);
            // If we're logged in, go to the dashboard instead.
            if (sessionState === SessionState.LOGGED_IN) {
                $state.transitionTo('dashboard');
            }
    })
    
    