/**
 * 车载控制器测试AI平台 - 测试设计页面
 */

const DesignPage = {
    /**
     * 渲染测试设计页面
     * @param {Object} app - 主应用实例
     * @returns {string} - HTML字符串
     */
    render(app) {
        const designData = app.projectData.designs || {};
        const reqData = app.projectData.requirements || {};
        const totalPoints = Object.keys(reqData).length;
        const totalDesigns = Object.keys(designData).length;
        const totalCases = Object.values(designData).reduce((sum, d) => sum + (d.testCases || 0), 0);

        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">${totalPoints || 0}</div><div class="dashboard-label">功能点数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${totalDesigns}</div><div class="dashboard-label">设计方案</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${totalCases}</div><div class="dashboard-label">测试用例</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${totalDesigns > 0 ? Math.round((totalCases / totalDesigns)) : 0}</div><div class="dashboard-label">平均用例/方案</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--primary);"></i>功能点读取</span>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.loadFunctionPointsFromProject()"><i class="fas fa-file-upload"></i>读取功能点列表</button>
                </div>
                <div class="card-body">
                    <div id="functionPointsCheckboxes">
                        ${this.renderFunctionPointsCheckboxes(reqData)}
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-clipboard-list" style="color: var(--secondary);"></i>测试方法选择</span>
                </div>
                <div class="card-body">
                    <div class="checkbox-group" style="margin-bottom: 16px;">
                        <label class="checkbox-item"><input type="checkbox" checked> <span>黑盒测试</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>白盒测试</span></label>
                        <label class="checkbox-item"><input type="checkbox" checked> <span>边界值测试</span></label>
                        <label class="checkbox-item"><input type="checkbox" checked> <span>等价类测试</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>状态机测试</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>场景测试</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>回归测试</span></label>
                    </div>
                    <div class="form-group">
                        <label class="form-label">测试环境（可多选）</label>
                        <div class="checkbox-group">
                            <label class="checkbox-item"><input type="checkbox" checked> <span>HIL台架</span></label>
                            <label class="checkbox-item"><input type="checkbox" checked> <span>MIL环境</span></label>
                            <label class="checkbox-item"><input type="checkbox"> <span>SIL环境</span></label>
                            <label class="checkbox-item"><input type="checkbox"> <span>PIL环境</span></label>
                            <label class="checkbox-item"><input type="checkbox"> <span>实车环境</span></label>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--primary);"></i>测试策略Skills读取</span>
                </div>
                <div class="card-body">
                    <div class="upload-zone" style="padding: 16px;" onclick="app.uploadFile('strategyFile')">
                        <div class="upload-icon" style="font-size: 24px;"><i class="fas fa-file-code"></i></div>
                        <div class="upload-text">点击读取测试策略文件</div>
                    </div>
                    <div id="strategyFileList">
                        ${app.uploadedFiles['strategyFile'] ? this.renderStrategyFileItem(app.uploadedFiles['strategyFile'], app) : ''}
                    </div>
                </div>
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn btn-primary" style="padding: 12px 40px; font-size: 14px;" onclick="app.generateTestDesign()"><i class="fas fa-magic"></i> 批量生成测试方案</button>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-alt" style="color: var(--info);"></i>生成的测试方案</span>
                    <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportAllDesigns()"><i class="fas fa-download"></i>导出全部</button>
                </div>
                <div class="card-body">
                    ${this.renderDesignList(designData)}
                </div>
            </div>
        `;
    },

    /**
     * 渲染功能点复选框
     */
    renderFunctionPointsCheckboxes(reqData) {
        const points = Object.values(reqData);
        if (points.length === 0) {
            return '<div style="font-size: 12px; color: var(--text-secondary);">暂无功能点，请在需求分析页面添加</div>';
        }
        return `
            <div class="checkbox-group" style="margin-bottom: 16px;">
                ${points.map(p => `
                    <label class="checkbox-item"><input type="checkbox" checked> <span>${p.id} ${p.name}</span></label>
                `).join('')}
            </div>
            <div style="font-size: 12px; color: var(--text-secondary);">已选择: <strong>${points.length}</strong> 个功能点</div>
        `;
    },

    /**
     * 渲染策略文件项
     */
    renderStrategyFileItem(file, app) {
        return `
            <div class="file-item">
                <div class="file-icon"><i class="fas fa-file-code"></i></div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-meta">${(file.size / 1024).toFixed(1)} KB</div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-danger" style="padding: 4px 6px;" onclick="app.removeFile('strategyFile')"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;
    },

    /**
     * 渲染设计列表
     */
    renderDesignList(designData) {
        const designs = Object.values(designData);
        if (designs.length === 0) {
            return '<div class="empty-state" style="padding: 30px;"><div style="font-size: 13px;">暂无测试方案，请点击"批量生成测试方案"开始</div></div>';
        }
        return designs.map((d, i) => `
            <div class="test-case-item">
                <div class="test-case-header">
                    <span class="test-case-id">${d.id || 'DP_' + (i+1)} - ${d.name || '测试方案'}</span>
                    <div><span class="tag ${d.completed ? 'tag-success' : 'tag-warning'}">${d.completed ? '已完成' : '待生成'}</span></div>
                </div>
                <div class="test-case-content">
                    <div class="test-case-row"><span class="test-case-label">测试目标:</span><span class="test-case-value">${d.goal || '验证功能正确性'}</span></div>
                    <div class="test-case-row"><span class="test-case-label">测试方法:</span><span class="test-case-value">${d.methods || '黑盒测试'}</span></div>
                    <div class="test-case-row"><span class="test-case-label">测试环境:</span><span class="test-case-value">${d.environments || 'HIL台架'}</span></div>
                    <div class="test-case-row"><span class="test-case-label">用例数量:</span><span class="test-case-value">${d.testCases || 0}个</span></div>
                    <div style="margin-top: 10px;">
                        <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px; margin-right: 6px;" onclick="app.viewDesign('${d.id}')"><i class="fas fa-eye"></i>查看</button>
                        <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px; margin-right: 6px;" onclick="app.editDesign('${d.id}')"><i class="fas fa-edit"></i>编辑</button>
                        <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;" onclick="app.exportDesign('${d.id}')"><i class="fas fa-download"></i>导出</button>
                    </div>
                </div>
            </div>
        `).join('');
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DesignPage;
}
