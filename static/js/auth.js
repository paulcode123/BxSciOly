/**
 * Authentication and session management
 */
document.addEventListener('DOMContentLoaded', function() {
    // Sync client-side session with server-side session
    syncSession();
});

// Function to sync client session with server
function syncSession() {
    const currentUser = JSON.parse(sessionStorage.getItem('currentUser'));
    
    if (currentUser) {
        // Set cookie for server access
        document.cookie = `currentUser=${JSON.stringify(currentUser)}; path=/; max-age=86400`;
        
        // Also sync with Flask's server-side session
        fetch('/api/auth/sync-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.uid}`
            },
            body: JSON.stringify({
                user: currentUser
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Session synced with server');
        })
        .catch(error => {
            console.error('Error syncing session:', error);
        });
    }
} 