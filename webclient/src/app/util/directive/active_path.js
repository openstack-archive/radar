angular.module('db.util').directive('activePath',
    function ($location, $rootScope) {
        'use strict';

        return {
            link: function ($scope, element, attrs) {
                var activePath = attrs.activePath;

                function setActivePath() {
                    var path = $location.path();
                    var isMatchedPath = path.match(activePath) !== null;

                    element.toggleClass('active', isMatchedPath);
                }

                // This is angularjs magic, the return method from any $on
                // binding will return a function that will disconnect
                // that binding.
                var disconnectBinding =
                    $rootScope.$on('$stateChangeSuccess', setActivePath);
                $scope.$on('$destroy', disconnectBinding);

                // INIT
                setActivePath();
            }
        };
    });