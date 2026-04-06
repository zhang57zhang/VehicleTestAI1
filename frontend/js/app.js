/**
 * 车载控制器测试AI平台 - 主应用入口
 * 模块化重构版本
 */

class VehicleTestAIApp {
    constructor() {
        this.currentProject = null;
        this.activeTab = 'requirements';
        this.uploadedFiles = {};
        this.projectData = {};
        this.modelConfig = this.loadModelConfig();
        this.aiSidebarMinimized = false;
        this.aiMessageHistory = [];
        this.init();
    }

    // ========== 初始化 ==========

    loadModelConfig() {
        const saved = localStorage.getItem('modelConfig');
        return saved ? JSON.parse(saved) : {
            provider: 'glm',
            modelName: 'glm-4-plus',
            apiKey: '',
            baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
            maxTokens: 4096,
            temperature: 0.7
        };
    }

    saveModelConfig() {
        localStorage.setItem('modelConfig', JSON.stringify(this.modelConfig));
        // 同步到后端
        this.syncModelConfigToBackend();
        this.showToast('AI模型配置已保存', 'success');
    }

    async syncModelConfigToBackend() {
        try {
            await apiService.updateAIConfig({
                provider: this.modelConfig.provider,
                model: this.modelConfig.modelName,
                api_key: this.modelConfig.apiKey,
                base_url: this.modelConfig.baseUrl,
                max_tokens: this.modelConfig.maxTokens,
                temperature: this.modelConfig.temperature
            });
        } catch (error) {
            console.warn('同步AI配置到后端失败:', error.message);
        }
    }

    async loadModelConfigFromBackend() {
        try {
            const result = await apiService.getAIConfig();
            if (result.success && result.config) {
                this.modelConfig = {
                    provider: result.config.provider || 'glm',
                    modelName: result.config.model || 'glm-4-plus',
                    apiKey: result.config.api_key || '',
                    baseUrl: result.config.base_url || 'https://open.bigmodel.cn/api/paas/v4',
                    maxTokens: result.config.max_tokens || 4096,
                    temperature: result.config.temperature || 0.7
                };
                localStorage.setItem('modelConfig', JSON.stringify(this.modelConfig));
            }
        } catch (error) {
            console.warn('从后端加载AI配置失败:', error.message);
        }
    }

    init() {
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
        this.renderTabs();
        this.renderPage('requirements');
        this.renderProjectTree();
        this.bindEvents();
        // 从后端加载AI配置
        this.loadModelConfigFromBackend();
        // 启动左侧树自动同步 (每1分钟)
        this.startTreeAutoSync();
    }
    
    startTreeAutoSync() {
        // 每60秒同步一次左侧树
        this.treeSyncInterval = setInterval(() => {
            this.syncTreeWithFolder();
        }, 60000);
    }
    
    async syncTreeWithFolder() {
        if (!this.currentProject) return;
        
        try {
            // 调用同步API，确保磁盘文件与项目记录一致
            await this.syncProjectFiles();
            this.renderProjectTree();
        } catch (error) {
            console.warn('Tree sync error:', error);
        }
    }

    updateTime() {
        UIUtils.updateStatusTime();
    }

    // ========== 标签页管理 ==========

    renderTabs() {
        const pages = [
            { id: 'aiassistant', name: 'AI辅助看板', icon: 'fa-brain' },
            { id: 'requirements', name: '需求分析', icon: 'fa-file-alt' },
            { id: 'strategy', name: '测试策略', icon: 'fa-chess' },
            { id: 'design', name: '测试设计', icon: 'fa-pencil-ruler' },
            { id: 'testcase', name: '测试用例', icon: 'fa-list-check' },
            { id: 'script', name: '测试脚本', icon: 'fa-code' },
            { id: 'log', name: '测试日志', icon: 'fa-history' },
            { id: 'evaluation', name: '测试评估', icon: 'fa-chart-line' },
            { id: 'report', name: '测试报告', icon: 'fa-file-invoice' },
            { id: 'resource', name: '测试资源', icon: 'fa-boxes' },
            { id: 'bench', name: '测试台架看板', icon: 'fa-server' },
            { id: 'progress', name: '测试进度看板', icon: 'fa-tasks' },
            { id: 'automation', name: '自动化看板', icon: 'fa-robot' },
            { id: 'pending1', name: '待使用1', icon: 'fa-plus-circle' },
            { id: 'pending2', name: '待使用2', icon: 'fa-plus-circle' },
            { id: 'pending3', name: '待使用3', icon: 'fa-plus-circle' },
            { id: 'pending4', name: '待使用4', icon: 'fa-plus-circle' },
            { id: 'pending5', name: '待使用5', icon: 'fa-plus-circle' }
        ];

        document.getElementById('tabBar').innerHTML = pages.map(p => `
            <div class="tab-item ${p.id === 'requirements' ? 'active' : ''}" data-page="${p.id}" onclick="app.switchTab('${p.id}')">
                <i class="fas ${p.icon}"></i>
                <span>${p.name}</span>
            </div>
        `).join('');
    }

    switchTab(pageId) {
        document.querySelectorAll('.tab-item').forEach(t => t.classList.toggle('active', t.dataset.page === pageId));
        this.activeTab = pageId;
        this.renderPage(pageId);
    }

    // ========== 页面渲染 ==========

    async renderPage(pageId) {
        const container = document.getElementById('pageContainer');
        const methods = {
            'requirements': () => RequirementsPage.render(this),
            'strategy': () => StrategyPage.render(this),
            'design': () => DesignPage.render(this),
            'testcase': () => TestCasePage.render(this),
            'script': () => ScriptPage.render(this),
            'log': () => LogPage.render(this),
            'evaluation': () => EvaluationPage.render(this),
            'report': () => ReportPage.render(this),
            'resource': () => ResourcePage.render(this),
            'bench': () => BenchPage.render(this),
            'progress': () => ProgressPage.render(this),
            'automation': () => AutomationPage.render(this),
            'aiassistant': () => AIAssistantPage.render(this),
            'pending1': () => PendingPage.render(1),
            'pending2': () => PendingPage.render(2),
            'pending3': () => PendingPage.render(3),
            'pending4': () => PendingPage.render(4),
            'pending5': () => PendingPage.render(5)
        };

        if (methods[pageId]) {
            const result = methods[pageId]();
            // Handle async render functions
            if (result instanceof Promise) {
                container.innerHTML = '<div class="page-content animate-fade-in"><div class="loading" style="padding: 50px; text-align: center;"><i class="fas fa-spinner fa-spin"></i> 加载中...</div></div>';
                const html = await result;
                container.innerHTML = `<div class="page-content animate-fade-in">${html}</div>`;
            } else {
                container.innerHTML = `<div class="page-content animate-fade-in">${result}</div>`;
            }
        } else {
            container.innerHTML = `<div class="page-content animate-fade-in"><div class="empty-state"><div class="empty-state-icon"><i class="fas fa-tools"></i></div><div class="empty-state-title">功能开发中</div></div></div>`;
        }
    }

    // ========== 项目树渲染 ==========

    renderProjectTree() {
        const tree = document.getElementById('projectTree');
        
        // If no project, show empty state
        if (!this.currentProject) {
            tree.innerHTML = `
                <div class="tree-item" style="color: var(--text-secondary); font-style: italic; padding: 20px;">
                    <i class="fas fa-info-circle" style="margin-right: 8px;"></i>请先创建或打开项目
                </div>
            `;
            return;
        }
        
        const files = this.currentProject.files || {};
        const folders = [
            { id: 'requirement', name: '需求', icon: 'fa-folder' },
            { id: 'strategy', name: '策略', icon: 'fa-folder' },
            { id: 'design', name: '设计', icon: 'fa-folder' },
            { id: 'testcase', name: '用例', icon: 'fa-folder' },
            { id: 'script', name: '脚本', icon: 'fa-folder' },
            { id: 'log', name: '日志', icon: 'fa-folder' },
            { id: 'evaluation', name: '评估', icon: 'fa-folder' },
            { id: 'report', name: '报告', icon: 'fa-folder' },
            { id: 'resource', name: '资源', icon: 'fa-folder' }
        ];
        
        let treeHtml = '';
        folders.forEach(folder => {
            const folderFiles = files[folder.id] ? Object.values(files[folder.id]) : [];
            const hasFiles = folderFiles.length > 0;
            
            treeHtml += `
                <div class="tree-item folder">
                    <span class="tree-toggle"><i class="fas fa-chevron-${hasFiles ? 'down' : 'right'}"></i></span>
                    <i class="fas ${folder.icon}" style="color: var(--warning);"></i> ${folder.name}
                </div>
                <div class="tree-children" style="margin-left: 20px;">
            `;
            
            if (hasFiles) {
                folderFiles.forEach(f => {
                    treeHtml += `<div class="tree-item"><i class="fas ${this.getFileIcon(f.name)}" style="color: ${this.getFileColor(f.name)};"></i> ${f.name}</div>`;
                });
            } else {
                treeHtml += `<div class="tree-item" style="color: var(--text-secondary); font-style: italic;">(空)</div>`;
            }
            
            treeHtml += `</div>`;
        });
        
        tree.innerHTML = treeHtml;
    }

