/**
 * 车载控制器测试AI平台 - 测试评估页面
 */

const EvaluationPage = {
    render(app) {
        const evalData = app.projectData.evaluation || {};
        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">${evalData.coverage || '--'}%</div><div class="dashboard-label">覆盖率</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${evalData.passRate || '--'}%</div><div class="dashboard-label">通过率</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${evalData.defects || 0}</div><div class="dashboard-label">遗留缺陷</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${evalData.grade || '--'}</div><div class="dashboard-label">质量等级</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--primary);"></i>数据源读取</span>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                        ${UIUtils.renderUploadSlot('evalRequirements', '需求文件', 'file-alt', app.uploadedFiles['evalRequirements'])}
                        ${UIUtils.renderUploadSlot('evalDTS', '缺陷DTS', 'bug', app.uploadedFiles['evalDTS'])}
                        ${UIUtils.renderUploadSlot('evalExec', '执行情况', 'clipboard-check', app.uploadedFiles['evalExec'])}
                    </div>
                </div>
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn btn-primary" style="padding: 12px 40px; font-size: 14px;" onclick="app.generateEvaluation()"><i class="fas fa-magic"></i> 生成测试评估</button>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-chart-bar" style="color: var(--secondary);"></i>特性评估</span>
                </div>
                <div class="card-body">
                    ${this.renderEvaluationResults(evalData)}
                </div>
            </div>
        `;
    },

    renderEvaluationResults(evalData) {
        if (!evalData.features) {
            return '<div class="empty-state" style="padding: 30px;"><div style="font-size: 13px;">暂无评估数据，请导入数据并点击"生成测试评估"</div></div>';
        }
        return `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>特性</th>
                            <th>覆盖率</th>
                            <th>通过率</th>
                            <th>缺陷数</th>
                            <th>评估结论</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${(evalData.features || []).map(f => `
                            <tr>
                                <td>${f.name}</td>
                                <td><div class="progress-bar" style="width: 80px;"><div class="progress-fill" style="width: ${f.coverage}%;"></div></div> ${f.coverage}%</td>
                                <td><div class="progress-bar" style="width: 80px;"><div class="progress-fill" style="width: ${f.passRate}%; background: var(--secondary);"></div></div> ${f.passRate}%</td>
                                <td>${f.defects || 0}</td>
                                <td><span class="tag tag-${f.passRate >= 90 ? 'success' : f.passRate >= 70 ? 'warning' : 'danger'}">${f.passRate >= 90 ? '通过' : f.passRate >= 70 ? '待改进' : '不通过'}</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EvaluationPage;
}
