(function() {
    function z(a, b) {
        for (var c in b)
            a.setAttribute(c, b[c])
    }
    function n(a, b) {
        a.onload = function() {
            this.onerror = this.onload = null;
            b(null, a)
        }
        ;
        a.onerror = function() {
            this.onerror = this.onload = null;
            b(Error("Failed to load " + this.src), a)
        }
    }
    function A(a, b) {
        a.onreadystatechange = function() {
            if ("complete" == this.readyState || "loaded" == this.readyState)
                this.onreadystatechange = null,
                b(null, a)
        }
    }
    function p() {}
    function v(a, b, c) {
        for (var d in b)
            !b.hasOwnProperty(d) || void 0 !== a[d] && !0 !== c || (a[d] = b[d]);
        return a
    }
    function B() {
        return "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx".replace(/[xy]/g, function(a) {
            var b = 16 * Math.random() | 0;
            return ("x" === a ? b : b & 3 | 8).toString(16)
        })
    }
    function w(a, b, c) {
        var d = function(a) {
            return a.replace(/(^\/)|(\/$)/g, "")
        };
        b = d(b.replace(/^https?:\/\//i, ""));
        return (c = c ? d(c) : "") ? a + "://" + b + "/" + c : a + "://" + b
    }
    function C(a, b, c) {
        function d() {
            h.parentNode && h.parentNode.removeChild(h);
            window[e] = p;
            l && clearTimeout(l)
        }
        "function" === typeof b && (c = b,
        b = {});
        b || (b = {});
        var e = "__wmjsonp_" + B().slice(2, 9) + D++
          , f = b.param || "cb"
          , g = null != b.timeout ? b.timeout : 6E4;
        b = encodeURIComponent;
        var k = document.getElementsByTagName("script")[0] || document.head, h, l;
        g && (l = setTimeout(function() {
            d();
            c && c(Error("Timeout"))
        }, g));
        window[e] = function(a) {
            d();
            c && c(null, a)
        }
        ;
        g = (new Date).getTime();
        a += (~a.indexOf("?") ? "\x26" : "?") + f + "\x3d" + b(e) + "\x26t\x3d" + g;
        a = a.replace("?\x26", "?");
        h = document.createElement("script");
        h.src = a;
        k.parentNode.insertBefore(h, k);
        return function() {
            window[e] && d()
        }
    }
    function E(a) {
        try {
            var b = localStorage.getItem(a).split(r);
            if (+b.splice(-1) >= t())
                return b.join(r);
            localStorage.removeItem(a);
            return ""
        } catch (c) {
            return ""
        }
    }
    function F(a, b) {
        var c = a.pn
          , d = a.protocol
          , e = a.timeout
          , f = a.__serverConfig__;
        void 0 === f && (f = {});
        c = w(d, f.configServer || "ac.dun.163yun.com", "/v2/config/js?pn\x3d" + c);
        C(c, {
            timeout: e
        }, b)
    }
    function G(a) {
        return {
            start: function() {
                a._start()
            },
            stop: function() {
                a._stop()
            },
            getToken: function(b, c, d) {
                if (!b)
                    throw Error("Missing business key");
                a._getToken(b, c, d)
            },
            getNdInfo: function(b) {
                a._getNdInfo(b)
            },
            getInstance: function() {
                return a
            }
        }
    }
    function H(a, b, c) {
        var d = a.productNumber
          , e = a.merged
          , f = a.pn || d;
        if (!f)
            throw Error("[NEWatchman] required product number");
        d = location.protocol.replace(":", "");
        a = v(v({
            onload: b,
            onerror: c
        }, a), {
            protocol: d,
            auto: !0,
            onload: p,
            onerror: p,
            timeout: 0,
            pn: f
        });
        "http" !== a.protocol && "https" !== a.protocol && (a.protocol = "https");
        if (!e)
            return u(a);
        var g = window.initWatchman.__instances__;
        if (g[f])
            g[f].callback.push(a.onload),
            g[f].instance && (g[f].callback.forEach(function(a) {
                return a(g[f].instance)
            }),
            g[f].callback.length = 0);
        else
            return g[f] = {
                instance: null,
                callback: [a.onload]
            },
            u(a)
    }
    var x = function(a, b, c) {
        var d = document.head || document.getElementsByTagName("head")[0]
          , e = document.createElement("script");
        "function" === typeof b && (c = b,
        b = {});
        b = b || {};
        c = c || function() {}
        ;
        e.type = b.type || "text/javascript";
        e.charset = b.charset || "utf8";
        e.async = "async"in b ? !!b.async : !0;
        e.src = a;
        b.attrs && z(e, b.attrs);
        b.text && (e.text = "" + b.text);
        ("onload"in e ? n : A)(e, c);
        e.onload || n(e, c);
        d.appendChild(e)
    }
      , D = 0
      , r = ","
      , t = function(a) {
        void 0 === a && (a = 0);
        return (new Date).getTime() + parseInt(a, 10)
    }
      , u = function(a) {
        function b(a, b) {
            var c = a.protocol
              , d = a.onerror
              , h = a.__serverConfig__;
            void 0 === h && (h = {});
            var l = a.attrs;
            void 0 === l && (l = {});
            var q = b.split(",")
              , p = q[0]
              , r = q[1]
              , n = q[2]
              , m = v({
                configHash: n,
                lastUsedVersion: q[4],
                sConfig: n,
                staticServer: h.staticServer || p,
                apiServer: h.apiServer || r,
                buildVersion: q[3]
            }, a)
              , h = m.buildVersion + "/watchman.min"
              , t = w(c, m.staticServer) + "/" + h + ".js"
              , u = {
                charset: "UTF-8",
                attrs: l
            }
              , y = function() {
                var a = m.pn
                  , b = m.onload
                  , c = m.merged
                  , d = G(new Watchman(m))
                  , e = window.initWatchman.__instances__;
                c && e[a] ? (e[a].instance = d,
                e[a].callback.forEach(function(a) {
                    return a(d)
                }),
                e[a].callback.length = 0) : b(d)
            };
            x(t, u, function(a) {
                if (!a && window.Watchman)
                    return y();
                x(t, u, function(a) {
                    return !a && window.Watchman ? y() : d("[NEWatchman] load js file error")
                })
            })
        }
        var c = a.merged ? a.pn + ":wm_cf" : "default:wm_cf"
          , d = E(c);
        d ? b(a, d) : F(a, function(d, f) {
            var g = a.onerror;
            if (d)
                return g(Error("[NEWatchman] fetch config timeout"));
            if (f && 200 === f.code) {
                var k = f.result
                  , g = k.ivp
                  , k = [k.s, k.as, k.conf, k.v, k.luv].join();
                try {
                    var h = t(g);
                    localStorage.setItem(c, k + r + h)
                } catch (l) {}
                b(a, k)
            } else
                g(Error("[NEWatchman] fetch config error"))
        })
    };
    window.initWatchman || (window.initWatchman = window.initNEWatchman = H,
    window.initWatchman.version = 6,
    window.initWatchman.__instances__ = {},
    window.initWatchman.__supportCaptcha__ = !0)
}
)();
