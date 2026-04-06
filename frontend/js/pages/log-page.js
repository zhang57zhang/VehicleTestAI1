/**
 * 车载控制器测试AI平台 - 测试日志页面
 * 支持DBC导入、信号提取、测试用例匹配
 */

const LogPage = {
    render(app) {
        const logs = app.projectData.logs || [];
        const dbcFiles = app.projectData.dbcFiles || {};
        const testcases = app.projectData.testcases || [];
        const logAnalysis = app.projectData.logAnalysis || [];
        
        // 统计数据
        const totalSignals = logAnalysis.reduce((sum, a) => sum + (a.signal_extraction?.signal_count || 0), 0);
        const avgPassRate = logAnalysis.length > 0 
            ? Math.round(logAnalysis.reduce((sum, a) => sum + (a.testcase_match?.pass_rate || 0), 0) / logAnalysis.length)
            : 0;

        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">${logs.length}</div><div class="dashboard-label">日志文件</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${Object.keys(dbcFiles).length}</div><div class="dashboard-label">DBC文件</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${totalSignals}</div><div class="dashboard-label">提取信号</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${avgPassRate}%</div><div class="dashboard-label">平均通过率</div></div>
            </div>
            
            <!-- 日志文件导入 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-file-import" style="color: var(--secondary);"></i>日志文件导入</span>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px;">
                        ${UIUtils.renderUploadSlot('logBLF', 'BLF日志', 'file', app.uploadedFiles['logBLF'])}
                        ${UIUtils.renderUploadSlot('logASC', 'ASC日志', 'file-alt', app.uploadedFiles['logASC'])}
                        ${UIUtils.renderUploadSlot('logCSV', 'CSV日志', 'file-csv', app.uploadedFiles['logCSV'])}
                        ${UIUtils.renderUploadSlot('logMF4', 'MF4日志', 'file', app.uploadedFiles['logMF4'])}
                    </div>
                </div>
            </div>
            
            <!-- DBC导入功能 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-database" style="color: var(--primary);"></i>DBC导入功能</span>
                    <span class="tag tag-info">${Object.keys(dbcFiles).length}个已加载</span>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 12px; color: var(--text-secondary); font-size: 12px;">
                        导入DBC文件后，日志分析将根据DBC定义解析CAN信号
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                        ${UIUtils.renderUploadSlot('dbcFile', 'DBC文件 (.dbc)', 'database', app.uploadedFiles['dbcFile'])}
                        ${UIUtils.renderUploadSlot('arxmlFile', 'ARXML文件 (.arxml)', 'file-code', app.uploadedFiles['arxmlFile'])}
                    </div>
                    ${this.renderDBCList(dbcFiles)}
                </div>
            </div>
            
            <!-- 测试用例导入 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-check-square" style="color: var(--info);"></i>测试用例匹配</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="app.selectAllTestCases()">
                            <i class="fas fa-check-double"></i> 全选
                        </button>
                        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="app.importTestCasesForLog()">
                            <i class="fas fa-file-import"></i> 导入用例
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 12px;">
                        <label class="form-label">选择测试用例进行信号匹配验证：</label>
                    </div>
                    ${this.renderTestCaseSelection(testcases, app)}
                </div>
            </div>
            
            <!-- 分析配置 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-cog" style="color: var(--warning);"></i>分析配置</span>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                        <div class="form-group">
                            <label class="form-label">选择DBC</label>
                            <select class="form-input form-select" id="selectedDBC">
                                <option value="">-- 不使用DBC --</option>
                                ${Object.keys(dbcFiles).map(name => `<option value="${name}">${name} (${dbcFiles[name].signal_count || 0}信号)</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">容差范围 (%)</label>
                            <input type="number" class="form-input" id="tolerance" value="5" min="0" max="50" step="1">
                        </div>
                        <div class="form-group">
                            <label class="form-label">日志格式</label>
                            <select class="form-input form-select" id="logFormat">
                                <option value="asc">ASC格式</option>
                                <option value="blf">BLF格式</option>
                                <option value="csv">CSV格式</option>
                                <option value="mf4">MF4格式</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 分析按钮 -->
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn btn-primary" style="padding: 12px 40px; font-size: 14px;" onclick="app.analyzeLogsWithDBC()">
                    <i class="fas fa-magic"></i> 分析日志并匹配测试用例
                </button>
            </div>
            
            <!-- 分析结果 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-chart-bar" style="color: var(--success);"></i>分析结果</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportLogAnalysis()">
                            <i class="fas fa-download"></i>导出分析
                        </button>
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.generateDTS()">
                            <i class="fas fa-file-medical"></i>生成DTS
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    ${this.renderAnalysisResults(logAnalysis)}
                </div>
            </div>
        `;
    },

    renderDBCList(dbcFiles) {
        const dbcList = Object.entries(dbcFiles);
        if (dbcList.length === 0) {
            return '<div style="color: var(--text-secondary); font-size: 12px; margin-top: 8px;">暂无已加载的DBC文件</div>';
        }
        
        return `
            <div style="margin-top: 12px; max-height: 150px; overflow-y: auto;">
                <table class="table" style="font-size: 12px;">
                    <thead>
                        <tr>
                            <th>DBC文件名</th>
                            <th>消息数</th>
                            <th>信号数</th>
                            <th>加载时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dbcList.map(([name, info]) => `
                            <tr>
                                <td><i class="fas fa-database" style="color: var(--primary); margin-right: 6px;"></i>${name}</td>
                                <td>${info.message_count || 0}</td>
                                <td>${info.signal_count || 0}</td>
                                <td style="font-size: 11px;">${info.parsed_at ? new Date(info.parsed_at).toLocaleString() : '-'}</td>
                                <td>
                                    <button class="btn btn-danger" style="padding: 2px 6px; font-size: 10px;" onclick="app.removeDBC('${name}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    renderTestCaseSelection(testcases, app) {
        if (testcases.length === 0) {
            return `
                <div class="empty-state" style="padding: 20px;">
                    <div style="font-size: 12px;">暂无测试用例，请先在"测试用例"页面生成或导入测试用例</div>
                    <button class="btn btn-secondary" style="margin-top: 10px;" onclick="app.switchTab('testcase')">
                        <i class="fas fa-arrow-right"></i> 前往测试用例页面
                    </button>
                </div>
            `;
        }
        
        // 只显示前10个用例，避免页面过长
        const displayTestcases = testcases.slice(0, 10);
        const hasMore = testcases.length > 10;
        
        return `
            <div style="max-height: 200px; overflow-y: auto;">
                ${displayTestcases.map((tc, index) => `
                    <div style="display: flex; align-items: center; padding: 8px; border-bottom: 1px solid var(--border);">
                        <input type="checkbox" class="testcase-checkbox" data-id="${tc.id || index}" checked 
                               style="margin-right: 10px; width: 16px; height: 16px;">
                        <div style="flex: 1;">
                            <div style="font-weight: 500; font-size: 12px;">${tc.name || tc.tc_name || `用例${index + 1}`}</div>
                            <div style="font-size: 11px; color: var(--text-secondary);">
                                ${tc.module || tc.test_phase || ''} ${tc.priority ? `| ${tc.priority}` : ''}
                            </div>
                        </div>
                        <span class="tag tag-${tc.priority === 'High' || tc.priority === 'P0' ? 'danger' : tc.priority === 'Medium' || tc.priority === 'P1' ? 'warning' : 'info'}" style="font-size: 10px;">
                            ${tc.priority || 'P2'}
                        </span>
                    </div>
                `).join('')}
                ${hasMore ? `<div style="text-align: center; padding: 8px; color: var(--text-secondary); font-size: 11px;">还有 ${testcases.length - 10} 个用例...</div>` : ''}
            </div>
            <div style="margin-top: 8px; font-size: 11px; color: var(--text-secondary);">
                已选择 <span id="selectedTestCaseCount">${displayTestcases.length}</span> 个测试用例
            </div>
        `;
    },

    renderAnalysisResults(logAnalysis) {
        if (!logAnalysis || logAnalysis.length === 0) {
            return '<div class="empty-state" style="padding: 30px;"><div style="font-size: 13px;">暂无分析结果，请导入日志文件并点击"分析日志"</div></div>';
        }
        
        // 显示最新的分析结果
        const latest = logAnalysis[logAnalysis.length - 1];
        
        return `
            <div style="margin-bottom: 16px;">
                <div class="dashboard-grid" style="grid-template-columns: repeat(4, 1fr);">
                    <div class="dashboard-card">
                        <div class="dashboard-stat">${latest.signal_extraction?.signal_count || 0}</div>
                        <div class="dashboard-label">提取信号</div>
                    </div>
                    <div class="dashboard-card">
                        <div class="dashboard-stat" style="color: var(--secondary);">${latest.testcase_match?.passed || 0}</div>
                        <div class="dashboard-label">通过用例</div>
                    </div>
                    <div class="dashboard-card">
                        <div class="dashboard-stat" style="color: var(--danger);">${latest.testcase_match?.failed || 0}</div>
                        <div class="dashboard-label">失败用例</div>
                    </div>
                    <div class="dashboard-card">
                        <div class="dashboard-stat">${latest.testcase_match?.pass_rate || 0}%</div>
                        <div class="dashboard-label">通过率</div>
                    </div>
                </div>
            </div>
            
            <!-- 信号统计表 -->
            ${this.renderSignalStats(latest.signal_extraction?.signal_stats || {})}
            
            <!-- 测试用例匹配结果 -->
            ${this.renderTestCaseMatchResults(latest.testcase_match?.results || [])}
            
            <!-- 分析报告预览 -->
            <div style="margin-top: 16px;">
                <div style="font-weight: 600; margin-bottom: 8px;"><i class="fas fa-file-alt" style="margin-right: 6px;"></i>分析报告</div>
                <div style="background: #1E293B; color: #E2E8F0; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 11px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">
                    ${latest.report || '暂无报告'}
                </div>
            </div>
        `;
    },

    renderSignalStats(signalStats) {
        const signals = Object.entries(signalStats);
        if (signals.length === 0) {
            return '';
        }
        
        return `
            <div style="margin-bottom: 16px;">
                <div style="font-weight: 600; margin-bottom: 8px;"><i class="fas fa-signal" style="margin-right: 6px;"></i>信号统计</div>
                <div class="table-container" style="max-height: 200px;">
                    <table class="table" style="font-size: 11px;">
                        <thead>
                            <tr>
                                <th>信号名</th>
                                <th>采样数</th>
                                <th>最小值</th>
                                <th>最大值</th>
                                <th>平均值</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${signals.slice(0, 20).map(([name, stats]) => `
                                <tr>
                                    <td>${name}</td>
                                    <td>${stats.count || 0}</td>
                                    <td>${stats.min?.toFixed(2) || '-'}</td>
                                    <td>${stats.max?.toFixed(2) || '-'}</td>
                                    <td>${stats.avg?.toFixed(2) || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    renderTestCaseMatchResults(results) {
        if (!results || results.length === 0) {
            return '';
        }
        
        return `
            <div style="margin-bottom: 16px;">
                <div style="font-weight: 600; margin-bottom: 8px;"><i class="fas fa-check-circle" style="margin-right: 6px;"></i>测试用例匹配结果</div>
                <div class="table-container" style="max-height: 200px;">
                    <table class="table" style="font-size: 11px;">
                        <thead>
                            <tr>
                                <th>用例ID</th>
                                <th>用例名称</th>
                                <th>状态</th>
                                <th>匹配信号</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${results.map(r => `
                                <tr>
                                    <td>${r.testcase_id}</td>
                                    <td>${r.testcase_name}</td>
                                    <td>
                                        <span class="tag tag-${r.status === 'passed' ? 'success' : r.status === 'failed' ? 'danger' : 'warning'}">
                                            ${r.status === 'passed' ? '✓ 通过' : r.status === 'failed' ? '✗ 失败' : '⚠ ' + r.status}
                                        </span>
                                    </td>
                                    <td>${r.signal_results?.filter(s => s.matched).length || 0}/${r.signal_results?.length || 0}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = LogPage;
}