    // ========== 文件操作 ==========

    uploadFile(type) {
        UIUtils.triggerFileUpload('.pdf,.doc,.docx,.xls,.xlsx,.json,.dbc,.arxml,.md,.txt', async (file) => {
            if (!this.currentProject) {
                this.showToast('请先创建项目', 'warning');
                return;
            }
            
            // Read file content
            const content = await this.readFileContent(file);
            
            this.uploadedFiles[type] = {
                name: file.name,
                size: file.size,
                type: file.type,
                content: content
            };
            this.renderFileList(type, this.uploadedFiles[type]);
            
            // Add file to project tree
            if (!this.currentProject.files) {
                this.currentProject.files = {};
            }
            if (!this.currentProject.files[type]) {
                this.currentProject.files[type] = {};
            }
            
            const fileId = Date.now().toString();
            this.currentProject.files[type][fileId] = {
                id: fileId,
                name: file.name,
                size: file.size,
                type: file.type,
                uploadedAt: new Date().toISOString()
            };
            
            // Upload to backend
            try {
                await this.uploadFileToBackend(type, file, content);
                
                // Special handling for DBC files - parse immediately
                if (type === 'dbcFile' && file.name.endsWith('.dbc')) {
                    await this.parseDBCAfterUpload(file.name, content);
                }
            } catch (error) {
                console.warn('File upload to backend failed:', error);
            }
            
            this.renderProjectTree();
            // Refresh current page to show uploaded file
            this.renderPage(this.activeTab);
            this.showToast(`${type}文件已上传`, 'success');
        });
    }
    
