angular.module('db.systems').controller('EventFilterController',
    function($scope, $modalInstance, Preference) {
        'use strict';

        function init() {
            $scope.enabled_event_types =
                Preference.get('display_events_filter');
        }

        $scope.close = function () {
            $modalInstance.dismiss('cancel');
        };

        $scope.save = function () {
            Preference.set('display_events_filter',
                           $scope.enabled_event_types);
            return $modalInstance.close($scope.enabled_event_types);
        };

        init();

    })
;
