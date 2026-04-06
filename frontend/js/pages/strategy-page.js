/**
 * 车载控制器测试AI平台 - 测试策略页面
 */

const StrategyPage = {
    /**
     * 渲染测试策略页面
     * @param {Object} app - 主应用实例
     * @returns {string} - HTML字符串
     */
    render(app) {
        const strategy = app.projectData.strategy || null;
        
        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">v2.1</div><div class="dashboard-label">策略版本</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">92%</div><div class="dashboard-label">需求覆盖</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">6</div><div class="dashboard-label">Skills应用</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">15</div><div class="dashboard-label">本月调用</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--primary);"></i>输入文件</span>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                        <div class="form-group">
                            <label class="form-label required">需求文档</label>
                            <div class="upload-zone" style="padding: 16px;" onclick="app.uploadFile('reqDoc')">
                                <div class="upload-icon" style="font-size: 24px;"><i class="fas fa-file-alt"></i></div>
                                <div class="upload-text">点击上传需求文档</div>
                            </div>
                            <div id="reqDocList">${this.renderUploadedFile(app, 'reqDoc')}</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">需求分析结果（可选）</label>
                            <div class="upload-zone" style="padding: 16px;" onclick="app.uploadFile('reqAnalysis')">
                                <div class="upload-icon" style="font-size: 24px;"><i class="fas fa-project-diagram"></i></div>
                                <div class="upload-text">点击读取需求分析结果</div>
                            </div>
                            <div id="reqAnalysisList">${this.renderUploadedFile(app, 'reqAnalysis')}</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">系统设计文档（可选）</label>
                            <div class="upload-zone" style="padding: 16px;" onclick="app.uploadFile('sysDesign')">
                                <div class="upload-icon" style="font-size: 24px;"><i class="fas fa-drafting-compass"></i></div>
                                <div class="upload-text">点击上传系统设计</div>
                            </div>
                            <div id="sysDesignList">${this.renderUploadedFile(app, 'sysDesign')}</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">自定义章节（可选）</label>
                            <div class="upload-zone" style="padding: 16px;" onclick="app.uploadFile('customChapter')">
                                <div class="upload-icon" style="font-size: 24px;"><i class="fas fa-file-word"></i></div>
                                <div class="upload-text">点击上传自定义章节</div>
                            </div>
                            <div id="customChapterList">${this.renderUploadedFile(app, 'customChapter')}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-magic" style="color: var(--secondary);"></i>测试策略Skills选择</span>
                </div>
                <div class="card-body">
                    ${this.renderSkillsSection()}
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-exclamation-triangle" style="color: var(--warning);"></i>项目风险（可选）</span>
                </div>
                <div class="card-body">
                    <textarea class="form-input form-textarea" id="riskDescription" placeholder="描述项目中的已知风险和限制条件..."></textarea>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-comment-dots" style="color: var(--primary);"></i>工程师要求</span>
                </div>
                <div class="card-body">
                    <textarea class="form-input form-textarea" id="engineerRequirements" placeholder="输入对测试策略的具体要求，如测试覆盖度要求、重点测试项、特殊要求等..." style="min-height: 120px;"></textarea>
                </div>
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn btn-primary" style="padding: 12px 40px; font-size: 14px;" onclick="app.generateTestStrategy()"><i class="fas fa-robot"></i> 开始生成测试策略</button>
            </div>
            ${strategy ? this.renderStrategyResult(strategy) : ''}
        `;
    },
    
    /**
     * 渲染已上传的文件
     */
    renderUploadedFile(app, type) {
        const file = app.uploadedFiles[type];
        if (!file) return '';
        
        return `
            <div class="file-item" style="margin-top: 8px; padding: 8px; background: var(--bg-light); border-radius: 6px; display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-file-alt" style="color: var(--primary);"></i>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-size: 12px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${file.name}</div>
                    <div style="font-size: 10px; color: var(--text-secondary);">${(file.size / 1024).toFixed(1)} KB</div>
                </div>
                <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="app.removeUploadedFile('${type}')"><i class="fas fa-trash"></i></button>
            </div>
        `;
    },
    
    /**
     * 渲染生成的测试策略
     */
    renderStrategyResult(strategy) {
        const content = typeof strategy === 'string' ? strategy : (strategy.content || strategy);
        return `
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-alt" style="color: var(--success);"></i>生成的测试策略</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportStrategy()"><i class="fas fa-download"></i>导出</button>
                    </div>
                </div>
                <div class="card-body">
                    <div style="background: #1E293B; color: #E2E8F0; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 500px; overflow-y: auto; white-space: pre-wrap;">${content}</div>
                </div>
            </div>
        `;
    },

    /**
     * 渲染Skills选择区域
     */
    renderSkillsSection() {
        return `
            <div class="subsection">
                <div class="subsection-title"><i class="fas fa-certificate" style="color: var(--info);"></i>标准规范</div>
                <div class="skills-grid">
                    <label class="skill-item"><input type="checkbox" value="iso26262"> <span class="skill-name">ISO26262功能安全</span></label>
                    <label class="skill-item"><input type="checkbox" value="iso21434"> <span class="skill-name">ISO21434网络安全</span></label>
                    <label class="skill-item"><input type="checkbox" value="aspice"> <span class="skill-name">ASPICE过程模型</span></label>
                    <label class="skill-item"><input type="checkbox" value="autosar"> <span class="skill-name">AUTOSAR标准</span></label>
                </div>
            </div>
            <div class="subsection">
                <div class="subsection-title"><i class="fas fa-vial" style="color: var(--warning);"></i>测试方法</div>
                <div class="skills-grid">
                    <label class="skill-item selected"><input type="checkbox" value="hil" checked> <span class="skill-name">HIL测试规范</span></label>
                    <label class="skill-item selected"><input type="checkbox" value="mil" checked> <span class="skill-name">MIL测试规范</span></label>
                    <label class="skill-item"><input type="checkbox" value="sil"> <span class="skill-name">SIL测试规范</span></label>
                    <label class="skill-item"><input type="checkbox" value="pil"> <span class="skill-name">PIL测试规范</span></label>
                </div>
            </div>
            <div class="subsection">
                <div class="subsection-title"><i class="fas fa-car-battery" style="color: var(--primary);"></i>功能域</div>
                <div class="skills-grid">
                    <label class="skill-item selected"><input type="checkbox" value="power" checked> <span class="skill-name">动力系统测试</span></label>
                    <label class="skill-item"><input type="checkbox" value="chassis"> <span class="skill-name">底盘系统测试</span></label>
                    <label class="skill-item"><input type="checkbox" value="body"> <span class="skill-name">车身系统测试</span></label>
                    <label class="skill-item"><input type="checkbox" value="comm"> <span class="skill-name">通信系统测试</span></label>
                </div>
            </div>
            <div class="subsection">
                <div class="subsection-title"><i class="fas fa-shield-alt" style="color: var(--danger);"></i>专项测试</div>
                <div class="skills-grid">
                    <label class="skill-item"><input type="checkbox" value="fault"> <span class="skill-name">故障注入测试</span></label>
                    <label class="skill-item"><input type="checkbox" value="boundary"> <span class="skill-name">边界条件测试</span></label>
                    <label class="skill-item"><input type="checkbox" value="durability"> <span class="skill-name">耐久可靠性测试</span></label>
                    <label class="skill-item"><input type="checkbox" value="emc"> <span class="skill-name">EMC电磁兼容</span></label>
                </div>
            </div>
        `;
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StrategyPage;
}
