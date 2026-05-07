/**
 * Client-side login storage: session tab vs persistent "remember me".
 */
(function () {
    var KEY = 'currentUser';

    function getRaw() {
        return sessionStorage.getItem(KEY) || localStorage.getItem(KEY);
    }

    function parseUser() {
        var s = getRaw();
        return s ? JSON.parse(s) : null;
    }

    function isRemembered() {
        return !!localStorage.getItem(KEY);
    }

    function clearAdminSessionKeys() {
        sessionStorage.removeItem('adminId');
        sessionStorage.removeItem('adminRole');
        sessionStorage.removeItem('adminPermissions');
        sessionStorage.removeItem('adminUserInfo');
        sessionStorage.removeItem('admin_token');
    }

    /** Populate admin API session from main login (full admins only). */
    function syncAdminSessionFromUser() {
        var u = parseUser();
        if (u && u.adminStatus === 'full') {
            var id = u.id || u.uid;
            sessionStorage.setItem('adminId', id);
            sessionStorage.setItem('adminRole', u.adminStatus);
            sessionStorage.setItem('adminPermissions', JSON.stringify(['all']));
            sessionStorage.setItem(
                'adminUserInfo',
                JSON.stringify({
                    firstName: u.firstName,
                    lastName: u.lastName,
                    email: u.doeEmail || u.email || '',
                })
            );
        } else {
            clearAdminSessionKeys();
        }
    }

    function setUser(userObj, remember) {
        var jsonStr = typeof userObj === 'string' ? userObj : JSON.stringify(userObj);
        if (remember) {
            localStorage.setItem(KEY, jsonStr);
            sessionStorage.removeItem(KEY);
        } else {
            sessionStorage.setItem(KEY, jsonStr);
            localStorage.removeItem(KEY);
        }
    }

    function clearUser() {
        sessionStorage.removeItem(KEY);
        localStorage.removeItem(KEY);
        document.cookie = 'currentUser=; path=/; max-age=0';
        clearAdminSessionKeys();
    }

    function getLoginRedirectUrl() {
        return '/login?redirect=' + encodeURIComponent(window.location.pathname + window.location.search);
    }

    function syncSession() {
        var currentUser = parseUser();
        if (!currentUser) {
            return;
        }
        var maxAge = isRemembered() ? 2592000 : 86400;
        document.cookie =
            'currentUser=' +
            encodeURIComponent(JSON.stringify(currentUser)) +
            '; path=/; max-age=' +
            maxAge;

        fetch('/api/auth/sync-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: 'Bearer ' + currentUser.uid,
            },
            body: JSON.stringify({ user: currentUser }),
        })
            .then(function (r) {
                return r.json();
            })
            .then(function () {
                console.log('Session synced with server');
            })
            .catch(function (err) {
                console.error('Error syncing session:', err);
            });
    }

    syncAdminSessionFromUser();

    document.addEventListener('DOMContentLoaded', function () {
        syncAdminSessionFromUser();
        syncSession();
    });

    window.BxSciOlyAuth = {
        getRaw: getRaw,
        parseUser: parseUser,
        setUser: setUser,
        clearUser: clearUser,
        isRemembered: isRemembered,
        syncAdminSessionFromUser: syncAdminSessionFromUser,
        getLoginRedirectUrl: getLoginRedirectUrl,
    };
})();
