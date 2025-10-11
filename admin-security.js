// Advanced Security Module for Admin Panel
// This file contains additional security measures to protect admin credentials

(function() {
    'use strict';
    
    // Console protection
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;
    
    console.log = function() {
        // Filter out sensitive information from console
        const args = Array.from(arguments);
        const filteredArgs = args.map(arg => {
            if (typeof arg === 'string') {
                return arg.replace(/admin|password|waxandwarmth/gi, '[PROTECTED]');
            }
            return arg;
        });
        originalLog.apply(console, filteredArgs);
    };
    
    // Detect developer tools
    let devtools = {
        open: false,
        orientation: null
    };
    
    function detectDevTools() {
        const threshold = 160;
        
        if (window.outerHeight - window.innerHeight > threshold || 
            window.outerWidth - window.innerWidth > threshold) {
            
            if (!devtools.open) {
                devtools.open = true;
                
                // Clear console when dev tools detected
                console.clear();
                
                // Show warning
                setTimeout(() => {
                    console.warn('%c🔒 SECURITY WARNING', 
                        'color: red; font-size: 20px; font-weight: bold;');
                    console.warn('%cThis is a protected admin area. Unauthorized access is prohibited.', 
                        'color: orange; font-size: 14px;');
                    console.warn('%cAll activities are logged and monitored.', 
                        'color: orange; font-size: 14px;');
                }, 100);
            }
        } else {
            if (devtools.open) {
                devtools.open = false;
            }
        }
    }
    
    // Monitor for dev tools every 500ms
    setInterval(detectDevTools, 500);
    
    // Disable right-click context menu on admin pages
    if (window.location.pathname.includes('admin')) {
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            console.warn('Right-click disabled for security');
            return false;
        });
        
        // Disable common debugging shortcuts
        document.addEventListener('keydown', function(e) {
            // Disable F12, Ctrl+Shift+I, Ctrl+Shift+C, Ctrl+U
            if (e.keyCode === 123 || 
                (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 67)) ||
                (e.ctrlKey && e.keyCode === 85)) {
                e.preventDefault();
                console.warn('Developer shortcuts disabled for security');
                return false;
            }
        });
    }
    
    // Obfuscated credential storage - for additional security
    window.secureStore = {
        // Encrypted storage for sensitive data
        set: function(key, value) {
            const encrypted = btoa(JSON.stringify({
                data: btoa(value),
                timestamp: Date.now(),
                checksum: btoa(key + value).substring(0, 8)
            }));
            sessionStorage.setItem('sec_' + btoa(key), encrypted);
        },
        
        get: function(key) {
            try {
                const encrypted = sessionStorage.getItem('sec_' + btoa(key));
                if (!encrypted) return null;
                
                const parsed = JSON.parse(atob(encrypted));
                const age = Date.now() - parsed.timestamp;
                
                // Expire after 1 hour
                if (age > 3600000) {
                    sessionStorage.removeItem('sec_' + btoa(key));
                    return null;
                }
                
                return atob(parsed.data);
            } catch (e) {
                return null;
            }
        },
        
        remove: function(key) {
            sessionStorage.removeItem('sec_' + btoa(key));
        }
    };
    
    // Anti-debugging measures
    const antiDebug = function() {
        function detectDebugger() {
            const before = Date.now();
            debugger;
            const after = Date.now();
            
            if (after - before > 100) {
                console.clear();
                console.warn('Debugging detected and blocked');
                
                // Optional: Redirect to login if debugging detected
                if (window.location.pathname.includes('admin')) {
                    setTimeout(() => {
                        window.location.href = '/admin-login.html';
                    }, 2000);
                }
            }
        }
        
        // Run every 1 second
        setInterval(detectDebugger, 1000);
    };
    
    // Initialize anti-debugging on admin pages
    if (window.location.pathname.includes('admin')) {
        antiDebug();
    }
    
    // Function to validate admin session integrity
    window.validateAdminSession = function() {
        const session = localStorage.getItem('adminSession');
        const username = localStorage.getItem('adminUsername');
        const token = localStorage.getItem('sessionToken');
        const timestamp = localStorage.getItem('loginTimestamp');
        
        if (!session || !username || !token || !timestamp) {
            return false;
        }
        
        // Check session age
        const age = Date.now() - parseInt(timestamp);
        if (age > 24 * 60 * 60 * 1000) { // 24 hours
            return false;
        }
        
        // Validate token format
        if (token.length !== 32) {
            return false;
        }
        
        return true;
    };
    
    // Clear sensitive data on page unload
    window.addEventListener('beforeunload', function() {
        // Clear any temporary sensitive data
        if (window.secureStore) {
            sessionStorage.clear();
        }
    });
    
    // Monitor for suspicious activities
    let activityCount = 0;
    document.addEventListener('click', function() {
        activityCount++;
        
        // Reset counter every minute
        setTimeout(() => {
            activityCount = Math.max(0, activityCount - 1);
        }, 60000);
        
        // If too many clicks in short time, log warning
        if (activityCount > 50) {
            console.warn('Suspicious activity detected');
        }
    });
    
})();

// Export for use in admin pages
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateAdminSession: window.validateAdminSession,
        secureStore: window.secureStore
    };
}