angular.element(document)
.ready(function () {
    'use strict';

    var initInjector = angular.injector(['ng']);
    var $http = initInjector.get('$http');
    var $log = initInjector.get('$log');

    function initializeApplication(config) {
        // Load everything we got into our module.
        for (var key in config) {
            $log.debug('Configuration: ' + key + ' -> ' + config[key]);
            angular.module('db.root').constant(key, config[key]);
        }
        $log.debug('angular bootstrap')
        angular.bootstrap(document, ['db.root']);
    }

    $log.info('Attempting to load parameters from ./config.json');
    $http.get('./config.json').then(
        function (response) {
            initializeApplication(response.data);
        },
        function () {
            $log.warn('Cannot load ./config.json, using defaults.');
            initializeApplication({});
        }
    );
}
);
