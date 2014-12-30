angular.module('db.util')
.factory('Marker', 
    function ($log) {

        'use strict';
        return {
            /**
             * Helper to generate a random alphanumeric string for the state
             * parameter.
             *
             * @param length The length of the string to generate.
             * @returns {string} A random alphanumeric string.
             */
         
            setMarker: function(input) {
                var first = input[0];
                $log.debug('marker: ' + first.id)
                return first.id;
            }
        

        }
});