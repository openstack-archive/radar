angular.module('db.operators').controller('OperatorDetailController',
    function ($scope, $rootScope, $state, $stateParams, Operator,
              Session) {
        'use strict';

        // Parse the ID
        var id = $stateParams.hasOwnProperty('id') ?
            parseInt($stateParams.id, 10) :
            null;

        /**
         * The Operator we're manipulating right now.
         *
         * @type Operator
         */
        $scope.Operator = {};

        /**
         * UI flag for when we're initially loading the view.
         *
         * @type {boolean}
         */
        $scope.isLoading = true;

        /**
         * UI view for when a change is round-tripping to the server.
         *
         * @type {boolean}
         */
        $scope.isUpdating = false;

        /**
         * Any error objects returned from the services.
         *
         * @type {{}}
         */
        $scope.error = {};

        /**
         * Generic service error handler. Assigns errors to the view's scope,
         * and unsets our flags.
         */
        function handleServiceError(error) {
            // We've encountered an error.
            $scope.error = error;
            $scope.isLoading = false;
            $scope.isUpdating = false;
        }

        /**
         * Resets our loading flags.
         */
        function handleServiceSuccess() {
            $scope.isLoading = false;
            $scope.isUpdating = false;
        }

        /**
         * Load the Operator
         */
        function loadOperator() {
            Operator.get(
                {'id': id},
                function (result) {
                    // We've got a result, assign it to the view and unset our
                    // loading flag.
                    $scope.Operator = result;

                    handleServiceSuccess();
                },
                handleServiceError
            );
        }

        loadOperator();
    });