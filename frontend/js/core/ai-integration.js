// AI integration module: exposes AI-related actions via app.aiIntegration
(function(){
    'use strict';
    const ensureApp = () => {
        if (typeof window.app === 'undefined') {
            setTimeout(ensureApp, 50);
            return;
        }
        if (!window.app.aiIntegration) {
            window.app.aiIntegration = {
                generateTestStrategy: () => window.app.generateTestStrategy(),
                generateTestDesign: () => window.app.generateTestDesign(),
                generateTestCases: () => window.app.generateTestCases(),
                generateScripts: () => window.app.generateScripts(),
                generateEvaluation: () => window.app.generateEvaluation(),
                generateReport: () => window.app.generateReport(),
                runAIMessage: (msg) => window.app.callAIAssistant(msg)
            };
            console.log('[ai-integration] Bound AI APIs to app');
        }
    };
    ensureApp();
})();
