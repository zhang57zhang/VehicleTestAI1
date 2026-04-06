/**
 * 车载控制器测试AI平台 - 测试报告页面
 */

const ReportPage = {
    render(app) {
        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">8</div><div class="dashboard-label">报告总数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">v3.2</div><div class="dashboard-label">最新版本</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">2024-01-15</div><div class="dashboard-label">最新生成</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">待审查</div><div class="dashboard-label">完整性状态</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--primary);"></i>报告模板与数据</span>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                        <div class="upload-zone" style="padding: 16px;" onclick="app.uploadFile('reportTemplate')">
                            <div class="upload-icon" style="font-size: 24px;"><i class="fas fa-file-word"></i></div>
                            <div class="upload-text">读取报告模板</div>
                        </div>
                        <div class="upload-zone" style="padding: 16px;" onclick="app.uploadFile('testResults')">
                            <div class="upload-icon" style="font-size: 24px;"><i class="fas fa-database"></i></div>
                            <div class="upload-text">读取测试结果数据</div>
                        </div>
                    </div>
                </div>
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn btn-primary" style="padding: 12px 40px; font-size: 14px;" onclick="app.generateReport()"><i class="fas fa-magic"></i> 生成测试报告</button>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-alt" style="color: var(--info);"></i>报告预览</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;"><i class="fas fa-eye"></i>预览</button>
                        <button class="btn btn-success" style="padding: 6px 12px; font-size: 12px;"><i class="fas fa-download"></i>导出</button>
                    </div>
                </div>
                <div class="card-body" style="background: #FAFBFC; padding: 30px;">
                    ${this.renderReportPreview()}
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-search" style="color: var(--secondary);"></i>AI完整性审查</span>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.reviewReport()"><i class="fas fa-magic"></i>执行审查</button>
                </div>
                <div class="card-body">
                    ${this.renderReviewResults()}
                </div>
            </div>
        `;
    },

    renderReportPreview() {
        return `
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="font-size: 24px; font-weight: 700; margin-bottom: 10px;">VCU控制器测试报告</h1>
                <div style="font-size: 14px; color: var(--text-secondary);">版本: v3.2 | 日期: 2024-01-15 | 状态: 待审查</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px;">
                <div style="text-align: center; padding: 16px; background: white; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="font-size: 28px; font-weight: 700; color: var(--primary);">128</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">用例总数</div>
                </div>
                <div style="text-align: center; padding: 16px; background: white; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="font-size: 28px; font-weight: 700; color: var(--secondary);">115</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">通过用例</div>
                </div>
                <div style="text-align: center; padding: 16px; background: white; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="font-size: 28px; font-weight: 700; color: var(--danger);">13</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">失败用例</div>
                </div>
                <div style="text-align: center; padding: 16px; background: white; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="font-size: 28px; font-weight: 700; color: var(--primary);">89.8%</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">通过率</div>
                </div>
            </div>
            <div style="background: white; border-radius: 8px; padding: 20px; border: 1px solid var(--border);">
                <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">测试结论</h3>
                <p style="font-size: 13px; line-height: 1.8; color: var(--text-primary);">本次测试覆盖VCU控制器扭矩管理、功率限制、故障诊断等核心功能，共执行128个测试用例，通过115个，失败13个，通过率89.8%。失败的用例主要集中在功率限制边界条件测试，已提交缺陷跟踪系统，建议在下一迭代中重点回归验证。</p>
            </div>
        `;
    },

    renderReviewResults() {
        return `
            <div class="review-result review-pass">
                <div class="review-title"><i class="fas fa-check-circle" style="color: var(--secondary);"></i> 报告格式完整性</div>
                <div class="review-content">✓ 包含执行摘要、测试环境、测试结果、缺陷分析、结论建议</div>
            </div>
            <div class="review-result review-pass">
                <div class="review-title"><i class="fas fa-check-circle" style="color: var(--secondary);"></i> 数据一致性</div>
                <div class="review-content">✓ 报告数据与测试执行记录一致</div>
            </div>
            <div class="review-result review-warning">
                <div class="review-title"><i class="fas fa-exclamation-triangle" style="color: var(--warning);"></i> 建议补充</div>
                <div class="review-content">⚠ 建议补充风险分析和遗留问题说明章节</div>
            </div>
        `;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReportPage;
}
