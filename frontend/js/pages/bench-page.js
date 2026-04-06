/**
 * 车载控制器测试AI平台 - 测试台架看板页面
 */

const BenchPage = {
    render(app) {
        return `
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-building" style="color: var(--primary);"></i>实验室切换</span>
                </div>
                <div class="card-body">
                    <div class="tabs-container">
                        <button class="tab-btn active" onclick="app.switchLab('lab1', this)">动力HIL实验室</button>
                        <button class="tab-btn" onclick="app.switchLab('lab2', this)">底盘HIL实验室</button>
                        <button class="tab-btn" onclick="app.switchLab('lab3', this)">整车仿真实验室</button>
                        <button class="tab-btn" onclick="app.switchLab('lab4', this)">MIL/SIL实验室</button>
                        <button class="tab-btn" onclick="app.switchLab('lab5', this)">环境应力实验室</button>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                        <div style="font-size: 12px; color: var(--text-secondary);">
                            <i class="fas fa-sync fa-spin" style="color: var(--secondary);"></i> 慢速轮询中 (每5分钟更新)
                        </div>
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.refreshBench()"><i class="fas fa-sync"></i>立即刷新</button>
                    </div>
                </div>
            </div>
            ${this.renderBenchCards()}
        `;
    },

    renderBenchCards() {
        const benches = [
            { name: 'dSPACE HIL #1', status: '运行中', location: '动力HIL实验室 - A区-01', temp: '68°C', voltage: '240V', progress: '65%', task: 'VCU_扭矩测试', endTime: '16:30' },
            { name: 'dSPACE HIL #2', status: '待机', location: '动力HIL实验室 - A区-02', temp: '25°C', voltage: '0V', progress: '-', task: '空闲中', endTime: '2小时前' },
            { name: 'NI PXI HIL', status: '运行中', location: '动力HIL实验室 - B区-01', temp: '52°C', voltage: '312V', progress: '42%', task: 'BMS_HIL测试', endTime: '17:45' }
        ];

        return benches.map(b => `
            <div class="bench-card">
                <div class="bench-status">
                    <span class="bench-name">${b.name}</span>
                    <span class="tag tag-${b.status === '运行中' ? 'success' : 'warning'}">${b.status}</span>
                </div>
                <div class="bench-location"><i class="fas fa-map-marker-alt"></i> ${b.location}</div>
                <div class="bench-metrics">
                    <div class="bench-metric">
                        <div class="bench-metric-value">${b.temp}</div>
                        <div class="bench-metric-label">控制器温度</div>
                    </div>
                    <div class="bench-metric">
                        <div class="bench-metric-value">${b.voltage}</div>
                        <div class="bench-metric-label">供电电压</div>
                    </div>
                    <div class="bench-metric">
                        <div class="bench-metric-value">${b.progress}</div>
                        <div class="bench-metric-label">${b.status === '运行中' ? '任务进度' : '无任务'}</div>
                    </div>
                </div>
                <div style="margin-top: 12px; font-size: 11px; color: var(--text-secondary);">
                    ${b.status === '运行中' ? `当前任务: ${b.task} | 预计结束: ${b.endTime}` : `${b.task} | 上次使用: ${b.endTime}`}
                </div>
            </div>
        `).join('');
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = BenchPage;
}
