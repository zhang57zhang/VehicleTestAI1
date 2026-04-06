/**
 * 车载控制器测试AI平台 - 工具函数模块
 * 包含: 文件处理、数据导出、格式化等通用工具函数
 */

const Helpers = {
    /**
     * 下载文件
     * @param {string} filename - 文件名
     * @param {string} content - 文件内容
     * @param {string} mimeType - MIME类型
     */
    downloadFile(filename, content, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * 获取文件图标
     * @param {string} filename - 文件名
     * @returns {string} - Font Awesome图标类名
     */
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'xls': 'fa-file-excel',
            'xlsx': 'fa-file-excel',
            'json': 'fa-file-code',
            'md': 'fa-file-alt',
            'py': 'fa-file-code',
            'js': 'fa-file-code',
            'robot': 'fa-file-code',
            'blf': 'fa-file',
            'asc': 'fa-file',
            'csv': 'fa-file-csv',
            'mf4': 'fa-file'
        };
        return icons[ext] || 'fa-file';
    },

    /**
     * 获取文件颜色
     * @param {string} filename - 文件名
     * @returns {string} - CSS颜色变量
     */
    getFileColor(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const colors = {
            'pdf': 'var(--danger)',
            'doc': 'var(--info)',
            'docx': 'var(--info)',
            'xls': 'var(--secondary)',
            'xlsx': 'var(--secondary)',
            'json': 'var(--primary)',
            'md': 'var(--text-secondary)',
            'py': 'var(--primary)',
            'js': 'var(--warning)'
        };
        return colors[ext] || 'var(--text-secondary)';
    },

    /**
     * 格式化文件大小
     * @param {number} bytes - 字节数
     * @returns {string} - 格式化后的大小字符串
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    },

    /**
     * 生成唯一ID
     * @param {string} prefix - ID前缀
     * @returns {string} - 唯一ID
     */
    generateId(prefix = '') {
        const timestamp = Date.now().toString(36).toUpperCase();
        const random = Math.random().toString(36).substring(2, 8).toUpperCase();
        return prefix ? `${prefix}_${timestamp}${random}` : `${timestamp}${random}`;
    },

    /**
     * 格式化日期时间
     * @param {Date|string} date - 日期对象或字符串
     * @param {string} format - 格式类型 'full'|'date'|'time'
     * @returns {string} - 格式化后的日期字符串
     */
    formatDateTime(date, format = 'full') {
        const d = new Date(date);
        const options = {
            full: { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' },
            date: { year: 'numeric', month: '2-digit', day: '2-digit' },
            time: { hour: '2-digit', minute: '2-digit' }
        };
        return d.toLocaleString('zh-CN', options[format] || options.full);
    },

    /**
     * 防抖函数
     * @param {Function} func - 要执行的函数
     * @param {number} wait - 等待时间(毫秒)
     * @returns {Function} - 防抖后的函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * 节流函数
     * @param {Function} func - 要执行的函数
     * @param {number} limit - 时间限制(毫秒)
     * @returns {Function} - 节流后的函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * 深拷贝对象
     * @param {Object} obj - 要拷贝的对象
     * @returns {Object} - 拷贝后的新对象
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    },

    /**
     * 本地存储操作
     */
    storage: {
        get(key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (e) {
                console.error('Error reading from localStorage:', e);
                return null;
            }
        },
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (e) {
                console.error('Error writing to localStorage:', e);
                return false;
            }
        },
        remove(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (e) {
                console.error('Error removing from localStorage:', e);
                return false;
            }
        }
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Helpers;
}
