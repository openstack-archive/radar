angular.module('db.util', ['ui.router', 'LocalStorageModule', 'angularMoment'])
    .run(function () {
        'use strict';
        angular.element.prototype.hide = function () {
            this.addClass('ng-hide');
        };

        angular.element.prototype.show = function () {
            this.removeClass('ng-hide');
        };
    });