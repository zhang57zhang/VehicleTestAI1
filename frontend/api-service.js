/**
 * 车载控制器测试AI平台 - 前端API服务
 * 负责与后端API交互
 */

// ==================== API配置 ====================

const API_CONFIG = {
    // 后端API地址 - 使用完整URL
    BASE_URL: 'http://localhost:5000/api',

    // API端点
    ENDPOINTS: {
        // 项目管理
        PROJECTS: '/projects',
        PROJECT_DETAIL: '/projects/{id}',

        // 文件上传
        UPLOAD: '/upload/{projectId}/{fileType}',

        // AI生成
        AI_GENERATE_STRATEGY: '/ai/generate-strategy',
        AI_GENERATE_DESIGN: '/ai/generate-design',
        AI_GENERATE_TESTCASES: '/ai/generate-testcases',
        AI_GENERATE_SCRIPTS: '/ai/generate-scripts',
        AI_PARSE_LOG: '/ai/parse-log',
        AI_GENERATE_EVALUATION: '/ai/generate-evaluation',
        AI_GENERATE_REPORT: '/ai/generate-report',
        AI_ANALYZE_REQUIREMENTS: '/ai/parse-requirements',
        AI_REVIEW_REPORT: '/ai/review-report',
        AI_OPTIMIZE_SCRIPT: '/ai/optimize-script',

        // DBC and log analysis
        DBC_PARSE: '/dbc/parse',
        DBC_LIST: '/dbc/list',
        LOGS_ANALYZE_WITH_DBC: '/logs/analyze-with-dbc',
        LOGS_SIGNAL_LIST: '/logs/signal-list',

        // Dashboard
        BENCHMARKS: '/benchmarks',
        AUTOMATION_JOBS: '/automation/jobs',

        // 健康检查
        HEALTH: '/health'
    },

    // 超时配置（毫秒）
    TIMEOUT: 30000,
    
    // AI请求超时（毫秒）- AI分析需要更长时间
    AI_TIMEOUT: 180000,  // 3分钟

    // 重试次数
    RETRY_COUNT: 3
};

// ==================== API服务类 ====================

class APIService {
    constructor() {
        this.baseUrl = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.aiTimeout = API_CONFIG.AI_TIMEOUT;
        this.retryCount = API_CONFIG.RETRY_COUNT;
    }

    /**
     * 构建URL
     * @param {string} endpoint - API端点
     * @param {object} params - URL参数
     */
    buildUrl(endpoint, params = {}) {
        let url = endpoint;
        for (const [key, value] of Object.entries(params)) {
            url = url.replace(`{${key}}`, encodeURIComponent(value));
        }
        return `${this.baseUrl}${url}`;
    }

