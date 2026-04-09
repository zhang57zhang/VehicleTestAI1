// Page rendering module: delegates to existing app render methods
(function(){
    'use strict';
    const ensureApp = () => {
        if (typeof window.app === 'undefined') {
            setTimeout(ensureApp, 50);
            return;
        }
        if (!window.app.pageRenderer) {
            window.app.pageRenderer = {
                renderPage: (pageId) => window.app.renderPage(pageId),
                renderTabs: () => window.app.renderTabs(),
                switchTab: (pageId) => window.app.switchTab(pageId),
                renderProjectTree: () => window.app.renderProjectTree(),
                renderProjectList: (projects) => window.app.renderProjectList?.(projects)
            };
            console.log('[page-renderer] Bound page rendering API to app');
        }
    };
    ensureApp();
})();
