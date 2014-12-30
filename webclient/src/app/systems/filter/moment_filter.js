angular.module('db.systems')
    .filter('moment', 
        function(TimeDateFormatter) {
            return function(dateString) {
                return TimeDateFormatter.getUtc(dateString);
            }
        }
    )