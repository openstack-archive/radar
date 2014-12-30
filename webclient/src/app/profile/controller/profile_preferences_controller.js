angular.module('db.profile').controller('ProfilePreferencesController',
    function ($scope, Preference) {
        'use strict';

        $scope.pageSize = Preference.get('page_size');

        $scope.save = function () {
            Preference.set('page_size', $scope.pageSize);
            $scope.message = 'Preferences Saved!';
        };
    });