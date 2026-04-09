// Project management module (public API surface on app)
// Exposes a structured namespace that delegates to existing app methods
// to preserve current behavior while enabling a modular architecture.
(function(){
    'use strict';
    const ensureApp = () => {
        if (typeof window.app === 'undefined') {
            setTimeout(ensureApp, 50);
            return;
        }
        if (!window.app.projectManager) {
            window.app.projectManager = {
                // Delegations to existing App methods
                newProject: () => window.app.newProject(),
                openProject: () => window.app.openProject(),
                saveProject: () => window.app.saveProject(),
                refreshProjectFiles: () => window.app.refreshProjectFiles?.(),
                loadProject: (index) => window.app.loadProject(index)
            };
            console.log('[project-manager] Bound projectManager API to app');
        }
    };
    ensureApp();
})();
