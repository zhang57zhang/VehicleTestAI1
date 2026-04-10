/**
 * 车载控制器测试AI平台 - 增强版API服务
 * 提供错误处理、重试机制、缓存和请求队列
 */

// ==================== 配置 ====================

const ENHANCED_API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api',
    
    // 超时配置
    TIMEOUT: 30000,
    AI_TIMEOUT: 180000,
    
    // 重试配置
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000,
    
    // 缓存配置
    CACHE_ENABLED: true,
    CACHE_TTL: 60000, // 1分钟
    
    // 请求队列
    MAX_CONCURRENT: 5
};

// ==================== 缓存管理器 ====================

class CacheManager {
    constructor(ttl = 60000) {
        this.cache = new Map();
        this.ttl = ttl;
    }
    
    /**
     * 生成缓存键
     */
    generateKey(method, url, data = null) {
        const dataHash = data ? JSON.stringify(data) : '';
        return `${method}:${url}:${dataHash}`;
    }
    
    /**
     * 获取缓存
     */
    get(method, url, data = null) {
        if (!ENHANCED_API_CONFIG.CACHE_ENABLED) return null;
        
        const key = this.generateKey(method, url, data);
        const cached = this.cache.get(key);
        
        if (cached && Date.now() - cached.timestamp < this.ttl) {
            console.log(`[Cache] Hit: ${key}`);
            return cached.data;
        }
        
        // 清理过期缓存
        if (cached) {
            this.cache.delete(key);
        }
        
        return null;
    }
    
    /**
     * 设置缓存
     */
    set(method, url, data, response) {
        if (!ENHANCED_API_CONFIG.CACHE_ENABLED) return;
        
        const key = this.generateKey(method, url, data);
        this.cache.set(key, {
            data: response,
            timestamp: Date.now()
        });
        
        // 限制缓存大小
        if (this.cache.size > 100) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }
    
    /**
     * 清除缓存
     */
    clear(pattern = null) {
        if (pattern) {
            for (const key of this.cache.keys()) {
                if (key.includes(pattern)) {
                    this.cache.delete(key);
                }
            }
        } else {
            this.cache.clear();
        }
    }
}

// ==================== 请求队列 ====================

class RequestQueue {
    constructor(maxConcurrent = 5) {
        this.queue = [];
        this.active = 0;
        this.maxConcurrent = maxConcurrent;
    }
    
    /**
     * 添加请求到队列
     */
    async add(requestFn) {
        return new Promise((resolve, reject) => {
            this.queue.push({
                fn: requestFn,
                resolve,
                reject
            });
            this.process();
        });
    }
    
    /**
     * 处理队列
     */
    async process() {
        while (this.queue.length > 0 && this.active < this.maxConcurrent) {
            this.active++;
            const { fn, resolve, reject } = this.queue.shift();
            
            try {
                const result = await fn();
                resolve(result);
            } catch (error) {
                reject(error);
            } finally {
                this.active--;
                this.process();
            }
        }
    }
}

// ==================== 增强版API服务 ====================

class EnhancedAPIService {
    constructor() {
        this.baseUrl = ENHANCED_API_CONFIG.BASE_URL;
        this.cache = new CacheManager(ENHANCED_API_CONFIG.CACHE_TTL);
        this.queue = new RequestQueue(ENHANCED_API_CONFIG.MAX_CONCURRENT);
        this.requestInterceptors = [];
        this.responseInterceptors = [];
    }
    
    /**
     * 添加请求拦截器
     */
    addRequestInterceptor(fn) {
        this.requestInterceptors.push(fn);
    }
    
    /**
     * 添加响应拦截器
     */
    addResponseInterceptor(fn) {
        this.responseInterceptors.push(fn);
    }
    
    /**
     * 构建URL
     */
    buildUrl(endpoint, params = {}) {
        let url = endpoint;
        for (const [key, value] of Object.entries(params)) {
            url = url.replace(`{${key}}`, encodeURIComponent(value));
        }
        return `${this.baseUrl}${url}`;
    }
    
    /**
     * 延迟函数
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * 带重试的请求
     */
    async requestWithRetry(method, url, data = null, options = {}) {
        const {
            maxRetries = ENHANCED_API_CONFIG.MAX_RETRIES,
            retryDelay = ENHANCED_API_CONFIG.RETRY_DELAY,
            timeout = ENHANCED_API_CONFIG.TIMEOUT,
            useCache = true,
            skipQueue = false
        } = options;
        
        // 检查缓存
        const cachedResponse = this.cache.get(method, url, data);
        if (cachedResponse && useCache && method === 'GET') {
            return cachedResponse;
        }
        
        // 请求函数
        const doRequest = async () => {
            let lastError = null;
            
            for (let attempt = 0; attempt < maxRetries; attempt++) {
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), timeout);
                    
                    const fetchOptions = {
                        method,
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        signal: controller.signal
                    };
                    
                    // 应用请求拦截器
                    let processedData = data;
                    for (const interceptor of this.requestInterceptors) {
                        processedData = interceptor(processedData);
                    }
                    
                    if (processedData && method !== 'GET') {
                        if (processedData instanceof FormData) {
                            fetchOptions.body = processedData;
                            delete fetchOptions.headers['Content-Type'];
                        } else {
                            fetchOptions.body = JSON.stringify(processedData);
                        }
                    }
                    
                    const response = await fetch(url, fetchOptions);
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new APIError(
                            errorData.error?.message || `HTTP ${response.status}`,
                            response.status,
                            errorData
                        );
                    }
                    