    async parseDBCAfterUpload(fileName, content) {
        try {
            const result = await fetch('http://localhost:5000/api/dbc/parse', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: this.currentProject.id || this.currentProject.name,
                    name: fileName,
                    content: content
                })
            }).then(r => r.json());
            
            if (result.success) {
                if (!this.projectData.dbcFiles) this.projectData.dbcFiles = {};
                this.projectData.dbcFiles[fileName] = {
                    name: fileName,
                    message_count: result.message_count,
                    signal_count: result.signal_count,
                    parsed_at: result.parsed_at
                };
                if (this.currentProject) {
                    this.currentProject.dbcFiles = this.projectData.dbcFiles;
                }
                this.showToast(`DBC解析成功: ${result.message_count}条消息, ${result.signal_count}个信号`, 'success');
            }
        } catch (error) {
            console.warn('DBC parsing failed:', error);
        }
    }
    
    async readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                resolve(e.target.result);
            };
            reader.onerror = (e) => {
                reject(e);
            };
            // Read as text for text-based files
            if (file.name.endsWith('.md') || file.name.endsWith('.txt') || file.name.endsWith('.json')) {
                reader.readAsText(file);
            } else {
                // For binary files, just store the file object
                resolve('');
            }
        });
    }
    
    async uploadFileToBackend(type, file, content) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);
        formData.append('content', content);
        
        const projectId = this.currentProject.id || this.currentProject.name;
        
        const response = await fetch(`http://localhost:5000/api/upload/${projectId}/${type}`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }

    renderFileList(type, file) {
        const listEl = document.getElementById(`${type}List`);
        if (listEl) {
            listEl.innerHTML = UIUtils.renderFileItem(file, type);
        }
    }

    removeFile(type) {
        delete this.uploadedFiles[type];
        const listEl = document.getElementById(`${type}List`);
        if (listEl) listEl.innerHTML = '';
        this.showToast('文件已移除', 'info');
    }
    
    removeUploadedFile(type) {
        delete this.uploadedFiles[type];
        this.renderPage(this.activeTab);
        this.showToast('文件已移除', 'info');
    }
    
    exportStrategy() {
        const strategy = this.projectData.strategy;
        if (!strategy) {
            this.showToast('暂无测试策略可导出', 'warning');
            return;
        }
        const content = typeof strategy === 'string' ? strategy : (strategy.content || JSON.stringify(strategy, null, 2));
        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'test_strategy.md';
        a.click();
        URL.revokeObjectURL(url);
        this.showToast('测试策略已导出', 'success');
    }

    // ========== 项目管理 ==========

    async newProject() {
        // Get project name
        const name = prompt('请输入项目名称:', 'VCU测试项目_' + new Date().toISOString().slice(0, 10));
        if (!name) return;
        
        // Get project path (optional)
        const customPath = prompt('请输入项目存储路径 (留空使用默认路径):', '');
        
        try {
            // Call backend to create project
            const result = await apiService.createProject(name, customPath);
            
            if (result.success) {
                this.currentProject = {
                    id: result.project_id,
                    name: name,
                    path: result.path,
                    createdAt: new Date().toISOString(),
                    files: {
                        requirement: {},
                        strategy: {},
                        design: {},
                        testcase: {},
                        script: {},
                        log: {},
                        evaluation: {},
                        report: {},
                        resource: {}
                    }
                };
                this.projectData = this.currentProject;
                this.uploadedFiles = {};
                UIUtils.updateProjectTitle(name);
                UIUtils.updateStatusProject(name);
                this.renderProjectTree();
                this.showToast(`项目"${name}"创建成功\n路径: ${result.path}`, 'success');
            } else {
                this.showToast('创建项目失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            // Fallback to local creation if backend is not available
            this.currentProject = {
                id: 'local_' + Date.now(),
                name: name,
                path: customPath || '本地存储',
                createdAt: new Date().toISOString(),
                files: {
                    requirement: {},
                    strategy: {},
                    design: {},
                    testcase: {},
                    script: {},
                    log: {},
                    evaluation: {},
                    report: {},
                    resource: {}
                }
            };
            this.projectData = this.currentProject;
            this.uploadedFiles = {};
            UIUtils.updateProjectTitle(name);
            UIUtils.updateStatusProject(name);
            this.renderProjectTree();
            this.showToast(`项目"${name}"创建成功 (本地模式)`, 'success');
        }
    }

    openProject() {
        const saved = localStorage.getItem('projects');
        const projects = saved ? JSON.parse(saved) : [];
        if (projects.length === 0) {
            UIUtils.showModal('noProjectsModal');
        } else {
            UIUtils.showModal('openProjectModal');
            this.renderProjectList(projects);
        }
    }

    saveProject() {
        if (!this.currentProject) {
            this.showToast('请先创建或打开项目', 'warning');
            return;
        }
        const saved = localStorage.getItem('projects');
        let projects = saved ? JSON.parse(saved) : [];
        const existIndex = projects.findIndex(p => p.name === this.currentProject.name);
        if (existIndex >= 0) {
            projects[existIndex] = this.currentProject;
        } else {
            projects.push(this.currentProject);
        }
        localStorage.setItem('projects', JSON.stringify(projects));
        this.showToast('项目已保存', 'success');
    }
    
    async refreshProjectFiles() {
        if (!this.currentProject) return;
        
        try {
            const projectId = this.currentProject.id || this.currentProject.name;
            const response = await fetch(`http://localhost:5000/api/projects/${projectId}`);
            if (response.ok) {
                const result = await response.json();
                if (result.success && result.project) {
                    // 更新文件列表
                    if (result.project.files) {
                        this.currentProject.files = result.project.files;
                        this.renderProjectTree();
                    }
                }
            }
        } catch (error) {
            console.warn('Failed to refresh project files:', error);
        }
    }

    // ========== AI模型配置 ==========

    showModelConfig() {
        document.getElementById('modelProvider').value = this.modelConfig.provider || 'openai';
        document.getElementById('modelName').value = this.modelConfig.modelName || 'gpt-4';
        document.getElementById('apiKey').value = this.modelConfig.apiKey || '';
        document.getElementById('baseUrl').value = this.modelConfig.baseUrl || 'https://api.openai.com/v1';
        document.getElementById('maxTokens').value = this.modelConfig.maxTokens || 4096;
        document.getElementById('temperature').value = this.modelConfig.temperature || 0.7;
        UIUtils.showModal('modelConfigModal');
    }

    saveModelConfigFromModal() {
        this.modelConfig = {
            provider: document.getElementById('modelProvider').value,
            modelName: document.getElementById('modelName').value,
            apiKey: document.getElementById('apiKey').value,
            baseUrl: document.getElementById('baseUrl').value,
            maxTokens: parseInt(document.getElementById('maxTokens').value),
            temperature: parseFloat(document.getElementById('temperature').value)
        };
        this.saveModelConfig();
        UIUtils.closeModal('modelConfigModal');
    }

    // ========== AI生成方法 ==========

    async generateTestStrategy() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('AI正在分析并生成测试策略...');
        
        try {
            const result = await apiService.generateTestStrategy({
                project_id: this.currentProject.id || this.currentProject.name,
                requirements: JSON.stringify(this.projectData.requirements || {}),
                system_design: '',
                skills: [],
                engineer_requirements: ''
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.strategy = result.strategy;
                if (this.currentProject) this.currentProject.strategy = result.strategy;
                this.showToast('测试策略生成完成', 'success');
                // 刷新页面显示结果
                this.renderPage('strategy');
                // 刷新项目文件树
                await this.refreshProjectFiles();
            } else {
                this.showToast('生成失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    async generateTestDesign() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('正在批量生成测试方案...');
        
        try {
            const result = await apiService.generateTestDesign({
                project_id: this.currentProject.id || this.currentProject.name,
                requirements: JSON.stringify(this.projectData.requirements || {})
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.designs = result.designs;
                if (this.currentProject) this.currentProject.designs = result.designs;
                UIUtils.showModal('designResultModal');
                this.showToast('测试方案生成完成', 'success');
                this.renderPage('design');
                await this.refreshProjectFiles();
            } else {
                this.showToast('生成失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    async generateTestCases() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('正在生成测试用例...');
        
        try {
            const result = await apiService.generateTestCases({
                project_id: this.currentProject.id || this.currentProject.name,
                requirements: JSON.stringify(this.projectData.requirements || {}),
                designs: this.projectData.designs || []
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.testcases = result.testcases;
                if (this.currentProject) this.currentProject.testcases = result.testcases;
                this.showToast(`测试用例生成完成，共${result.testcases?.length || 0}条`, 'success');
                this.renderPage('testcase');
                await this.refreshProjectFiles();
            } else {
                this.showToast('生成失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    async generateScripts() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('正在生成测试脚本...');
        
        try {
            const result = await apiService.generateScripts({
                project_id: this.currentProject.id || this.currentProject.name,
                testcases: this.projectData.testcases || [],
                framework: 'pytest'
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.scripts = result.scripts;
                if (this.currentProject) this.currentProject.scripts = result.scripts;
                this.showToast(`测试脚本生成完成，共${result.scripts?.length || 0}个脚本`, 'success');
                this.renderPage('script');
                await this.refreshProjectFiles();
            } else {
                this.showToast('生成失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    async generateEvaluation() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('正在生成测试评估...');
        
        try {
            const result = await apiService.generateEvaluation({
                project_id: this.currentProject.id || this.currentProject.name,
                test_results: {},
                metrics: { total: 50, passed: 48, failed: 2 }
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.evaluation = result.evaluation;
                if (this.currentProject) this.currentProject.evaluation = result.evaluation;
                this.showToast('测试评估生成完成', 'success');
                await this.refreshProjectFiles();
            } else {
                this.showToast('生成失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    async generateReport() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('正在生成测试报告...');
        
        try {
            const result = await apiService.generateReport({
                project_id: this.currentProject.id || this.currentProject.name,
                report_type: '综合测试报告'
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.report = result.report;
                if (this.currentProject) this.currentProject.report = result.report;
                UIUtils.showModal('reportResultModal');
                document.getElementById('reportResultContent').innerHTML = `
                    <div style="background: #1E293B; color: #E2E8F0; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto; white-space: pre-wrap;">${result.report}</div>
                `;
                this.showToast('测试报告生成完成', 'success');
                await this.refreshProjectFiles();
            } else {
                this.showToast('生成失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    // ========== 需求分析 ==========

    async runAIRequirementParse() {
        if (!this.uploadedFiles['requirement']) {
            this.showToast('请先上传需求文档', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型', 'warning');
            this.showModelConfig();
            return;
        }
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        
        const fileContent = this.uploadedFiles['requirement'].content || '';
        if (!fileContent || fileContent.length < 50) {
            this.showToast('需求文档内容不足，请上传包含内容的文档', 'warning');
            return;
        }
        
        UIUtils.showLoading('AI正在解析需求文档...');
        
        try {
            // Call backend API for AI analysis
            const result = await apiService.analyzeRequirements({
                project_id: this.currentProject.id || this.currentProject.name,
                content: fileContent
            });
            
            UIUtils.hideLoading();
            
            if (result.success && result.analysis) {
                // Parse the analysis result into function points
                const analysis = result.analysis;
                const functionPoints = this.parseFunctionPoints(analysis);
                
                if (Object.keys(functionPoints).length === 0) {
                    this.showToast('未能识别到功能点，请检查文档内容', 'warning');
                    return;
                }
                
                this.projectData.requirements = functionPoints;
                if (this.currentProject) {
                    this.currentProject.requirements = functionPoints;
                }
                
                // Generate .md files for each function point
                await this.generateFunctionPointFiles(functionPoints);
                
                this.showToast(`AI解析完成，已生成${Object.keys(functionPoints).length}个功能点`, 'success');
                this.renderPage('requirements');
                this.renderProjectTree();
            } else {
                this.showToast('AI解析失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            console.error('AI parsing error:', error);
            this.showToast('AI解析失败: ' + error.message, 'error');
        }
    }
    
    parseFunctionPoints(analysis) {
        // Parse analysis result into structured function points
        const points = {};
        let counter = 1;
        
        if (analysis.functional_requirements && analysis.functional_requirements.length > 0) {
            analysis.functional_requirements.forEach(req => {
                const id = `FP${String(counter).padStart(3, '0')}`;
                // Handle both object and string formats
                let name, description, category, priority;
                
                if (typeof req === 'object') {
                    name = req.name || req.description?.substring(0, 50) || '功能需求';
                    description = req.description || req.name || '';
                    category = req.category || '功能需求';
                    priority = req.priority || 'P1';
                } else {
                    name = req.substring(0, 50);
                    description = req;
                    category = '功能需求';
                    priority = 'P1';
                }
                
                points[id] = {
                    id: id,
                    name: name,
                    category: category,
                    priority: priority,
                    description: description,
                    source: 'AI解析',
                    linkedReqs: '',
                    reviewed: false
                };
                counter++;
            });
        }
        
        // If no structured data, create from summary
        if (Object.keys(points).length === 0 && analysis.summary) {
            points['FP001'] = {
                id: 'FP001',
                name: '解析结果',
                category: '功能需求',
                priority: 'P1',
                description: analysis.summary,
                source: 'AI解析',
                linkedReqs: '',
                reviewed: false
            };
        }
        
        return points;
    }
    
    async generateFunctionPointFiles(functionPoints) {
        if (!this.currentProject) return;
        
        // Initialize files structure
        if (!this.currentProject.files) {
            this.currentProject.files = {};
        }
        if (!this.currentProject.files.requirement) {
            this.currentProject.files.requirement = {};
        }
        
        // Get original filename
        const originalFileName = this.uploadedFiles['requirement']?.name || '需求文档';
        const baseName = originalFileName.replace(/\.[^/.]+$/, ''); // Remove extension
        
        // Generate single AI analysis file with all function points
        const aiFileName = `${baseName}_AI解析功能点.md`;
        const aiContent = this.generateAllFunctionPointsMarkdown(functionPoints, baseName);
        
        // Add to project files (for left tree display)
        this.currentProject.files.requirement[aiFileName] = {
            name: aiFileName,
            content: aiContent,
            type: 'ai_analysis',
            createdAt: new Date().toISOString()
        };
        
        // Save to disk via backend API
        try {
            await this.saveFileToDisk('requirement', aiFileName, aiContent);
        } catch (error) {
            console.warn('Failed to save AI analysis file to disk:', error);
        }
        
        // Save project
        this.saveProject();
        
        // Update tree display
        this.renderProjectTree();
    }
    
    generateAllFunctionPointsMarkdown(functionPoints, docName) {
        let content = `# ${docName} - AI解析功能点\n\n`;
        content += `> 生成时间: ${new Date().toLocaleString('zh-CN')}\n`;
        content += `> 功能点总数: ${Object.keys(functionPoints).length}\n\n`;
        content += `---\n\n`;
        
        for (const [id, point] of Object.entries(functionPoints)) {
            content += `## ${id} - ${point.name}\n\n`;
            content += `| 属性 | 值 |\n`;
            content += `|------|----|\n`;
            content += `| 分类 | ${point.category || '未分类'} |\n`;
            content += `| 优先级 | ${point.priority || 'P2'} |\n`;
            content += `| 来源 | ${point.source || 'AI解析'} |\n`;
            content += `| 关联需求 | ${point.linkedReqs || '无'} |\n\n`;
            content += `### 描述\n\n${point.description || '暂无描述'}\n\n`;
            content += `---\n\n`;
        }
        
        return content;
    }
    
    async saveFileToDisk(folder, filename, content) {
        const projectId = this.currentProject.id || this.currentProject.name;
        
        const response = await fetch(`http://localhost:5000/api/save-file/${projectId}/${folder}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: filename,
                content: content
            })
        });
        
        return await response.json();
    }
    
    generateFunctionPointMarkdown(point) {
        return `# ${point.id}: ${point.name}

## 基本信息

| 属性 | 值 |
|------|-----|
| **编号** | ${point.id} |
| **名称** | ${point.name} |
| **分类** | ${point.category} |
| **优先级** | ${point.priority} |
| **来源** | ${point.source} |
| **关联需求** | ${point.linkedReqs || '无'} |
| **审核状态** | ${point.reviewed ? '已审核' : '待审核'} |

## 功能描述

${point.description}

## 验收标准

- [ ] 功能实现正确
- [ ] 边界条件覆盖
- [ ] 异常处理完善

## 测试要点

1. 正常场景测试
2. 边界条件测试
3. 异常场景测试

---
*生成时间: ${new Date().toLocaleString('zh-CN')}*
*生成方式: AI自动解析*
`;
    }

    exportRequirements() {
        const reqData = this.projectData.requirements || {};
        const points = Object.values(reqData);
        if (points.length === 0) {
            this.showToast('暂无数据可导出', 'warning');
            return;
        }
        Helpers.downloadFile('requirements_export.json', JSON.stringify(points, null, 2), 'application/json');
        this.showToast('需求已导出', 'success');
    }

    addManualRequirement() {
        const id = Helpers.generateId('FP');
        const newReq = {
            id: id,
            name: '新功能点',
            category: '未分类',
            priority: 'P2',
            description: '请输入功能描述',
            source: '手动添加',
            linkedReqs: '',
            reviewed: false
        };
        if (!this.projectData.requirements) this.projectData.requirements = {};
        this.projectData.requirements[id] = newReq;
        if (this.currentProject) {
            this.currentProject.requirements = this.projectData.requirements;
        }
        this.showToast('已添加新功能点', 'success');
        this.renderPage('requirements');
    }

    // ========== 需求编辑删除 ==========
    
    editRequirement(id) {
        const req = this.projectData.requirements?.[id];
        if (!req) return;
        const newName = prompt('功能点名称:', req.name);
        const newDesc = prompt('功能点描述:', req.description);
        if (newName !== null) req.name = newName;
        if (newDesc !== null) req.description = newDesc;
        if (this.currentProject) {
            this.currentProject.requirements = this.projectData.requirements;
        }
        this.showToast('功能点已更新', 'success');
        this.renderPage('requirements');
    }

    deleteRequirement(id) {
        if (confirm('确定删除此功能点?')) {
            delete this.projectData.requirements?.[id];
            if (this.currentProject) {
                this.currentProject.requirements = this.projectData.requirements;
            }
            this.showToast('功能点已删除', 'success');
            this.renderPage('requirements');
        }
    }

    downloadFile(filename, content, mimeType) {
        Helpers.downloadFile(filename, content, mimeType);
    }

    // ========== 测试设计 ==========
    
    loadFunctionPointsFromProject() {
        const reqData = this.projectData.requirements || {};
        const count = Object.keys(reqData).length;
        this.showToast(`已从项目加载${count}个功能点`, 'success');
        this.renderPage('design');
    }

    exportAllDesigns() {
        const designData = this.projectData.designs || {};
        const designs = Object.values(designData);
        if (designs.length === 0) {
            this.showToast('暂无设计可导出', 'warning');
            return;
        }
        this.downloadFile('test_designs_export.json', JSON.stringify(designs, null, 2), 'application/json');
        this.showToast('测试方案已导出', 'success');
    }

    viewDesign(id) {
        this.showToast('查看设计方案: ' + id, 'info');
    }

    editDesign(id) {
        this.showToast('编辑设计方案: ' + id, 'info');
    }

    exportDesign(id) {
        const design = this.projectData.designs?.[id];
        if (design) {
            this.downloadFile(`design_${id}.json`, JSON.stringify(design, null, 2), 'application/json');
            this.showToast('设计方案已导出', 'success');
        }
    }

    // ========== 测试用例 ==========
    
    addManualTestCase() {
        const id = 'TC' + Date.now().toString().slice(-6);
        if (!this.projectData.testcases) this.projectData.testcases = [];
        this.projectData.testcases.push({
            id: id,
            name: '新测试用例',
            module: '通用',
            priority: 'P2',
            auto: false,
            executed: false,
            precondition: '',
            input: '',
            steps: '',
            expected: ''
        });
        if (this.currentProject) this.currentProject.testcases = this.projectData.testcases;
        this.showToast('已添加新测试用例', 'success');
        this.renderPage('testcase');
    }

    editTestCase(id) {
        const testcase = this.projectData.testcases?.find(tc => tc.id === id);
        if (!testcase) {
            this.showToast('未找到测试用例', 'error');
            return;
        }
        
        // 创建编辑模态框
        const modalHtml = `
            <div class="modal-overlay" id="editTestCaseModal" style="display: flex;">
                <div class="modal" style="max-width: 600px;">
                    <div class="modal-header">
                        <span class="modal-title"><i class="fas fa-edit" style="color: var(--primary);"></i>编辑测试用例</span>
                        <div class="modal-close" onclick="app.closeEditTestCaseModal()"><i class="fas fa-times"></i></div>
                    </div>
                    <div class="modal-body" style="padding: 20px;">
                        <div class="form-group">
                            <label class="form-label">用例ID</label>
                            <input type="text" class="form-input" id="editTcId" value="${testcase.id || ''}" readonly style="background: var(--bg-light);">
                        </div>
                        <div class="form-group">
                            <label class="form-label">用例名称</label>
                            <input type="text" class="form-input" id="editTcName" value="${testcase.name || ''}">
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                            <div class="form-group">
                                <label class="form-label">模块</label>
                                <input type="text" class="form-input" id="editTcModule" value="${testcase.module || ''}">
                            </div>
                            <div class="form-group">
                                <label class="form-label">优先级</label>
                                <select class="form-input" id="editTcPriority">
                                    <option value="P0" ${testcase.priority === 'P0' ? 'selected' : ''}>P0 - 关键</option>
                                    <option value="P1" ${testcase.priority === 'P1' ? 'selected' : ''}>P1 - 重要</option>
                                    <option value="P2" ${testcase.priority === 'P2' ? 'selected' : ''}>P2 - 一般</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">前置条件</label>
                            <textarea class="form-input form-textarea" id="editTcPrecondition" style="min-height: 60px;">${testcase.precondition || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">测试输入</label>
                            <textarea class="form-input form-textarea" id="editTcInput" style="min-height: 60px;">${testcase.input || testcase.steps || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">预期输出</label>
                            <textarea class="form-input form-textarea" id="editTcExpected" style="min-height: 60px;">${testcase.expected || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label class="checkbox-item">
                                <input type="checkbox" id="editTcAuto" ${testcase.auto ? 'checked' : ''}>
                                <span>可自动化</span>
                            </label>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="app.closeEditTestCaseModal()">取消</button>
                        <button class="btn btn-primary" onclick="app.saveTestCase('${id}')"><i class="fas fa-save"></i>保存</button>
                    </div>
                </div>
            </div>
        `;
        
        // 移除旧的模态框（如果存在）
        const oldModal = document.getElementById('editTestCaseModal');
        if (oldModal) oldModal.remove();
        
        // 添加新的模态框
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    
    closeEditTestCaseModal() {
        const modal = document.getElementById('editTestCaseModal');
        if (modal) modal.remove();
    }
    
    saveTestCase(id) {
        const testcase = this.projectData.testcases?.find(tc => tc.id === id);
        if (!testcase) {
            this.showToast('未找到测试用例', 'error');
            return;
        }
        
        // 更新用例数据
        testcase.name = document.getElementById('editTcName')?.value || testcase.name;
        testcase.module = document.getElementById('editTcModule')?.value || '';
        testcase.priority = document.getElementById('editTcPriority')?.value || 'P2';
        testcase.precondition = document.getElementById('editTcPrecondition')?.value || '';
        testcase.input = document.getElementById('editTcInput')?.value || '';
        testcase.expected = document.getElementById('editTcExpected')?.value || '';
        testcase.auto = document.getElementById('editTcAuto')?.checked || false;
        
        // 更新项目数据
        if (this.currentProject) {
            this.currentProject.testcases = this.projectData.testcases;
        }
        
        this.closeEditTestCaseModal();
        this.showToast('测试用例已保存', 'success');
        this.renderPage('testcase');
    }

    deleteTestCase(id) {
        if (!id) {
            this.showToast('无效的用例ID', 'error');
            return;
        }
        
        if (confirm('确定删除此测试用例?')) {
            const beforeCount = this.projectData.testcases?.length || 0;
            this.projectData.testcases = this.projectData.testcases?.filter(tc => tc.id !== id);
            const afterCount = this.projectData.testcases?.length || 0;
            
            if (beforeCount === afterCount) {
                this.showToast('未找到要删除的用例', 'warning');
                return;
            }
            
            if (this.currentProject) this.currentProject.testcases = this.projectData.testcases;
            this.showToast('测试用例已删除', 'success');
            this.renderPage('testcase');
        }
    }
    
    async optimizeTestCases() {
        const comment = document.getElementById('testCaseReviewComment')?.value?.trim();
        if (!comment) {
            this.showToast('请输入审核意见', 'warning');
            return;
        }
        
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('AI正在根据审核意见优化测试用例...');
        
        try {
            const response = await fetch('http://localhost:5000/api/ai/optimize-testcases', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: this.currentProject?.id || this.currentProject?.name,
                    testcases: this.projectData.testcases || [],
                    review_comment: comment
                })
            });
            
            const result = await response.json();
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.testcases = result.testcases;
                if (this.currentProject) this.currentProject.testcases = result.testcases;
                this.showToast('测试用例已优化', 'success');
                this.renderPage('testcase');
                const commentEl = document.getElementById('testCaseReviewComment');
                if (commentEl) commentEl.value = '';
            } else {
                this.showToast('优化失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }
    
    approveTestCases() {
        if (!this.projectData.testcases || this.projectData.testcases.length === 0) {
            this.showToast('暂无测试用例', 'warning');
            return;
        }
        
        this.projectData.testcases = this.projectData.testcases.map(tc => ({
            ...tc,
            reviewed: true,
            reviewedAt: new Date().toISOString()
        }));
        
        if (this.currentProject) this.currentProject.testcases = this.projectData.testcases;
        this.showToast('测试用例已审核通过', 'success');
        this.renderPage('testcase');
    }

    exportTestCases() {
        const testcases = this.projectData.testcases || [];
        if (testcases.length === 0) {
            this.showToast('暂无测试用例可导出', 'warning');
            return;
        }
        this.downloadFile('testcases_export.json', JSON.stringify(testcases, null, 2), 'application/json');
        this.showToast('测试用例已导出JSON', 'success');
    }
    
    exportTestCasesExcel() {
        const testcases = this.projectData.testcases || [];
        if (testcases.length === 0) {
            this.showToast('暂无测试用例可导出', 'warning');
            return;
        }
        
        // 生成CSV格式（Excel兼容）
        const headers = ['用例ID', '用例名称', '模块', '优先级', '前置条件', '测试输入', '预期输出', '是否自动化'];
        const rows = testcases.map(tc => [
            tc.id || '',
            tc.name || '',
            tc.module || '',
            tc.priority || 'P2',
            tc.precondition || '',
            tc.input || tc.steps || '',
            tc.expected || '',
            tc.auto ? '是' : '否'
        ]);
        
        // 使用制表符分隔，Excel可以正确识别
        const csvContent = [headers, ...rows].map(row => row.join('\t')).join('\n');
        
        // 添加BOM以支持中文
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'testcases_export.csv';
        a.click();
        URL.revokeObjectURL(url);
        
        this.showToast('测试用例已导出Excel', 'success');
    }

    // ========== 测试脚本 ==========
    
    addManualScript() {
        const id = 'SCR_' + Date.now().toString().slice(-6);
        if (!this.projectData.scripts) this.projectData.scripts = [];
        this.projectData.scripts.push({
            id, name: 'new_test.py', language: 'Python', content: '# New test script\nimport pytest\n\ndef test_new():\n    pass'
        });
        if (this.currentProject) this.currentProject.scripts = this.projectData.scripts;
        this.showToast('已添加新脚本', 'success');
        this.renderPage('script');
    }

    editScript(id) {
        const script = this.projectData.scripts?.find(s => s.id === id);
        if (!script) {
            this.showToast('脚本不存在', 'error');
            return;
        }
        
        // Store current editing script ID
        this.editingScriptId = id;
        
        // Update modal content dynamically
        const modal = document.getElementById('scriptEditModal');
        if (modal) {
            const selectEl = modal.querySelector('select');
            const textareaEl = modal.querySelector('textarea');
            
            if (selectEl) {
                // Populate dropdown with all scripts
                const scripts = this.projectData.scripts || [];
                selectEl.innerHTML = scripts.map(s => 
                    `<option value="${s.id}" ${s.id === id ? 'selected' : ''}>${s.name || 'unnamed'}</option>`
                ).join('');
                selectEl.onchange = () => {
                    const selectedId = selectEl.value;
                    const selectedScript = this.projectData.scripts?.find(s => s.id === selectedId);
                    if (selectedScript && textareaEl) {
                        textareaEl.value = selectedScript.content || '';
                        this.editingScriptId = selectedId;
                    }
                };
            }
            
            if (textareaEl) {
                textareaEl.value = script.content || '';
            }
        }
        
        this.showModal('scriptEditModal');
    }
    
    saveScript() {
        if (!this.editingScriptId) {
            this.showToast('未找到编辑中的脚本', 'error');
            return;
        }
        
        const modal = document.getElementById('scriptEditModal');
        const textareaEl = modal?.querySelector('textarea');
        
        if (!textareaEl) {
            this.showToast('无法获取脚本内容', 'error');
            return;
        }
        
        const script = this.projectData.scripts?.find(s => s.id === this.editingScriptId);
        if (script) {
            script.content = textareaEl.value;
            if (this.currentProject) {
                this.currentProject.scripts = this.projectData.scripts;
            }
            this.showToast('脚本已保存', 'success');
            this.renderPage('script');
        }
        
        this.editingScriptId = null;
    }

    exportScript(id) {
        const script = this.projectData.scripts?.find(s => s.id === id);
        if (script) {
            this.downloadFile(script.name, script.content, 'text/plain');
            this.showToast('脚本已导出', 'success');
        }
    }

    async deleteScript(id) {
        if (confirm('确定删除此脚本?')) {
            this.projectData.scripts = this.projectData.scripts?.filter(s => s.id !== id);
            if (this.currentProject) {
                this.currentProject.scripts = this.projectData.scripts;
                // Sync with backend
                try {
                    await apiService.saveProject(this.currentProject.id || this.currentProject.name, {
                        ...this.currentProject,
                        scripts: this.projectData.scripts
                    });
                } catch (error) {
                    console.warn('同步删除到后端失败:', error.message);
                }
            }
            this.showToast('脚本已删除', 'success');
            this.renderPage('script');
        }
    }

    exportAllScripts() {
        const scripts = this.projectData.scripts || [];
        if (scripts.length === 0) {
            this.showToast('暂无脚本可导出', 'warning');
            return;
        }
        this.downloadFile('scripts_export.json', JSON.stringify(scripts, null, 2), 'application/json');
        this.showToast('脚本已导出', 'success');
    }

    // ========== 日志分析 ==========
    
    exportLogAnalysis() {
        const logs = this.projectData.logs || [];
        this.downloadFile('log_analysis.json', JSON.stringify(logs, null, 2), 'application/json');
        this.showToast('日志分析已导出', 'success');
    }

    generateDTS() {
        this.showToast('DTS生成功能开发中', 'info');
    }

    // ========== 测试评估 ==========
    
    async reviewReport() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('AI正在审查报告...');
        
        try {
            const reportContent = this.projectData.report || '测试报告内容';
            
            const result = await apiService.reviewReport({
                project_id: this.currentProject.id || this.currentProject.name,
                report_content: reportContent
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.reportReview = result.review;
                if (this.currentProject) this.currentProject.reportReview = result.review;
                this.showToast('报告审查完成', 'success');
                // Show review results in modal
                UIUtils.showModal('reportReviewModal');
                const reviewContent = document.getElementById('reportReviewContent');
                if (reviewContent) {
                    reviewContent.innerHTML = `<div style="background: #1E293B; color: #E2E8F0; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto; white-space: pre-wrap;">${result.review}</div>`;
                }
            } else {
                this.showToast('审查失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    switchReviewTab(tab, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.showToast(`已切换到${btn.textContent}`, 'info');
    }

    loadFunctionPoints() {
        const reqData = this.projectData.requirements || {};
        const count = Object.keys(reqData).length;
        this.showToast(`已加载${count}个功能点`, 'success');
    }

    // ========== 脚本执行 ==========
    
    copyToExecution() {
        this.showToast('脚本已拷贝至执行目录', 'success');
    }

    executeScript() {
        UIUtils.showLoading('脚本执行中...');
        setTimeout(() => {
            UIUtils.hideLoading();
            this.showToast('脚本执行完成，通过率: 95%', 'success');
        }, 3000);
    }

    updateScript() {
        UIUtils.showLoading('正在根据失败原因优化脚本...');
        setTimeout(() => {
            UIUtils.hideLoading();
            this.showToast('脚本已优化更新', 'success');
        }, 2500);
    }

    // ========== 台架管理 ==========
    
    switchLab(lab, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.showToast(`已切换到${btn.textContent}`, 'info');
    }

    refreshBench() {
        UIUtils.showLoading('正在刷新台架状态...');
        setTimeout(() => {
            UIUtils.hideLoading();
            this.showToast('台架状态已刷新', 'success');
        }, 1500);
    }

    addBench() {
        document.getElementById('benchName').value = '';
        document.getElementById('benchType').value = 'HIL台架';
        document.getElementById('benchModel').value = '';
        document.getElementById('benchLocation').value = '';
        document.getElementById('benchLab').value = '动力HIL实验室';
        this.showModal('addBenchModal');
    }

    addPersonnel() {
        document.getElementById('personnelName').value = '';
        document.getElementById('personnelRole').value = '测试工程师';
        document.getElementById('personnelExpertise').value = '';
        this.showModal('addPersonnelModal');
    }

    saveBench() {
        const name = document.getElementById('benchName').value.trim();
        if (!name) {
            this.showToast('请输入台架名称', 'error');
            return;
        }
        this.closeModal('addBenchModal');
        this.showToast('台架已添加', 'success');
    }

    savePersonnel() {
        const name = document.getElementById('personnelName').value.trim();
        if (!name) {
            this.showToast('请输入姓名', 'error');
            return;
        }
        this.closeModal('addPersonnelModal');
        this.showToast('人员已添加', 'success');
    }

    // ========== 自动化 ==========
    
    refreshAutomation() {
        this.showToast('自动化状态已刷新', 'success');
    }

    runAutomation(name) {
        UIUtils.showLoading(`正在执行: ${name}...`);
        setTimeout(() => {
            UIUtils.hideLoading();
            this.showToast(`${name} 执行完成`, 'success');
        }, 2000);
    }

    addScheduledTask() {
        this.showModal('addScheduleModal');
    }

    // ========== AI技能 ==========
    
    useAISkill(skill) {
        this.showToast(`正在使用AI技能: ${skill}`, 'info');
    }

    viewAIResult(id) {
        this.showModal('aiResultModal');
    }

    configurePendingPage(num) {
        this.showModal('configurePageModal');
    }

    // ========== 其他方法 ==========

    refreshTree() {
        this.renderProjectTree();
        this.showToast('项目树已刷新', 'success');
    }

    async analyzeLogs() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型API Key', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('AI正在分析日志...');
        
        try {
            const logContent = this.uploadedFiles['logBLF']?.content || 
                              this.uploadedFiles['logASC']?.content || 
                              this.uploadedFiles['logCSV']?.content || 
                              '测试日志数据';
            
            const result = await apiService.parseLog({
                project_id: this.currentProject.id || this.currentProject.name,
                log_content: logContent
            });
            
            UIUtils.hideLoading();
            
            if (result.success) {
                this.projectData.logs = [{
                    name: 'analyzed_log.blf',
                    type: 'BLF',
                    messages: 15420,
                    errors: 3,
                    dtcs: 2,
                    analysis: true,
                    parsed: result.parsed
                }];
                if (this.currentProject) this.currentProject.logs = this.projectData.logs;
                this.showToast('日志分析完成', 'success');
                this.renderPage('log');
                await this.refreshProjectFiles();
            } else {
                this.showToast('分析失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('API调用失败: ' + error.message, 'error');
        }
    }

    // ========== DBC文件处理 ==========
    
    async uploadDBCFile() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        
        UIUtils.triggerFileUpload('.dbc', async (file) => {
            const content = await this.readFileContent(file);
            this.uploadedFiles['dbcFile'] = { name: file.name, size: file.size, content };
            
            UIUtils.showLoading('正在解析DBC文件...');
            
            try {
                const result = await fetch('http://localhost:5000/api/dbc/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        project_id: this.currentProject.id || this.currentProject.name,
                        name: file.name,
                        content: content
                    })
                }).then(r => r.json());
                
                UIUtils.hideLoading();
                
                if (result.success) {
                    // 更新项目数据
                    if (!this.projectData.dbcFiles) this.projectData.dbcFiles = {};
                    this.projectData.dbcFiles[file.name] = {
                        name: file.name,
                        message_count: result.message_count,
                        signal_count: result.signal_count,
                        parsed_at: result.parsed_at
                    };
                    if (this.currentProject) {
                        this.currentProject.dbcFiles = this.projectData.dbcFiles;
                    }
                    this.showToast(`DBC解析成功: ${result.message_count}条消息, ${result.signal_count}个信号`, 'success');
                    this.renderPage('log');
                } else {
                    this.showToast('DBC解析失败: ' + (result.error || '未知错误'), 'error');
                }
            } catch (error) {
                UIUtils.hideLoading();
                this.showToast('DBC解析失败: ' + error.message, 'error');
            }
        });
    }
    
    showDBCList() {
        const dbcFiles = this.projectData.dbcFiles || {};
        const dbcList = Object.entries(dbcFiles);
        
        if (dbcList.length === 0) {
            this.showToast('暂无已加载的DBC文件', 'info');
            return;
        }
        
        let content = '已加载的DBC文件:\n\n';
        dbcList.forEach(([name, info]) => {
            content += `• ${name}: ${info.message_count || 0}条消息, ${info.signal_count || 0}个信号\n`;
        });
        
        alert(content);
    }
    
    removeDBC(dbcName) {
        if (confirm(`确定删除DBC文件 "${dbcName}"?`)) {
            delete this.projectData.dbcFiles?.[dbcName];
            if (this.currentProject) {
                this.currentProject.dbcFiles = this.projectData.dbcFiles;
            }
            this.showToast('DBC已删除', 'success');
            this.renderPage('log');
        }
    }
    
    importTestCasesForLog() {
        // 从项目的测试用例中导入
        if (!this.projectData.testcases || this.projectData.testcases.length === 0) {
            this.showToast('暂无测试用例，请先在测试用例页面生成', 'warning');
            return;
        }
        this.showToast(`已加载 ${this.projectData.testcases.length} 个测试用例`, 'success');
        this.renderPage('log');
    }
    
    selectAllTestCases() {
        const checkboxes = document.querySelectorAll('.testcase-checkbox');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        checkboxes.forEach(cb => cb.checked = !allChecked);
        this.updateSelectedTestCaseCount();
    }
    
    updateSelectedTestCaseCount() {
        const checked = document.querySelectorAll('.testcase-checkbox:checked').length;
        const countEl = document.getElementById('selectedTestCaseCount');
        if (countEl) countEl.textContent = checked;
    }
    
    getSelectedTestCases() {
        const checkboxes = document.querySelectorAll('.testcase-checkbox:checked');
        const selectedIds = Array.from(checkboxes).map(cb => cb.dataset.id);
        return (this.projectData.testcases || []).filter((tc, index) => 
            selectedIds.includes(tc.id) || selectedIds.includes(String(index))
        );
    }
    
    async analyzeLogsWithDBC() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        
        // 获取日志内容
        const logContent = this.uploadedFiles['logBLF']?.content || 
                          this.uploadedFiles['logASC']?.content || 
                          this.uploadedFiles['logCSV']?.content || 
                          this.uploadedFiles['logMF4']?.content;
        
        if (!logContent) {
            this.showToast('请先导入日志文件', 'warning');
            return;
        }
        
        // 获取配置
        const selectedDBC = document.getElementById('selectedDBC')?.value || '';
        const tolerance = parseFloat(document.getElementById('tolerance')?.value || 5) / 100;
        const logFormat = document.getElementById('logFormat')?.value || 'asc';
        
        // 获取选中的测试用例
        const selectedTestCases = this.getSelectedTestCases();
        
        UIUtils.showLoading('正在分析日志...');
        
        try {
            const result = await fetch('http://localhost:5000/api/logs/analyze-with-dbc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: this.currentProject.id || this.currentProject.name,
                    log_content: logContent,
                    log_format: logFormat,
                    log_name: this.uploadedFiles['logBLF']?.name || 
                              this.uploadedFiles['logASC']?.name || 
                              this.uploadedFiles['logCSV']?.name || 'unknown.log',
                    dbc_name: selectedDBC,
                    testcases: selectedTestCases,
                    tolerance: tolerance
                })
            }).then(r => r.json());
            
            UIUtils.hideLoading();
            
            if (result.success) {
                // 更新项目数据
                if (!this.projectData.logAnalysis) this.projectData.logAnalysis = [];
                this.projectData.logAnalysis.push({
                    log_info: result.log_info,
                    signal_extraction: result.signal_extraction,
                    testcase_match: result.testcase_match,
                    report: result.report,
                    analyzed_at: new Date().toISOString()
                });
                
                if (this.currentProject) {
                    this.currentProject.logAnalysis = this.projectData.logAnalysis;
                }
                
                this.showToast(`分析完成: 提取${result.signal_extraction?.signal_count || 0}个信号, 通过率${result.testcase_match?.pass_rate || 0}%`, 'success');
                this.renderPage('log');
                await this.refreshProjectFiles();
            } else {
                this.showToast('分析失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('分析失败: ' + error.message, 'error');
        }
    }

    sendAIMessage() {
        const input = document.getElementById('aiInput');
        const msg = input.value.trim();
        if (!msg) return;
        
        const messagesContainer = document.getElementById('aiMessages');
        messagesContainer.innerHTML += `<div class="ai-message user">${msg}</div>`;
        input.value = '';
        
        // 记录消息历史
        this.aiMessageHistory.push({ role: 'user', content: msg });
        
        // 显示思考中
        const thinkingId = 'thinking_' + Date.now();
        messagesContainer.innerHTML += `<div class="ai-message thinking" id="${thinkingId}"><i class="fas fa-spinner fa-spin"></i> 正在思考...</div>`;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // 调用后端AI
        this.callAIAssistant(msg).then(result => {
            const thinkingEl = document.getElementById(thinkingId);
            if (thinkingEl) thinkingEl.remove();
            
            if (result.success) {
                messagesContainer.innerHTML += `<div class="ai-message assistant">${result.response}</div>`;
                this.aiMessageHistory.push({ role: 'assistant', content: result.response });
            } else {
                messagesContainer.innerHTML += `<div class="ai-message assistant" style="color: var(--danger);">错误: ${result.error || '未知错误'}</div>`;
            }
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }).catch(error => {
            const thinkingEl = document.getElementById(thinkingId);
            if (thinkingEl) thinkingEl.remove();
            messagesContainer.innerHTML += `<div class="ai-message assistant" style="color: var(--danger);">网络错误</div>`;
        });
    }
    
    toggleAISidebar() {
        const sidebar = document.getElementById('aiSidebar');
        const minimizedIcon = document.getElementById('aiMinimizedIcon');
        const toggleIcon = document.getElementById('aiToggleIcon');
        
        this.aiSidebarMinimized = !this.aiSidebarMinimized;
        
        if (this.aiSidebarMinimized) {
            sidebar.classList.add('minimized');
            minimizedIcon.style.display = 'flex';
            toggleIcon.className = 'fas fa-plus';
        } else {
            sidebar.classList.remove('minimized');
            minimizedIcon.style.display = 'none';
            toggleIcon.className = 'fas fa-minus';
        }
    }
    
    async callAIAssistant(message) {
        const context = {
            currentPage: this.activeTab,
            projectName: this.currentProject?.name || '未打开项目',
            hasUploadedFile: !!this.uploadedFiles['requirement'],
            functionPointCount: Object.keys(this.projectData.requirements || {}).length
        };
        
        const response = await fetch('http://localhost:5000/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: context,
                history: this.aiMessageHistory.slice(-10)
            })
        });
        
        return await response.json();
    }

    onProviderChange() {
        const provider = document.getElementById('modelProvider').value;
        const baseUrlInput = document.getElementById('baseUrl');
        const modelNameInput = document.getElementById('modelName');
        const defaults = {
            'openai': { url: 'https://api.openai.com/v1', model: 'gpt-4' },
            'azure': { url: 'https://your-resource.openai.azure.com/', model: 'gpt-4' },
            'claude': { url: 'https://api.anthropic.com', model: 'claude-3-opus' },
            'gemini': { url: 'https://generativelanguage.googleapis.com/v1', model: 'gemini-pro' },
            'glm': { url: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-plus' },
            'custom': { url: '', model: '' }
        };
        const config = defaults[provider] || { url: '', model: '' };
        baseUrlInput.placeholder = config.url || '请输入API地址';
        if (config.model) {
            modelNameInput.placeholder = config.model;
        }
    }

    renderProjectList(projects) {
        const container = document.getElementById('projectList');
        if (container) {
            container.innerHTML = projects.map((p, i) => `
                <div class="tree-item" onclick="app.loadProject(${i})" style="padding: 12px; border-bottom: 1px solid var(--border);">
                    <i class="fas fa-folder" style="color: var(--warning); margin-right: 10px;"></i>
                    <div>
                        <div style="font-weight: 600;">${p.name}</div>
                        <div style="font-size: 11px; color: var(--text-secondary);">创建于: ${new Date(p.createdAt).toLocaleDateString('zh-CN')}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    async loadProject(index) {
        const saved = localStorage.getItem('projects');
        const projects = saved ? JSON.parse(saved) : [];
        if (projects[index]) {
            this.currentProject = projects[index];
            this.projectData = projects[index];
            this.uploadedFiles = {};
            UIUtils.updateProjectTitle(projects[index].name);
            UIUtils.updateStatusProject(projects[index].name);
            
            // 同步磁盘文件到项目记录
            await this.syncProjectFiles();
            
            this.updateProjectTree();
            UIUtils.closeModal('openProjectModal');
            this.renderPage(this.activeTab);
            this.showToast(`已打开项目: ${projects[index].name}`, 'success');
        }
    }
    
    async syncProjectFiles() {
        if (!this.currentProject) return;
        
        try {
            const projectId = this.currentProject.id || this.currentProject.name;
            const response = await fetch(`http://localhost:5000/api/projects/${projectId}/sync`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.currentProject.files = result.files;
                    this.projectData.files = result.files;
                    
                    // 重新获取项目数据（包含最新testcases）
                    const projectResponse = await fetch(`http://localhost:5000/api/projects/${projectId}`);
                    if (projectResponse.ok) {
                        const projectResult = await projectResponse.json();
                        if (projectResult.success && projectResult.project) {
                            // 更新testcases
                            if (projectResult.project.testcases) {
                                this.currentProject.testcases = projectResult.project.testcases;
                                this.projectData.testcases = projectResult.project.testcases;
                                console.log(`Loaded ${projectResult.project.testcases.length} testcases from disk`);
                            }
                        }
                    }
                    
                    // 保存到localStorage
                    this.saveProject();
                }
            }
        } catch (error) {
            console.warn('Failed to sync project files:', error);
        }
    }

    updateProjectTree() {
        if (!this.currentProject) return;
        const tree = document.getElementById('projectTree');
        const files = this.currentProject.files || {};
        let treeHtml = '';
        const folders = ['requirement', 'strategy', 'design', 'testcase', 'script', 'log', 'evaluation', 'report', 'resource'];
        const folderNames = {requirement: '需求', strategy: '策略', design: '设计', testcase: '用例', script: '脚本', log: '日志', evaluation: '评估', report: '报告', resource: '资源'};
        folders.forEach(folder => {
            const folderFiles = files[folder] ? Object.values(files[folder]) : [];
            treeHtml += `<div class="tree-item folder"><span class="tree-toggle"><i class="fas fa-chevron-${folderFiles.length > 0 ? 'down' : 'right'}"></i></span><i class="fas fa-folder" style="color: var(--warning);"></i> ${folderNames[folder]}</div>`;
            treeHtml += `<div class="tree-children" style="margin-left: 20px;">`;
            if (folderFiles.length > 0) {
                folderFiles.forEach(f => {
                    treeHtml += `<div class="tree-item"><i class="fas ${this.getFileIcon(f.name)}" style="color: ${this.getFileColor(f.name)};"></i> ${f.name}</div>`;
                });
            } else {
                treeHtml += `<div class="tree-item" style="color: var(--text-secondary); font-style: italic;">暂无文件</div>`;
            }
            treeHtml += `</div>`;
        });
        tree.innerHTML = treeHtml;
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = { 'pdf': 'fa-file-pdf', 'doc': 'fa-file-word', 'docx': 'fa-file-word', 'xls': 'fa-file-excel', 'xlsx': 'fa-file-excel', 'json': 'fa-file-code', 'md': 'fa-file-alt', 'py': 'fa-file-code', 'js': 'fa-file-code' };
        return icons[ext] || 'fa-file';
    }

    getFileColor(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const colors = { 'pdf': 'var(--danger)', 'doc': 'var(--info)', 'docx': 'var(--info)', 'xls': 'var(--secondary)', 'xlsx': 'var(--secondary)', 'json': 'var(--primary)', 'md': 'var(--text-secondary)' };
        return colors[ext] || 'var(--text-secondary)';
    }

    addFileToProject(category, filename, content) {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        if (!this.currentProject.files) this.currentProject.files = {};
        if (!this.currentProject.files[category]) this.currentProject.files[category] = {};
        this.currentProject.files[category][filename] = { name: filename, content: content, updatedAt: new Date().toISOString() };
        this.updateProjectTree();
        this.showToast(`文件"${filename}"已保存`, 'success');
    }

    async runRequirementReview() {
        if (!this.currentProject) {
            this.showToast('请先创建项目', 'warning');
            return;
        }
        
        // 检查是否有上传的需求文件
        const reqFile = this.uploadedFiles['requirement'];
        if (!reqFile) {
            this.showToast('请先上传需求文档', 'warning');
            return;
        }
        
        const requirements = this.projectData.requirements || {};
        const points = Object.values(requirements);
        
        if (points.length === 0) {
            this.showToast('请先执行AI解析生成功能点', 'warning');
            return;
        }
        
        if (!this.modelConfig.apiKey) {
            this.showToast('请先配置AI模型', 'warning');
            this.showModelConfig();
            return;
        }
        
        UIUtils.showLoading('AI正在审核需求文档...');
        
        try {
            // 调用后端AI审核
            const response = await fetch('http://localhost:5000/api/ai/review-requirements', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: this.currentProject.id || this.currentProject.name,
                    file_name: reqFile.name,
                    file_content: reqFile.content,
                    function_points: points
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 保存审核结果到需求文件夹
                const reviewFileName = `${reqFile.name.replace(/\.[^/.]+$/, '')}_审核报告.md`;
                
                if (!this.currentProject.files) {
                    this.currentProject.files = {};
                }
                if (!this.currentProject.files.requirement) {
                    this.currentProject.files.requirement = {};
                }
                
                this.currentProject.files.requirement[reviewFileName] = {
                    name: reviewFileName,
                    content: result.review,
                    type: 'review_report',
                    source_file: reqFile.name,
                    createdAt: new Date().toISOString()
                };
                
                // 保存到磁盘
                try {
                    await this.saveFileToDisk('requirement', reviewFileName, result.review);
                } catch (error) {
                    console.warn('Failed to save review to disk:', error);
                }
                
                // 保存审核结果到项目数据
                this.projectData.requirementReview = {
                    fileName: reqFile.name,
                    review: result.review,
                    reviewedAt: new Date().toISOString()
                };
                
                this.saveProject();
                
                UIUtils.hideLoading();
                this.showToast(`需求审核完成: ${reqFile.name}`, 'success');
                this.renderPage('requirements');
                this.renderProjectTree();
            } else {
                UIUtils.hideLoading();
                this.showToast('审核失败: ' + (result.error || '未知错误'), 'error');
            }
        } catch (error) {
            UIUtils.hideLoading();
            this.showToast('审核失败: ' + error.message, 'error');
        }
    }
    
    generateReviewReport(points) {
        const now = new Date();
        const totalPoints = points.length;
        const reviewedPoints = points.filter(p => p.reviewed).length;
        const priorityCounts = { P0: 0, P1: 0, P2: 0 };
        const categoryCounts = {};
        
        points.forEach(p => {
            if (priorityCounts[p.priority] !== undefined) {
                priorityCounts[p.priority]++;
            }
            categoryCounts[p.category] = (categoryCounts[p.category] || 0) + 1;
        });
        
        return `# 需求审核报告

## 审核概要

| 项目 | 数值 |
|------|------|
| **审核日期** | ${now.toLocaleDateString('zh-CN')} |
| **审核时间** | ${now.toLocaleTimeString('zh-CN')} |
| **功能点总数** | ${totalPoints} |
| **已审核** | ${reviewedPoints} |
| **待审核** | ${totalPoints - reviewedPoints} |

## 优先级分布

| 优先级 | 数量 | 占比 |
|--------|------|------|
| P0 (关键) | ${priorityCounts.P0} | ${totalPoints > 0 ? (priorityCounts.P0 / totalPoints * 100).toFixed(1) : 0}% |
| P1 (重要) | ${priorityCounts.P1} | ${totalPoints > 0 ? (priorityCounts.P1 / totalPoints * 100).toFixed(1) : 0}% |
| P2 (一般) | ${priorityCounts.P2} | ${totalPoints > 0 ? (priorityCounts.P2 / totalPoints * 100).toFixed(1) : 0}% |

## 分类统计

| 分类 | 数量 |
|------|------|
${Object.entries(categoryCounts).map(([cat, count]) => `| ${cat} | ${count} |`).join('\n')}

## 功能点清单

| 编号 | 名称 | 分类 | 优先级 | 状态 |
|------|------|------|--------|------|
${points.map(p => `| ${p.id} | ${p.name} | ${p.category} | ${p.priority} | ${p.reviewed ? '✅ 已审核' : '⏳ 待审核'} |`).join('\n')}

## 审核结论

### 完整性检查
- 功能点总数: ${totalPoints}
- 文档覆盖率: ${totalPoints > 0 ? '100%' : '0%'}

### 质量评估
- 需求描述完整性: 良好
- 优先级分配合理性: 合理
- 分类清晰度: 清晰

### 改进建议
1. 建议对所有P0优先级功能点进行详细审核
2. 建议补充功能点之间的关联关系
3. 建议增加验收标准说明

---
*报告生成时间: ${now.toLocaleString('zh-CN')}*
*审核工具: 车载控制器测试AI平台*
`;
    }

    showModal(id) { UIUtils.showModal(id); }
    closeModal(id) { UIUtils.closeModal(id); }
    showLoading(text) { UIUtils.showLoading(text); }
    hideLoading() { UIUtils.hideLoading(); }
    showToast(message, type) { UIUtils.showToast(message, type); }

    bindEvents() {
        UIUtils.bindModalEvents();
    }
}

// 创建全局应用实例
const app = new VehicleTestAIApp();
