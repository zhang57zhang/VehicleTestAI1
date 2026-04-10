/**
 * 测试执行页面 (TE - Test Execution)
 * 对应测试活动: ACT-TE-*
 */

const ExecutionPage = {
    render: function(app) {
        const project = app.currentProject;
        
        if (!project) {
            return '<div class="page-header"><h2><i class="fas fa-play-circle"></i> 测试执行</h2></div>' +
                   '<div class="empty-state"><div class="empty-state-title">请先打开项目</div></div>';
        }
        
        const testcases = app.projectData.testcases || [];
        const executedCount = testcases.filter(tc => tc.executed).length;
        
        return '<div class="page-header"><h2><i class="fas fa-play-circle"></i> 测试执行</h2>' +
               '<p class="page-subtitle">执行测试用例并记录结果 (ACT-TE-*)</p></div>' +
               '<div class="stats-grid">' +
               '<div class="stat-card"><div class="stat-value">' + testcases.length + '</div><div class="stat-label">总用例数</div></div>' +
               '<div class="stat-card"><div class="stat-value">' + executedCount + '</div><div class="stat-label">已执行</div></div>' +
               '</div>' +
               '<div class="section-card"><div class="section-header"><h3>执行控制</h3></div>' +
               '<div class="section-body">' +
               '<select id="executionEnv" class="form-select">' +
               '<option value="HIL">HIL (硬件在环)</option>' +
               '<option value="SIL">SIL (软件在环)</option>' +
               '<option value="Manual">手动执行</option>' +
               '</select>' +
               '<button class="btn btn-primary" onclick="ExecutionPage.startExecution()">开始执行</button>' +
               '</div></div>' +
               '<div class="section-card"><div class="section-header"><h3>用例列表</h3></div>' +
               '<div class="section-body">' + this.renderTestcaseList(testcases) + '</div></div>';
    },
    
    renderTestcaseList: function(testcases) {
        if (testcases.length === 0) {
            return '<div class="empty-state"><div class="empty-state-title">暂无测试用例</div></div>';
        }
        
        var html = '<table class="data-table"><thead><tr><th>ID</th><th>名称</th><th>优先级</th><th>状态</th></tr></thead><tbody>';
        testcases.forEach(function(tc) {
            html += '<tr><td>' + tc.id + '</td><td>' + tc.name + '</td><td>' + (tc.priority || 'P2') + '</td>' +
                    '<td>' + (tc.executed ? '已执行' : '待执行') + '</td></tr>';
        });
        html += '</tbody></table>';
        return html;
    },
    
    startExecution: function() {
        var env = document.getElementById('executionEnv').value;
        console.log('开始执行:', env);
        alert('开始执行测试 (环境: ' + env + ')');
    }
};

if (typeof window !== 'undefined') {
    window.ExecutionPage = ExecutionPage;
}
