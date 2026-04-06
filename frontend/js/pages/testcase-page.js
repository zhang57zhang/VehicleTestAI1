/**
 * 车载控制器测试AI平台 - 测试用例页面
 */

const TestCasePage = {
    render(app) {
        // 确保每个用例都有唯一ID - 在render开始时就处理
        const testCases = app.projectData.testcases || [];
        testCases.forEach((tc, index) => {
            if (!tc.id) {
                tc.id = 'TC' + String(index + 1).padStart(3, '0');
            }
        });
        // 同步回app.projectData
        app.projectData.testcases = testCases;
        
        const caseCount = testCases.length;
        const autoCount = testCases.filter(c => c.auto).length;
        const executedCount = testCases.filter(c => c.executed).length;
        const passedCount = testCases.filter(c => c.status === 'passed').length;
        const autoRate = caseCount > 0 ? Math.round((autoCount / caseCount) * 100) : 0;
        const coverageRate = caseCount > 0 ? Math.round((passedCount / caseCount) * 100) : 0;

        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">${caseCount}</div><div class="dashboard-label">用例总数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${autoRate}%</div><div class="dashboard-label">自动化率</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${coverageRate}%</div><div class="dashboard-label">覆盖率</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${executedCount}</div><div class="dashboard-label">已执行</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--primary);"></i>输入数据源</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.generateTestCases()"><i class="fas fa-magic"></i>生成用例</button>
                    </div>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px;">
                        ${UIUtils.renderUploadSlot('testPlan', '测试方案', 'clipboard', app.uploadedFiles['testPlan'])}
                        ${UIUtils.renderUploadSlot('funcList', '功能点列表', 'list', app.uploadedFiles['funcList'])}
                        ${UIUtils.renderUploadSlot('dbc', 'DBC信号', 'database', app.uploadedFiles['dbc'])}
                        ${UIUtils.renderUploadSlot('canMatrix', '通信矩阵', 'project-diagram', app.uploadedFiles['canMatrix'])}
                        ${UIUtils.renderUploadSlot('alarmList', '告警列表', 'bell', app.uploadedFiles['alarmList'])}
                        ${UIUtils.renderUploadSlot('diagList', '诊断列表', 'wrench', app.uploadedFiles['diagList'])}
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-magic" style="color: var(--secondary);"></i>用例设计方法</span>
                </div>
                <div class="card-body">
                    <div class="checkbox-group">
                        <label class="checkbox-item"><input type="checkbox" checked> <span>等价类划分</span></label>
                        <label class="checkbox-item"><input type="checkbox" checked> <span>边界值分析</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>判定表法</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>状态迁移</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>因果图法</span></label>
                        <label class="checkbox-item"><input type="checkbox"> <span>正交试验</span></label>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-list-check" style="color: var(--info);"></i>生成的测试用例 (${caseCount}条)</span>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" class="form-input" style="width: 160px; padding: 6px 10px; font-size: 12px;" placeholder="搜索用例...">
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportTestCasesExcel()"><i class="fas fa-file-excel"></i>导出Excel</button>
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportTestCases()"><i class="fas fa-file-code"></i>导出JSON</button>
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.addManualTestCase()"><i class="fas fa-plus"></i>手动添加</button>
                    </div>
                </div>
                <div class="card-body">
                    ${this.renderTestCasesList(testCases, app)}
                </div>
            </div>
            ${testCases.length > 0 ? this.renderReviewSection() : ''}
        `;
    },
    
    renderReviewSection() {
        return `
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-comments" style="color: var(--success);"></i>用例审核与优化</span>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">审核意见</label>
                        <textarea class="form-input form-textarea" id="testCaseReviewComment" placeholder="请输入对测试用例的审核意见，AI将根据您的意见进行优化修改...例如：&#10;- 用例覆盖不够全面，需要增加边界值测试&#10;- 某些用例的前置条件描述不清晰&#10;- 需要增加异常场景的测试用例" style="min-height: 100px;"></textarea>
                    </div>
                    <div style="display: flex; gap: 8px; margin-top: 12px;">
                        <button class="btn btn-primary" style="padding: 8px 16px; font-size: 12px;" onclick="app.optimizeTestCases()"><i class="fas fa-magic"></i> AI优化用例</button>
                        <button class="btn btn-secondary" style="padding: 8px 16px; font-size: 12px;" onclick="app.approveTestCases()"><i class="fas fa-check"></i> 确认通过</button>
                    </div>
                </div>
            </div>
        `;
    },

    renderTestCasesList(testCases, app) {
        if (testCases.length === 0) {
            return '<div class="empty-state" style="padding: 30px;"><div style="font-size: 13px;">暂无测试用例，请点击"生成用例"或"手动添加"</div></div>';
        }
        
        // 确保每个用例都有唯一ID
        testCases.forEach((tc, index) => {
            if (!tc.id) {
                tc.id = 'TC' + String(index + 1).padStart(3, '0');
            }
        });
        
        return testCases.map((c, index) => `
            <div class="test-case-item" id="testCase-${c.id}">
                <div class="test-case-header">
                    <span class="test-case-id">${c.id}</span>
                    <div>
                        <span class="tag tag-${c.priority === 'P0' ? 'danger' : c.priority === 'P1' ? 'warning' : 'info'}">${c.priority || 'P2'}</span>
                        <span class="tag tag-${c.auto ? 'success' : 'warning'}">${c.auto ? '可自动化' : '待自动化'}</span>
                        ${c.reviewed ? '<span class="tag tag-success">已审核</span>' : ''}
                    </div>
                </div>
                <div class="test-case-content">
                    <div class="test-case-row"><span class="test-case-label">用例名称:</span><span class="test-case-value">${c.name || '未命名'}</span></div>
                    <div class="test-case-row"><span class="test-case-label">前置条件:</span><span class="test-case-value">${c.precondition || '无'}</span></div>
                    <div class="test-case-row"><span class="test-case-label">测试输入:</span><span class="test-case-value">${c.input || c.steps || '无'}</span></div>
                    <div class="test-case-row"><span class="test-case-label">预期输出:</span><span class="test-case-value">${c.expected || '无'}</span></div>
                    <div style="margin-top: 10px;">
                        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="app.editTestCase('${c.id}')"><i class="fas fa-edit"></i>编辑</button>
                        <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="app.deleteTestCase('${c.id}')"><i class="fas fa-trash"></i>删除</button>
                    </div>
                </div>
            </div>
        `).join('');
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestCasePage;
}
