/**
 * 车载控制器测试AI平台 - UI工具模块
 * 包含: Toast提示、Loading、Modal等UI操作
 */

const UIUtils = {
    /**
     * 显示Toast提示
     * @param {string} message - 提示消息
     * @param {string} type - 类型: 'success'|'error'|'warning'|'info'
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = 'toast';
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            warning: '#F59E0B',
            info: '#3B82F6'
        };
        toast.style.background = colors[type] || colors.info;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },

    /**
     * 显示Loading
     * @param {string} text - Loading文本
     */
    showLoading(text = '处理中，请稍候...') {
        const loadingText = document.getElementById('loadingText');
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingText) loadingText.textContent = text;
        if (loadingOverlay) loadingOverlay.style.display = 'flex';
    },

    /**
     * 隐藏Loading
     */
    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) loadingOverlay.style.display = 'none';
    },

    /**
     * 显示模态框
     * @param {string} id - 模态框ID
     */
    showModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.add('active');
    },

    /**
     * 隐藏模态框
     * @param {string} id - 模态框ID
     */
    closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.remove('active');
    },

    /**
     * 隐藏所有模态框
     */
    closeAllModals() {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
        });
    },

    /**
     * 绑定模态框事件
     */
    bindModalEvents() {
        // ESC键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // 点击遮罩关闭模态框
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.classList.remove('active');
                }
            });
        });
    },

    /**
     * 创建文件上传输入框并触发
     * @param {string} accept - 接受的文件类型
     * @param {Function} callback - 回调函数
     */
    triggerFileUpload(accept, callback) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = accept;
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file && callback) {
                callback(file);
            }
        };
        input.click();
    },

    /**
     * 渲染上传槽位
     * @param {string} key - 上传类型键
     * @param {string} label - 显示标签
     * @param {string} icon - Font Awesome图标名
     * @param {Object} uploadedFile - 已上传的文件对象
     * @returns {string} - HTML字符串
     */
    renderUploadSlot(key, label, icon, uploadedFile = null) {
        return `
            <div class="upload-zone" style="padding: 12px; ${uploadedFile ? 'background: var(--bg-light); border-color: var(--secondary);' : ''}" 
                 onclick="app.uploadFile('${key}')">
                <div class="file-icon"><i class="fas fa-${icon}"></i></div>
                <div class="upload-text" style="font-size: 11px;">${label}</div>
                ${uploadedFile ? `<div style="font-size: 10px; color: var(--secondary);">${uploadedFile.name}</div>` : ''}
            </div>
        `;
    },

    /**
     * 渲染文件列表项
     * @param {Object} file - 文件对象
     * @param {string} type - 文件类型
     * @returns {string} - HTML字符串
     */
    renderFileItem(file, type) {
        return `
            <div class="file-item">
                <div class="file-icon"><i class="fas fa-file-alt"></i></div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-meta">${Helpers.formatFileSize(file.size)}</div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-danger" style="padding: 4px 6px;" onclick="app.removeFile('${type}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * 更新状态栏时间
     */
    updateStatusTime() {
        const statusTime = document.getElementById('statusTime');
        if (statusTime) {
            statusTime.textContent = new Date().toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
    },

    /**
     * 更新状态栏项目名
     * @param {string} projectName - 项目名称
     */
    updateStatusProject(projectName) {
        const statusProject = document.getElementById('statusProject');
        if (statusProject) {
            statusProject.textContent = projectName || '未打开项目';
        }
    },

    /**
     * 更新项目标题
     * @param {string} title - 项目标题
     */
    updateProjectTitle(title) {
        const projectTitle = document.getElementById('projectTitle');
        if (projectTitle) {
            projectTitle.textContent = title || '项目名称';
        }
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIUtils;
}
