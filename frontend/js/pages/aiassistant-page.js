/**
 * 车载控制器测试AI平台 - AI辅助看板页面
 */

const AIAssistantPage = {
    async render(app) {
        // 从后端获取真实的AI统计数据
        let stats = { total_calls: 0, hours_saved: 0, adoption_rate: 100, active_skills: 0 };
        let skillUsage = {};
        let history = [];
        
        try {
            const response = await fetch('http://localhost:5000/api/ai/stats');
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    stats = result.stats;
                    skillUsage = result.skill_usage;
                    history = result.history;
                }
            }
        } catch (e) {
            console.warn('Failed to load AI stats:', e);
        }

        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">${stats.total_calls || 0}</div><div class="dashboard-label">AI调用次数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${stats.hours_saved || 0}</div><div class="dashboard-label">本月节省工时</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${stats.adoption_rate || 100}%</div><div class="dashboard-label">AI采纳率</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${stats.active_skills || 0}</div><div class="dashboard-label">活跃技能</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-magic" style="color: var(--primary);"></i>AI技能使用统计</span>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px;">
                        ${this.renderSkillCards(skillUsage)}
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-history" style="color: var(--secondary);"></i>最近AI交互记录</span>
                </div>
                <div class="card-body">
                    ${this.renderAIHistoryTable(history)}
                </div>
            </div>
        `;
    },

    renderSkillCards(skillUsage) {
        const skills = [
            { icon: 'fa-file-alt', color: 'var(--danger)', name: '需求分析' },
            { icon: 'fa-chess', color: 'var(--primary)', name: '策略生成' },
            { icon: 'fa-pencil-ruler', color: 'var(--secondary)', name: '测试设计' },
            { icon: 'fa-list-check', color: 'var(--warning)', name: '用例生成' },
            { icon: 'fa-code', color: 'var(--info)', name: '脚本生成' },
            { icon: 'fa-file-invoice', color: 'var(--danger)', name: '报告生成' }
        ];

        return skills.map(s => {
            const usage = skillUsage[s.name] || { count: 0, last_used: null };
            const isActive = usage.count > 0;
            return `
                <div class="bench-card" style="text-align: center; cursor: pointer;" onclick="app.useAISkill('${s.name}')">
                    <div style="font-size: 28px; color: ${s.color}; margin-bottom: 8px;"><i class="fas ${s.icon}"></i></div>
                    <div style="font-weight: 600; font-size: 12px;">${s.name}</div>
                    <div style="font-size: 10px; color: var(--text-secondary);">使用${usage.count}次</div>
                    <div style="margin-top: 8px;"><span class="tag ${isActive ? 'tag-success' : 'tag-warning'}">${isActive ? '活跃' : '未使用'}</span></div>
                </div>
            `;
        }).join('');
    },

    renderAIHistoryTable(history) {
        if (!history || history.length === 0) {
            return '<div class="empty-state" style="padding: 30px;"><div style="font-size: 13px;">暂无AI交互记录，开始使用AI功能后将自动记录</div></div>';
        }

        const statusClass = { '成功': 'tag-success', '失败': 'tag-danger', '待优化': 'tag-warning' };

        return `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>技能类型</th>
                            <th>请求内容</th>
                            <th>状态</th>
                            <th>耗时</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${history.map((h, i) => `
                            <tr>
                                <td>${new Date(h.time).toLocaleString('zh-CN')}</td>
                                <td><span class="tag tag-primary">${h.type}</span></td>
                                <td>${h.content}</td>
                                <td><span class="tag ${statusClass[h.status] || 'tag-info'}">${h.status}</span></td>
                                <td>${h.duration}</td>
                                <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="app.viewAIResult('${h.id}')"><i class="fas fa-eye"></i>查看</button></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIAssistantPage;
}