                    let result = await response.json();
                    
                    // 应用响应拦截器
                    for (const interceptor of this.responseInterceptors) {
                        result = interceptor(result);
                    }
                    
                    // 缓存GET请求
                    if (useCache && method === 'GET') {
                        this.cache.set(method, url, data, result);
                    }
                    
                    return result;
                    
                } catch (error) {
                    lastError = error;
                    
                    // 不重试的情况
                    if (error instanceof APIError) {
                        if (error.status === 400 || error.status === 401 || error.status === 403) {
                            throw error;
                        }
                    }
                    
                    // 超时或网络错误，重试
                    if (attempt < maxRetries - 1) {
                        console.warn(`[API] Retry ${attempt + 1}/${maxRetries}: ${url}`);
                        await this.delay(retryDelay * (attempt + 1));
                    }
                }
            }
            
            throw lastError;
        };
        
        // 使用队列或直接执行
        if (skipQueue) {
            return doRequest();
        } else {
            return this.queue.add(doRequest);
        }
    }
    
    // ==================== 便捷方法 ====================
    
    async get(endpoint, params = {}, options = {}) {
        const url = this.buildUrl(endpoint, params);
        return this.requestWithRetry('GET', url, null, options);
    }
    
    async post(endpoint, data = null, options = {}) {
        const url = this.buildUrl(endpoint);
        return this.requestWithRetry('POST', url, data, { ...options, useCache: false });
    }
    
    async put(endpoint, data = null, options = {}) {
        const url = this.buildUrl(endpoint);
        return this.requestWithRetry('PUT', url, data, { ...options, useCache: false });
    }
    
    async delete(endpoint, params = {}, options = {}) {
        const url = this.buildUrl(endpoint, params);
        return this.requestWithRetry('DELETE', url, null, { ...options, useCache: false });
    }
    
    // ==================== 项目管理 ====================
    
    async getProjects() {
        return this.get('/projects');
    }
    
    async createProject(name, description = '') {
        return this.post('/projects', { name, description });
    }
    
    async getProject(projectId) {
        return this.get(`/projects/${projectId}`);
    }
    
    async updateProject(projectId, data) {
        return this.put(`/projects/${projectId}`, data);
    }
    
    async deleteProject(projectId) {
        return this.delete(`/projects/${projectId}`);
    }
    
    async syncProject(projectId) {
        return this.post(`/projects/${projectId}/sync`);
    }
    
    // ==================== 需求管理 ====================
    
    async getRequirements(projectId) {
        return this.get(`/requirements/${projectId}`);
    }
    
    async createRequirement(projectId, data) {
        return this.post('/requirements', { project_id: projectId, ...data });
    }
    
    async updateRequirement(requirementId, data) {
        return this.put(`/requirements/${requirementId}`, data);
    }
    
    async deleteRequirement(requirementId) {
        return this.delete(`/requirements/${requirementId}`);
    }
    
    // ==================== AI生成 ====================
    
    async generateStrategy(params) {
        return this.post('/ai/generate-strategy', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async generateDesign(params) {
        return this.post('/ai/generate-design', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async generateTestCases(params) {
        return this.post('/ai/generate-testcases', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async generateScripts(params) {
        return this.post('/ai/generate-scripts', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async generateEvaluation(params) {
        return this.post('/ai/generate-evaluation', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async generateReport(params) {
        return this.post('/ai/generate-report', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async analyzeRequirements(params) {
        return this.post('/ai/parse-requirements', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async parseLog(params) {
        return this.post('/ai/parse-log', params, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT,
            skipQueue: true
        });
    }
    
    async chat(message, history = []) {
        return this.post('/ai/chat', { message, history }, {
            timeout: ENHANCED_API_CONFIG.AI_TIMEOUT
        });
    }
    
    // ==================== 文件操作 ====================
    
    async uploadFile(projectId, fileType, file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', fileType);
        
        const url = this.buildUrl(`/upload/${projectId}/${fileType}`);
        
        return this.requestWithRetry('POST', url, formData, {
            useCache: false,
            skipQueue: true
        });
    }
    
    async saveFile(projectId, folder, filename, content) {
        return this.post(`/save-file/${projectId}/${folder}`, { filename, content });
    }
    
    // ==================== AI配置 ====================
    
    async getAIConfig() {
        return this.get('/ai/config');
    }
    
    async updateAIConfig(config) {
        return this.post('/ai/config', config);
    }
    
    // ==================== 健康检查 ====================
    
    async checkHealth() {
        try {
            const result = await this.get('/health', {}, { maxRetries: 1 });
            return { healthy: true, ...result };
        } catch (error) {
            return { healthy: false, error: error.message };
        }
    }
    
    // ==================== 缓存管理 ====================
    
    clearCache(pattern = null) {
        this.cache.clear(pattern);
    }
}

// ==================== 自定义错误类 ====================

class APIError extends Error {
    constructor(message, status, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

// ==================== 单例导出 ====================

const enhancedAPIService = new EnhancedAPIService();

// 全局暴露
if (typeof window !== 'undefined') {
    window.EnhancedAPIService = EnhancedAPIService;
    window.enhancedAPIService = enhancedAPIService;
    window.APIError = APIError;
}
