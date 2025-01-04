/*
 * NAME
 *   js_sprintf-1.0.1.js
 * DESCRIPTION
 *   sprintf() function for JavaScript
 * AUTHOR
 *   Tohoho <tohoho@cat.memail.jp>
 * WEBSITE
 *   http://www.tohoho-web.com/tech/js_sprintf.html
 * COPYRIGHT
 *   Copyright(C) 2015 Tohoho
 * LICENSE
 *   This software is released under the MIT License, see LICENSE.txt.
 * DATE
 *   2015-09-23
 */
String.sprintf = function(format) {
    var argc = 1;
    var ret = "";
    for (var i = 0; i < format.length; i++) {
        var c = format.substr(i, 1);
        if (c !== "%") {
            ret += c;
            continue;
        }
        var str = "";
        var exp = "";
        if (!format.substr(i).match(/(%([-\+ #0]*)(\d*)(\.|)(\d*)(hh|h|l|ll|j|z|t|L|)(.))/)) {
            ret += c;
            continue;
        }
        var all = RegExp.$1 ? RegExp.$1 : "";
        var flag = RegExp.$2 ? RegExp.$2 : "";
        var n1 = RegExp.$3 ? RegExp.$3 : 0;
        var dot = RegExp.$4 ? RegExp.$4 : "";
        var n2 = RegExp.$5 ? RegExp.$5 : -1;
        var len = RegExp.$6 ? RegExp.$6 : "";
        var type = RegExp.$7 ? RegExp.$7 : "";
        if (type === "c") {
            str = String.fromCharCode(arguments[argc++]);
        } else if (type === "%") {
            str = "%";
        } else if (type === "s") {
            str = arguments[argc++].toString();
            if (n2 > 0) {
                str = str.substr(0, n2);
            }
            if (flag.match(/0/) && !flag.match(/-/)) {
                for (var j = str.length; j < n1; j++) {
                    str = "0" + str;
                }
            }
        } else if (type.match(/[diuox]/)) {
            var sign = "";
            var num = parseInt(arguments[argc++]);
            num = isNaN(num) ? 0 : num;
            if ((type === "d") || (type === "i")) {
                if (num < 0) {
                    sign = "-";
                    num = num * -1;
                } else if (flag.match(/\+/)) {
                    sign = "+";
                }
                str = num.toString();
            } else if (type === "u") {
                str = (num >>> 0).toString();
            } else if (type === "o") {
                str = (num >>> 0).toString(8);
            } else if ((type === "x") || (type === "X")) {
                str = (num >>> 0).toString(16);
            }
            if (flag.match(/0/)) {
                for (var j = str.length; j < (sign ? n1 - 1 : n1); j++) {
                    str = "0" + str;
                }
            }
            for (var j = str.length; j < (sign ? n2 - 1 : n2); j++) {
                str = "0" + str;
            }
            str = sign + str;
        } else if (type.match(/[eEfFgG]/)) {
            if (n2 == -1) {
                n2 = 6;
            }
            var str2 = arguments[argc++].toString();
            if (!str2.match(/^([-\+]?)(\d*)(\.|)(\d*)([eE]?)([-+]?\d*)$/)) {
                continue;
            } 
            var sign = RegExp.$1;
            var num1 = RegExp.$2;
            var num2 = RegExp.$4;
            var num3 = "";
            var pnt = ".";
            var exp = RegExp.$6 ? parseInt(RegExp.$6) : 0;
            if (type.match(/[eEgG]/)) {
                if (num1 >= 10) {
                    var e = num1.length - 1;
                    num2 = num1.substr(1) + num2;
                    num1 = num1.substr(0, 1);
                    exp += e;
                } else if (num1 == 0) {
                    var e = num2.match(/^(0+)/) ? RegExp.$1.length + 1 : 1;
                    num1 = num2.substr(e - 1, 1);
                    num2 = num2.substr(e);
                    exp -= e;
                }
            } else if (type.match(/[fF]/)) {
                for (; exp > 0; exp--) {
                    if (num2 != "") {
                        num1 = num1 + num2.substr(0, 1);
                        num2 = num2.substr(1);
                    } else {
                        num1 = num1 + "0";
                    }
                }
                for (; exp < 0; exp++) {
                    if (num1 != "") {
                        num2 = num1.substr(-1, 1) + num2;
                        num1 = num1.substr(0, num1.length - 1);
                    } else {
                        num2 = "0" + num2;
                    }
                }
                if (num1 == "") {
                    num1 = "0";
                }
            }
            num3 = num2.substr(n2);
            num2 = num2.substr(0, n2);
            if (!num3.match(/^(|[01234].*|50*)$/)) {
                if (num2 == "") {
                    num1++;
                } else {
                    num2++;
                }
            }
            for (var j = num2.length; j < n2; j++) {
                num2 = num2 + "0";
            }
            if ((sign !== "-") && flag.match(/\+/)) {
                sign = "+";
            }
            if (type.match(/[eEgG]/)) {
                if (exp >= 10) {
                    exp = "+" + exp;
                } else if (exp >= 0) {
                    exp = "+0" + exp;
                } else if (exp > -10) {
                    exp = "-0" + (-exp).toString();
                } else {
                    exp = exp.toString();
                }
            }
            if (num2 === "") {
                pnt = "";
            }
            if (type.match(/[eg]/)) {
                exp = "e" + exp;
            } else if (type.match(/[EG]/)) {
                exp = "E" + exp;
            } else if (type.match(/[fF]/)) {
                exp = "";
            }
            for (var j = (sign + num1 + pnt + num2 + exp).length; j < n1; j++) {
                if (flag.match(/0/)) {
                    num1 = "0" + num1;
                }
            }
            str = sign + num1 + pnt + num2 + exp;
            for (var j = str.length; j < n1; j++) {
                if (flag.match(/-/)) {
                    str = str + " ";
                } else {
                    str = " " + str;
                }
            }
        } else {
            str = all;
        }
        if (flag.match(/-/)) {
            for (var j = str.length; j < n1; j++) {
                str = str + " ";
            }
        } else {
            for (var j = str.length; j < n1; j++) {
                str = " " + str;
            }
        }
        ret += str;
        i += all.length - 1;
    }
    return ret.toString();
}

