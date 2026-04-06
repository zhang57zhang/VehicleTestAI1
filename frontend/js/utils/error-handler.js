// 前端错误处理增强系统
// File: /home/qw/.openclaw/workspace/VehicleTestAI1/frontend/js/utils/error-handler.js
// Purpose: 统一前端错误处理、日志记录和重试机制

(function() {
    'use strict';
    
    // ==================== 错误类型定义 ====================
    
    const ErrorType = {
        NETWORK_ERROR: 'network_error',
        API_ERROR: 'api_error',
        VALIDATION_ERROR: 'validation_error',
        TIMEOUT_ERROR: 'timeout_error',
        UNKNOWN_ERROR: 'unknown_error'
    };
    
    const ErrorSeverity = {
        LOW: 'low',           // 可以忽略的错误
        MEDIUM: 'medium',     // 需要注意的错误
        HIGH: 'high',         // 严重影响使用的错误
        CRITICAL: 'critical'  // 系统无法使用的错误
    };
    
    // ==================== 错误追踪器 ====================
    
    class FrontendErrorTracker {
        constructor(maxErrors = 100) {
            this.errors = [];
            this.maxErrors = maxErrors;
        }
        
        track(error, context = {}) {
            const errorRecord = {
                id: this.generateId(),
                type: error.type || ErrorType.UNKNOWN_ERROR,
                message: error.message || 'Unknown error',
                severity: error.severity || ErrorSeverity.MEDIUM,
                timestamp: new Date().toISOString(),
                context: context,
                stack: error.stack || null,
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            
            this.errors.push(errorRecord);
            
            // 只保留最近的错误
            if (this.errors.length > this.maxErrors) {
                this.errors.shift();
            }
            
            // 上报错误
            this.report(errorRecord);
            
            return errorRecord;
        }
        
        generateId() {
            return 'err_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        report(errorRecord) {
            // 记录到控制台
            console.error('[Error]', errorRecord);
            
            // TODO: 上报到错误追踪服务
            // fetch('/api/errors/report', {
            //     method: 'POST',
            //     body: JSON.stringify(errorRecord)
            // });
        }
        
        getStats() {
            const byType = {};
            const bySeverity = {};
            
            this.errors.forEach(err => {
                byType[err.type] = (byType[err.type] || 0) + 1;
                bySeverity[err.severity] = (bySeverity[err.severity] || 0) + 1;
            });
            
            return {
                total: this.errors.length,
                byType: byType,
                bySeverity: bySeverity,
                recent: this.errors.slice(-10)
            };
        }
        
        clear() {
            this.errors = [];
        }
    }
    
    // 全局错误追踪器
    const errorTracker = new FrontendErrorTracker();
    
    // ==================== API 错误处理器 ====================
    
    class APIErrorHandler {
        constructor() {
            this.retryAttempts = 3;
            this.retryDelay = 1000; // 1秒
        }
        
        async handle(response, request) {
            // 解析响应
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { message: 'Unknown error' };
            }
            
            // 创建错误对象
            const error = {
                type: ErrorType.API_ERROR,
                message: errorData.error?.message || `HTTP ${response.status}`,
                severity: this.getSeverity(response.status),
                status: response.status,
                errorId: errorData.error?.id,
                errorCode: errorData.error?.code,
                request: request
            };
            
            // 追踪错误
            errorTracker.track(error, { url: request.url });
            
            return error;
        }
        
        getSeverity(status) {
            if (status >= 500) return ErrorSeverity.HIGH;
            if (status >= 400) return ErrorSeverity.MEDIUM;
            if (status === 401 || status === 403) return ErrorSeverity.HIGH;
            return ErrorSeverity.LOW;
        }
        
        async retry(request, attempt = 1) {
            if (attempt >= this.retryAttempts) {
                throw new Error('Max retry attempts exceeded');
            }
            
            const delay = this.retryDelay * Math.pow(2, attempt - 1);
            console.log(`⏳ Retry attempt ${attempt} in ${delay}ms`);
            
            await new Promise(resolve => setTimeout(resolve, delay));
            
            return fetch(request.url, request.options);
        }
    }
    
    const apiErrorHandler = new APIErrorHandler();
    
    // ==================== 增强的 Fetch 函数 ====================
    
    async function enhancedFetch(url, options = {}) {
        const request = { url, options };
        
        try {
            // 设置超时
            const timeout = options.timeout || 30000; // 30秒
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            // 检查响应状态
            if (!response.ok) {
                const error = await apiErrorHandler.handle(response, request);
                
                // 对于某些错误，自动重试
                if (response.status >= 500 && options.retry !== false) {
                    console.log('🔄 Auto-retry on server error');
                    const retryResponse = await apiErrorHandler.retry(request);
                    if (retryResponse.ok) {
                        return retryResponse;
                    }
                }
                
                throw error;
            }
            
            return response;
            
        } catch (error) {
            // 网络错误
            if (error.name === 'AbortError') {
                const timeoutError = {
                    type: ErrorType.TIMEOUT_ERROR,
                    message: 'Request timeout',
                    severity: ErrorSeverity.MEDIUM
                };
                errorTracker.track(timeoutError, request);
                throw timeoutError;
            }
            
            // 网络错误
            if (error.type === 'TypeError' && error.message.includes('fetch')) {
                const networkError = {
                    type: ErrorType.NETWORK_ERROR,
                    message: 'Network error',
                    severity: ErrorSeverity.HIGH
                };
                errorTracker.track(networkError, request);
                throw networkError;
            }
            
            // 其他错误
            if (!error.type) {
                error.type = ErrorType.UNKNOWN_ERROR;
                error.severity = ErrorSeverity.MEDIUM;
            }
            
            errorTracker.track(error, request);
            throw error;
        }
    }
    
    // ==================== Toast 通知系统 ====================
    
    class ToastManager {
        constructor() {
            this.container = this.createContainer();
            this.toasts = [];
            this.maxToasts = 5;
        }
        
        createContainer() {
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    max-width: 400px;
                `;
                document.body.appendChild(container);
            }
            return container;
        }
        
        show(message, type = 'info', duration = 5000) {
            const toast = this.createToast(message, type, duration);
            this.container.appendChild(toast);
            
            // 限制同时显示的 Toast 数量
            this.toasts.push(toast);
            if (this.toasts.length > this.maxToasts) {
                const oldToast = this.toasts.shift();
                this.removeToast(oldToast);
            }
            
            // 自动移除
            setTimeout(() => {
                this.removeToast(toast);
            }, duration);
            
            return toast;
        }
        
        createToast(message, type, duration) {
            const toast = document.createElement('div');
            
            const colors = {
                success: '#10b981',
                error: '#ef4444',
                warning: '#f59e0b',
                info: '#3b82f6'
            };
            
            const icons = {
                success: '✓',
                error: '✕',
                warning: '⚠',
                info: 'ℹ'
            };
            
            toast.style.cssText = `
                background: white;
                border-left: 4px solid ${colors[type] || colors.info};
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                display: flex;
                align-items: center;
                gap: 12px;
                animation: slideIn 0.3s ease;
            `;
            
            toast.innerHTML = `
                <div style="
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    background: ${colors[type] || colors.info};
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    flex-shrink: 0;
                ">${icons[type] || icons.info}</div>
                <div style="flex: 1; color: #1f2937; font-size: 14px;">${message}</div>
                <button onclick="this.parentElement.remove()" style="
                    background: none;
                    border: none;
                    cursor: pointer;
                    font-size: 20px;
                    color: #9ca3af;
                    padding: 0;
                    line-height: 1;
                ">×</button>
            `;
            
            return toast;
        }
        
        removeToast(toast) {
            if (toast && toast.parentElement) {
                toast.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.parentElement.removeChild(toast);
                    }
                }, 300);
                
                const index = this.toasts.indexOf(toast);
                if (index > -1) {
                    this.toasts.splice(index, 1);
                }
            }
        }
        
        success(message) {
            return this.show(message, 'success');
        }
        
        error(message) {
            return this.show(message, 'error', 8000);
        }
        
        warning(message) {
            return this.show(message, 'warning');
        }
        
        info(message) {
            return this.show(message, 'info');
        }
    }
    
    // 全局 Toast 管理器
    const toastManager = new ToastManager();
    
    // ==================== 导出全局函数 ====================
    
    window.ErrorHandler = {
        track: (error, context) => errorTracker.track(error, context),
        getStats: () => errorTracker.getStats(),
        clear: () => errorTracker.clear(),
        
        fetch: enhancedFetch,
        
        toast: {
            success: (msg) => toastManager.success(msg),
            error: (msg) => toastManager.error(msg),
            warning: (msg) => toastManager.warning(msg),
            info: (msg) => toastManager.info(msg)
        },
        
        ErrorType: ErrorType,
        ErrorSeverity: ErrorSeverity
    };
    
    // 兼容旧代码
    window.showToast = (message, type) => {
        if (type === 'success') toastManager.success(message);
        else if (type === 'error') toastManager.error(message);
        else if (type === 'warning') toastManager.warning(message);
        else toastManager.info(message);
    };
    
    // 添加样式动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    console.log('✅ 错误处理系统已加载');
    
})();
