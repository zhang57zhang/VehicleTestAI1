/**
 * 车载控制器测试AI平台 - 测试资源页面
 */

const ResourcePage = {
    render(app) {
        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">12</div><div class="dashboard-label">台架总数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">8</div><div class="dashboard-label">空闲台架</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">5</div><div class="dashboard-label">实验室</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">75%</div><div class="dashboard-label">利用率</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-server" style="color: var(--primary);"></i>台架信息管理</span>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.addBench()"><i class="fas fa-plus"></i>添加台架</button>
                </div>
                <div class="card-body">
                    ${this.renderBenchTable()}
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-users" style="color: var(--secondary);"></i>人员信息管理</span>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.addPersonnel()"><i class="fas fa-plus"></i>添加人员</button>
                </div>
                <div class="card-body">
                    ${this.renderPersonnelTable()}
                </div>
            </div>
        `;
    },

    renderBenchTable() {
        return `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>台架名称</th>
                            <th>类型</th>
                            <th>型号</th>
                            <th>位置</th>
                            <th>实验室</th>
                            <th>状态</th>
                            <th>利用率</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>dSPACE HIL #1</td>
                            <td>HIL台架</td>
                            <td>SCALEXIO</td>
                            <td>A区-01</td>
                            <td>动力HIL实验室</td>
                            <td><span class="tag tag-success">空闲</span></td>
                            <td>60%</td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;">编辑</button></td>
                        </tr>
                        <tr>
                            <td>dSPACE HIL #2</td>
                            <td>HIL台架</td>
                            <td>SCALEXIO</td>
                            <td>A区-02</td>
                            <td>动力HIL实验室</td>
                            <td><span class="tag tag-warning">使用中</span></td>
                            <td>85%</td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;">编辑</button></td>
                        </tr>
                        <tr>
                            <td>NI PXI HIL</td>
                            <td>HIL台架</td>
                            <td>PXIe-8880</td>
                            <td>B区-01</td>
                            <td>底盘HIL实验室</td>
                            <td><span class="tag tag-success">空闲</span></td>
                            <td>45%</td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;">编辑</button></td>
                        </tr>
                        <tr>
                            <td>功率台架 #1</td>
                            <td>功率台架</td>
                            <td>CS2000</td>
                            <td>C区-01</td>
                            <td>整车仿真实验室</td>
                            <td><span class="tag tag-warning">维护中</span></td>
                            <td>0%</td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;">编辑</button></td>
                        </tr>
                        <tr>
                            <td>MIL/SIL服务器</td>
                            <td>MIL/SIL</td>
                            <td>Dell PowerEdge</td>
                            <td>D区-机柜1</td>
                            <td>MIL/SIL实验室</td>
                            <td><span class="tag tag-success">运行中</span></td>
                            <td>90%</td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;">编辑</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    },

    renderPersonnelTable() {
        return `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>姓名</th>
                            <th>角色</th>
                            <th>专业领域</th>
                            <th>当前任务</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>张工程师</td>
                            <td>测试负责人</td>
                            <td>VCU HIL测试</td>
                            <td>扭矩测试</td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;">详情</button></td>
                        </tr>
                        <tr>
                            <td>李工程师</td>
                            <td>测试工程师</td>
                            <td>MIL/SIL测试</td>
                            <td>用例设计</td>
                            <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;">详情</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResourcePage;
}
