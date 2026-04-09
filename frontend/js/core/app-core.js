// Core app state and lightweight orchestration module
// This module introduces a minimal core registry and makes the
// main app structure easier to compose with higher-level modules.
// It intentionally avoids changing existing runtime behavior.
(function(){
    'use strict';
    // Defer initialization until the global app instance exists
    const ensureApp = () => {
        if (typeof window.app === 'undefined') {
            setTimeout(ensureApp, 50);
            return;
        }
        // Attach a lightweight core registry to the app instance
        if (!window.app.core) {
            window.app.core = {
                initializedAt: Date.now(),
                modules: {}
            };
            console.log('[app-core] Initialized core registry on app instance');
        }
    };
    ensureApp();
})();
