angular.module('db.util').factory('TimeDateFormatter', 
	function () {

        'use strict';
        return {
            getUtc: function(input) {
            	return  moment(input, moment.ISO_8601).utc().format("YYYY-MM-DD HH:mm:ss") + ' UTC'
            }
        }
});
   