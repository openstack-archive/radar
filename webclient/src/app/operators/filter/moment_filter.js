angular.module('db.operators')
    .filter('moment', 
        function(TimeDateFormatter) {
            return function(dateString) {
                return TimeDateFormatter.getUtc(dateString);
            }
        }
    )