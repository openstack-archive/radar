angular.module('db.util').factory('StringUtil',
    function () {
        'use strict';

        var defaultLength = 32; // MD5 length. Seems decent.
        var alphaNumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
            'abcdefghijklmnopqrstuvwxyz' +
            '0123456789';

        return {
            /**
             * Helper to generate a random alphanumeric string for the state
             * parameter.
             *
             * @param length The length of the string to generate.
             * @returns {string} A random alphanumeric string.
             */
            randomAlphaNumeric: function (length) {
                return this.random(length, alphaNumeric);
            },

            /**
             * Helper to generate a random string of specified length, using a
             * provided list of characters.
             *
             * @param length The length of the string to generate.
             * @param characters The list of valid characters.
             * @returns {string} A random string composed of provided
             * characters.
             */
            random: function (length, characters) {
                length = length || defaultLength;
                characters = characters || alphaNumeric;

                var text = '';

                for (var i = 0; i < length; i++) {
                    text += characters.charAt(Math.floor(
                            Math.random() * characters.length));
                }

                return text;
            }
        };
    }
);