    /**
     * 通用请求方法
     * @param {string} method - HTTP方法
     * @param {string} url - 请求URL
     * @param {object} data - 请求数据
     * @param {object} headers - 请求头
     * @param {number} customTimeout - 自定义超时时间
     */
    async request(method, url, data = null, headers = {}, customTimeout = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            }
        };

        if (data && method !== 'GET') {
            if (data instanceof FormData) {
                options.body = data;
                delete options.headers['Content-Type'];
            } else {
                options.body = JSON.stringify(data);
            }
        }

        const timeout = customTimeout || this.timeout;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            options.signal = controller.signal;

            const response = await fetch(url, options);
            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请稍后重试');
            }
            throw error;
        }
    }

    /**
     * GET请求
     */
    async get(endpoint, params = {}) {
        const url = this.buildUrl(endpoint, params);
        return this.request('GET', url);
    }

    /**
     * POST请求
     * @param {string} endpoint - API端点
     * @param {object} data - 请求数据
     * @param {number} customTimeout - 自定义超时时间（可选）
     */
    async post(endpoint, data = null, customTimeout = null) {
        const url = this.buildUrl(endpoint);
        return this.request('POST', url, data, {}, customTimeout);
    }

    /**
     * PUT请求
     */
    async put(endpoint, data = null) {
        const url = this.buildUrl(endpoint);
        return this.request('PUT', url, data);
    }

    /**
     * DELETE请求
     */
    async delete(endpoint, params = {}) {
        const url = this.buildUrl(endpoint, params);
        return this.request('DELETE', url);
    }

    // ==================== 项目管理API ====================

    /**
     * 获取项目列表
     */
    async getProjects() {
        return this.get(API_CONFIG.ENDPOINTS.PROJECTS);
    }

    /**
     * 创建项目
     * @param {string} name - 项目名称
     * @param {string} customPath - 自定义路径 (可选)
     */
    async createProject(name, customPath = null) {
        const data = { name };
        if (customPath) {
            data.path = customPath;
        }
        return this.post(API_CONFIG.ENDPOINTS.PROJECTS, data);
    }

    /**
     * 获取项目详情
     * @param {string} projectId - 项目ID
     */
    async getProject(projectId) {
        return this.get(API_CONFIG.ENDPOINTS.PROJECT_DETAIL, { id: projectId });
    }

    /**
     * 更新项目
     * @param {string} projectId - 项目ID
     * @param {object} data - 更新数据
     */
    async updateProject(projectId, data) {
        return this.put(API_CONFIG.ENDPOINTS.PROJECT_DETAIL, { id: projectId }, data);
    }

    /**
     * 删除项目
     * @param {string} projectId - 项目ID
     */
    async deleteProject(projectId) {
        return this.delete(API_CONFIG.ENDPOINTS.PROJECT_DETAIL, { id: projectId });
    }

    // ==================== 文件上传API ====================

    /**
     * 上传文件
     * @param {string} projectId - 项目ID
     * @param {string} fileType - 文件类型
     * @param {File} file - 文件对象
     */
    async uploadFile(projectId, fileType, file) {
        const formData = new FormData();
        formData.append('file', file);

        const url = this.buildUrl(API_CONFIG.ENDPOINTS.UPLOAD, {
            projectId,
            fileType
        });

        return this.request('POST', url, formData);
    }

    /**
     * 删除文件
     * @param {string} projectId - 项目ID
     * @param {string} fileId - 文件ID
     */
    async deleteFile(projectId, fileId) {
        return this.delete(`/files/${projectId}/${fileId}`);
    }

    // ==================== AI生成API ====================

    /**
     * 生成测试策略
     * @param {object} params - 参数
     */
    async generateTestStrategy(params) {
        return this.post(API_CONFIG.ENDPOINTS.AI_GENERATE_STRATEGY, params, this.aiTimeout);
    }

    /**
     * 生成测试设计
     * @param {object} params - 参数
     */
    async generateTestDesign(params) {
        return this.post(API_CONFIG.ENDPOINTS.AI_GENERATE_DESIGN, params, this.aiTimeout);
    }

    /**
     * 生成测试用例
     * @param {object} params - 参数
     */
    async generateTestCases(params) {
        return this.post(API_CONFIG.ENDPOINTS.AI_GENERATE_TESTCASES, params, this.aiTimeout);
    }

    /**
     * 生成测试脚本
     * @param {object} params - 参数
     */
    async generateScripts(params) {
        return this.post(API_CONFIG.ENDPOINTS.AI_GENERATE_SCRIPTS, params, this.aiTimeout);
    }

    /**
     * 解析测试日志
     * @param {object} params - 参数
     */
    async parseLog(params) {
        return this.post(API_CONFIG.ENDPOINTS.AI_PARSE_LOG, params, this.aiTimeout);
    }

    /**
     * 生成测试评估
     * @param {object} params - 参数
     */
    async generateEvaluation(params) {
        return this.post(API_CONFIG.ENDPOINTS.AI_GENERATE_EVALUATION, params, this.aiTimeout);
    }

    /**
     * 生成测试报告
     * @param {object} params - 参数
     */
    async generateReport(params) {
        return this.post(API_CONFIG.ENDPOINTS.AI_GENERATE_REPORT, params, this.aiTimeout);
    }

    /**
     * 分析需求
     * @param {object} params - 参数
     */
    async analyzeRequirements(params) {
        // AI分析需要更长的超时时间
        return this.post(API_CONFIG.ENDPOINTS.AI_ANALYZE_REQUIREMENTS, params, this.aiTimeout);
    }

    /**
     * 审查报告
     * @param {string} reportContent - 报告内容
     */
    async reviewReport(reportContent) {
        return this.post(API_CONFIG.ENDPOINTS.AI_REVIEW_REPORT, { report_content: reportContent }, this.aiTimeout);
    }

    /**
     * 优化脚本
     * @param {string} scriptContent - 脚本内容
     */
    async optimizeScript(scriptContent) {
        return this.post(API_CONFIG.ENDPOINTS.AI_OPTIMIZE_SCRIPT, { script_content: scriptContent }, this.aiTimeout);
    }

    // ==================== 看板API ====================

    /**
     * 获取测试台架列表
     */
    async getBenchmarks() {
        return this.get(API_CONFIG.ENDPOINTS.BENCHMARKS);
    }

    /**
     * 添加测试台架
     * @param {object} data - 台架数据
     */
    async addBenchmark(data) {
        return this.post(API_CONFIG.ENDPOINTS.BENCHMARKS, data);
    }

    /**
     * 获取自动化任务列表
     */
    async getAutomationJobs() {
        return this.get(API_CONFIG.ENDPOINTS.AUTOMATION_JOBS);
    }

    /**
     * 创建自动化任务
     * @param {object} data - 任务数据
     */
    async createAutomationJob(data) {
        return this.post(API_CONFIG.ENDPOINTS.AUTOMATION_JOBS, data);
    }

    /**
     * 执行自动化任务
     * @param {string} jobId - 任务ID
     */
    async runAutomationJob(jobId) {
        return this.post(`${API_CONFIG.ENDPOINTS.AUTOMATION_JOBS}/${jobId}/run`);
    }

    // ==================== AI配置API ====================

    /**
     * 获取AI配置
     */
    async getAIConfig() {
        return this.get('/ai/config');
    }

    /**
     * 更新AI配置
     * @param {object} config - 配置数据
     */
    async updateAIConfig(config) {
        return this.post('/ai/config', config);
    }

    /**
     * 测试AI连接
     */
    async testAIConnection() {
        return this.post('/ai/test');
    }

    // ==================== 健康检查 ====================

    /**
     * 检查服务健康状态
     */
    async checkHealth() {
        try {
            const result = await this.get(API_CONFIG.ENDPOINTS.HEALTH);
            return { healthy: true, ...result };
        } catch (error) {
            return { healthy: false, error: error.message };
        }
    }
}

// ==================== API服务单例 ====================

const apiService = new APIService();

// ==================== 导出 ====================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIService, apiService, API_CONFIG };
}
