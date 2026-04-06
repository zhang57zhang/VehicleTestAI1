/**
 * 车载控制器测试AI平台 - 测试脚本页面
 */

const ScriptPage = {
    render(app) {
        const scripts = app.projectData.scripts || [];
        
        // 确保每个脚本都有唯一ID
        scripts.forEach((s, index) => {
            if (!s.id) {
                s.id = 'SCR' + String(index + 1).padStart(3, '0');
            }
        });
        app.projectData.scripts = scripts;
        
        const scriptCount = scripts.length;
        const autoCount = scripts.filter(s => s.language === 'Python' || s.language === 'Robot' || s.auto).length;
        const executedCount = scripts.filter(s => s.executed).length;
        const passedCount = scripts.filter(s => s.status === 'passed').length;
        const passRate = executedCount > 0 ? Math.round((passedCount / executedCount) * 100) : 0;

        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">${scriptCount}</div><div class="dashboard-label">脚本总数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${autoCount}</div><div class="dashboard-label">已自动化</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${executedCount}</div><div class="dashboard-label">已执行</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${passRate}%</div><div class="dashboard-label">通过率</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--primary);"></i>输入数据源</span>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px;">
                        ${UIUtils.renderUploadSlot('testCases', '测试用例', 'list-check', app.uploadedFiles['testCases'])}
                        ${UIUtils.renderUploadSlot('autoInterface', '自动化接口表', 'plug', app.uploadedFiles['autoInterface'])}
                        ${UIUtils.renderUploadSlot('autoRules', '自动化规则', 'check-double', app.uploadedFiles['autoRules'])}
                        ${UIUtils.renderUploadSlot('scriptDbc', 'DBC信号', 'database', app.uploadedFiles['scriptDbc'])}
                        ${UIUtils.renderUploadSlot('scriptCan', '通信矩阵', 'project-diagram', app.uploadedFiles['scriptCan'])}
                        ${UIUtils.renderUploadSlot('scriptAlarm', '告警列表', 'bell', app.uploadedFiles['scriptAlarm'])}
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-code" style="color: var(--secondary);"></i>脚本类型与模板</span>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">脚本类型</label>
                        <select class="form-input form-select" id="scriptType">
                            <option value="python">Python + CANoe COM</option>
                            <option value="python_c">Python + CANalyzer</option>
                            <option value="python_dspace">Python + dSPACE</option>
                            <option value="robot">Robot Framework</option>
                            <option value="c">C/C++</option>
                            <option value="matlab">MATLAB/Simulink</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">用例模板</label>
                        <div class="upload-zone" style="padding: 12px;" onclick="app.uploadFile('scriptTemplate')">
                            <div class="upload-icon" style="font-size: 20px;"><i class="fas fa-file-code"></i></div>
                            <div class="upload-text" style="font-size: 11px;">点击上传脚本模板</div>
                            ${app.uploadedFiles['scriptTemplate'] ? `<div style="font-size: 10px; color: var(--secondary);">${app.uploadedFiles['scriptTemplate'].name}</div>` : ''}
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">执行目录配置</label>
                        <input type="text" class="form-input" id="execDir" placeholder="例如: /workspace/tests">
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-comment-dots" style="color: var(--primary);"></i>工程师要求</span>
                </div>
                <div class="card-body">
                    <textarea class="form-input form-textarea" id="scriptRequirements" placeholder="输入脚本开发要求，如命名规范、日志要求、错误处理、报告格式等..."></textarea>
                </div>
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn btn-primary" style="padding: 12px 40px; font-size: 14px;" onclick="app.generateScripts()"><i class="fas fa-magic"></i> 生成测试脚本</button>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-code" style="color: var(--info);"></i>生成的脚本 (${scriptCount}个)</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportAllScripts()"><i class="fas fa-download"></i>导出全部</button>
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.addManualScript()"><i class="fas fa-plus"></i>手动添加</button>
                    </div>
                </div>
                <div class="card-body">
                    ${this.renderScriptsList(scripts)}
                </div>
            </div>
        `;
    },

    renderScriptsList(scripts) {
        if (scripts.length === 0) {
            return '<div class="empty-state" style="padding: 30px;"><div style="font-size: 13px;">暂无脚本，请点击"生成测试脚本"或"手动添加"</div></div>';
        }
        return scripts.map((s, index) => {
            const id = s.id || 'SCR' + String(index + 1).padStart(3, '0');
            const name = s.name || `script_${index + 1}.py`;
            const language = s.language || 'Python';
            const framework = s.framework || 'pytest';
            const content = s.content || '';
            
            return `
            <div class="test-case-item" id="script-${id}" style="margin-bottom: 16px;">
                <div class="test-case-header">
                    <span class="test-case-id">${name}</span>
                    <div>
                        <span class="tag tag-info">${language}</span>
                        <span class="tag tag-success">${framework}</span>
                    </div>
                </div>
                <div style="background: #1E293B; color: #E2E8F0; font-family: 'Consolas', 'Monaco', monospace; padding: 14px; border-radius: 6px; max-height: 300px; overflow-y: auto; margin: 10px 0;">
                    <pre style="font-size: 11px; line-height: 1.5; white-space: pre-wrap; margin: 0;">${content}</pre>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 8px;">
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="app.editScript('${id}')"><i class="fas fa-edit"></i>编辑</button>
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="app.exportScript('${id}')"><i class="fas fa-download"></i>导出</button>
                    <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="app.deleteScript('${id}')"><i class="fas fa-trash"></i>删除</button>
                </div>
            </div>
            `;
        }).join('');
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScriptPage;
}
