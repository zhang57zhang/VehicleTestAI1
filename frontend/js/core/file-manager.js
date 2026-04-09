// File management module: exposes file-related helpers via app.fileManager
(function(){
    'use strict';
    const ensureApp = () => {
        if (typeof window.app === 'undefined') {
            setTimeout(ensureApp, 50);
            return;
        }
        if (!window.app.fileManager) {
            window.app.fileManager = {
                uploadFile: (type) => window.app.uploadFile(type),
                readFileContent: (file) => window.app.readFileContent(file),
                uploadFileToBackend: (type, file, content) => window.app.uploadFileToBackend(type, file, content),
                renderFileList: (type, file) => window.app.renderFileList(type, file),
                removeFile: (type) => window.app.removeFile(type),
                removeUploadedFile: (type) => window.app.removeUploadedFile(type)
            };
            console.log('[file-manager] Bound fileManager API to app');
        }
    };
    ensureApp();
})();
