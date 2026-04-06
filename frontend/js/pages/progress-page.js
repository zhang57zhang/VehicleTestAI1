/**
 * 车载控制器测试AI平台 - 测试进度看板页面
 */

const ProgressPage = {
    render(app) {
        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">68%</div><div class="dashboard-label">整体进度</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">5</div><div class="dashboard-label">剩余工作日</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">2</div><div class="dashboard-label">风险项</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">正常</div><div class="dashboard-label">项目状态</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-tasks" style="color: var(--primary);"></i>测试阶段管理</span>
                </div>
                <div class="card-body" style="padding: 0;">
                    ${this.renderPhaseList()}
                </div>
            </div>
        `;
    },

    renderPhaseList() {
        const phases = [
            { name: '需求分析', timeline: '01-01 ~ 01-10', progress: 100, owner: '张工', status: '已完成' },
            { name: '测试策略', timeline: '01-11 ~ 01-15', progress: 100, owner: '李工', status: '已完成' },
            { name: '测试设计', timeline: '01-16 ~ 01-25', progress: 85, owner: '王工', status: '进行中' },
            { name: '用例设计', timeline: '01-26 ~ 02-05', progress: 45, owner: '赵工', status: '进行中' },
            { name: '脚本开发', timeline: '02-06 ~ 02-20', progress: 0, owner: '周工', status: '待开始' },
            { name: '测试执行', timeline: '02-21 ~ 03-15', progress: 0, owner: '陈工', status: '待开始' },
            { name: '报告编制', timeline: '03-16 ~ 03-25', progress: 0, owner: '吴工', status: '待开始' }
        ];

        return phases.map(p => `
            <div class="phase-item">
                <div class="phase-name">${p.name}</div>
                <div class="phase-timeline">${p.timeline}</div>
                <div class="phase-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${p.progress}%; ${p.progress === 100 ? 'background: var(--secondary);' : ''}"></div>
                    </div>
                </div>
                <div class="phase-owner">${p.owner}</div>
                <div class="phase-status">
                    <span class="tag tag-${p.status === '已完成' ? 'success' : p.status === '进行中' ? 'info' : ''}">${p.status}</span>
                </div>
            </div>
        `).join('');
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProgressPage;
}
