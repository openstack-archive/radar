angular.module('db.notification').controller('NotificationsController',
    function ($scope, Notification) {
        'use strict';

        var defaultDisplayCount = 5;

        $scope.displayCount = defaultDisplayCount;

        $scope.notifications = [];

        /**
         * Remove a notification from the display list.
         *
         * @param notification
         */
        $scope.remove = function (notification) {
            var idx = $scope.notifications.indexOf(notification);
            if (idx > -1) {
                $scope.notifications.splice(idx, 1);
            }

            // If the notification list length drops below default, make
            // sure we reset the limit.
            if ($scope.notifications.length <= defaultDisplayCount) {
                $scope.displayCount = defaultDisplayCount;
            }
        };

        /**
         * Reveal more notifications, either current count + 5 or the total
         * number of messages, whichever is smaller.
         */
        $scope.showMore = function () {
            // Set this to something big.
            $scope.displayCount = Math.min($scope.notifications.length,
                    $scope.displayCount + 5);
        };

        /**
         * Set up a notification subscriber, and make sure it's removed when
         * the scope is destroyed.
         */
        $scope.$on('$destroy', Notification.subscribe(
                function (notification) {
                    $scope.notifications.push(notification);
                }
            )
        );
    });