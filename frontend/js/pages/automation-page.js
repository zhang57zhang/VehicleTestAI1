/**
 * 车载控制器测试AI平台 - 自动化看板页面
 */

const AutomationPage = {
    render(app) {
        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">156</div><div class="dashboard-label">脚本总数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">128</div><div class="dashboard-label">已自动化</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">82%</div><div class="dashboard-label">自动化率</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">89%</div><div class="dashboard-label">通过率</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-tachometer-alt" style="color: var(--primary);"></i>自动化执行概览</span>
                    <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.refreshAutomation()"><i class="fas fa-sync"></i>刷新</button>
                </div>
                <div class="card-body">
                    ${this.renderAutomationTable()}
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-clock" style="color: var(--secondary);"></i>定时执行任务</span>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.addScheduledTask()"><i class="fas fa-plus"></i>添加任务</button>
                </div>
                <div class="card-body">
                    ${this.renderScheduledTasks()}
                </div>
            </div>
        `;
    },

    renderAutomationTable() {
        return `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>脚本名称</th>
                            <th>用例数</th>
                            <th>执行次数</th>
                            <th>通过率</th>
                            <th>上次执行</th>
                            <th>状态</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>扭矩请求测试套件</td>
                            <td>15</td>
                            <td>45</td>
                            <td><div class="progress-bar" style="width: 80px;"><div class="progress-fill" style="width: 93%; background: var(--secondary);"></div></div> 93%</td>
                            <td>2024-01-15 16:30</td>
                            <td><span class="tag tag-success"><i class="fas fa-check"></i>正常</span></td>
                            <td><button class="btn btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="app.runAutomation('torque')"><i class="fas fa-play"></i>执行</button></td>
                        </tr>
                        <tr>
                            <td>功率限制测试套件</td>
                            <td>12</td>
                            <td>38</td>
                            <td><div class="progress-bar" style="width: 80px;"><div class="progress-fill" style="width: 85%; background: var(--secondary);"></div></div> 85%</td>
                            <td>2024-01-15 15:20</td>
                            <td><span class="tag tag-success"><i class="fas fa-check"></i>正常</span></td>
                            <td><button class="btn btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="app.runAutomation('power')"><i class="fas fa-play"></i>执行</button></td>
                        </tr>
                        <tr>
                            <td>故障诊断测试套件</td>
                            <td>20</td>
                            <td>52</td>
                            <td><div class="progress-bar" style="width: 80px;"><div class="progress-fill" style="width: 78%; background: var(--warning);"></div></div> 78%</td>
                            <td>2024-01-15 14:10</td>
                            <td><span class="tag tag-warning"><i class="fas fa-exclamation"></i>待优化</span></td>
                            <td><button class="btn btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="app.runAutomation('diag')"><i class="fas fa-play"></i>执行</button></td>
                        </tr>
                        <tr>
                            <td>能量回收测试套件</td>
                            <td>8</td>
                            <td>15</td>
                            <td><div class="progress-bar" style="width: 80px;"><div class="progress-fill" style="width: 95%; background: var(--secondary);"></div></div> 95%</td>
                            <td>2024-01-15 11:00</td>
                            <td><span class="tag tag-success"><i class="fas fa-check"></i>正常</span></td>
                            <td><button class="btn btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="app.runAutomation('recycle')"><i class="fas fa-play"></i>执行</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    },

    renderScheduledTasks() {
        return `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>任务名称</th>
                            <th>执行套件</th>
                            <th>执行计划</th>
                            <th>下次执行</th>
                            <th>状态</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>每日回归测试</td>
                            <td>扭矩+功率测试套件</td>
                            <td>每日 18:00</td>
                            <td>明天 18:00</td>
                            <td><span class="tag tag-success">启用</span></td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;"><i class="fas fa-pause"></i>暂停</button></td>
                        </tr>
                        <tr>
                            <td>每周全面测试</td>
                            <td>全部测试套件</td>
                            <td>每周五 20:00</td>
                            <td>周五 20:00</td>
                            <td><span class="tag tag-success">启用</span></td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;"><i class="fas fa-pause"></i>暂停</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutomationPage;
}
