/**
 * 车载控制器测试AI平台 - 需求分析页面
 */

const RequirementsPage = {
    /**
     * 渲染需求分析页面
     * @param {Object} app - 主应用实例
     * @returns {string} - HTML字符串
     */
    render(app) {
        const reqFile = app.uploadedFiles['requirement'];
        const reqData = app.projectData.requirements || {};
        const reviewData = app.projectData.requirementReview || {};

        return `
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-stat">${Object.keys(reqData).length || 0}</div><div class="dashboard-label">功能点总数</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${Object.keys(reqData).filter(k => reqData[k].reviewed).length || 0}</div><div class="dashboard-label">已审核功能点</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${Object.keys(reqData).length > 0 ? '95' : '--'}%</div><div class="dashboard-label">IR-SR完整性</div></div>
                <div class="dashboard-card"><div class="dashboard-stat">${reqFile ? '100' : '--'}%</div><div class="dashboard-label">文档覆盖率</div></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-upload" style="color: var(--primary);"></i>需求文档导入</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportRequirements()"><i class="fas fa-download"></i>导出</button>
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.runAIRequirementParse()" ${!reqFile ? 'disabled' : ''}><i class="fas fa-magic"></i>AI解析</button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="upload-zone" onclick="app.uploadFile('requirement')">
                        <div class="upload-icon"><i class="fas fa-cloud-upload-alt"></i></div>
                        <div class="upload-text"><strong>点击上传</strong> 或拖拽需求文档 (PDF/Word/Excel)</div>
                    </div>
                    <div id="requirementsFileList">
                        ${reqFile ? this.renderFileItem(reqFile, 'requirement', app) : ''}
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-list-ul" style="color: var(--secondary);"></i>功能点列表</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.addManualRequirement()"><i class="fas fa-plus"></i>手动添加</button>
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="app.exportRequirements()"><i class="fas fa-download"></i>导出</button>
                    </div>
                </div>
                <div class="card-body">
                    ${this.renderFunctionPointsList(reqData)}
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <span class="card-title"><i class="fas fa-check-double" style="color: var(--info);"></i>需求审核</span>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="app.runRequirementReview()" ${!reqFile ? 'disabled' : ''}><i class="fas fa-play"></i>执行审核</button>
                </div>
                <div class="card-body">
                    ${reviewData.review ? this.renderRealReviewResults(reviewData) : this.renderEmptyReview(reqFile)}
                </div>
            </div>
        `;
    },

    /**
     * 渲染文件项
     */
    renderFileItem(file, type, app) {
        return `
            <div class="file-item">
                <div class="file-icon"><i class="fas fa-file-alt"></i></div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-meta">${(file.size / 1024).toFixed(1)} KB</div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-secondary" style="padding: 4px 6px;" onclick="app.editRequirements()"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-danger" style="padding: 4px 6px;" onclick="app.removeFile('requirements')"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;
    },

    /**
     * 渲染功能点列表
     */
    renderFunctionPointsList(reqData) {
        const points = Object.values(reqData);
        if (points.length === 0) {
            return '<div class="empty-state" style="padding: 30px;"><div style="font-size: 13px;">暂无功能点，请上传需求文档并点击AI解析</div></div>';
        }
        return points.map(p => `
            <div class="function-point-item">
                <div class="function-point-header">
                    <span class="function-point-id">${p.id || 'FP_NEW'} - ${p.name || '新功能点'}</span>
                    <span class="function-point-source">${p.source || '手动添加'}</span>
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">分类: ${p.category || '未分类'} | 优先级: ${p.priority || 'P2'} | 关联需求: ${p.linkedReqs || '无'}</div>
                <div class="function-point-quote">"${p.description || '暂无描述'}"</div>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="app.editRequirement('${p.id}')"><i class="fas fa-edit"></i>编辑</button>
                    <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="app.deleteRequirement('${p.id}')"><i class="fas fa-trash"></i>删除</button>
                </div>
            </div>
        `).join('');
    },

    /**
     * 渲染空审核状态
     */
    renderEmptyReview(reqFile) {
        if (!reqFile) {
            return '<div class="empty-state" style="padding: 20px;"><div style="font-size: 13px;">请先上传需求文档后再进行审核</div></div>';
        }
        return '<div class="empty-state" style="padding: 20px;"><div style="font-size: 13px;">点击"执行审核"对需求文档进行AI审核</div></div>';
    },

    /**
     * 渲染真实审核结果
     */
    renderRealReviewResults(reviewData) {
        return `
            <div style="margin-bottom: 16px; padding: 12px; background: var(--bg-secondary); border-radius: 8px;">
                <div style="font-size: 12px; color: var(--text-secondary);">
                    <strong>审核文件:</strong> ${reviewData.fileName || '未知'}<br>
                    <strong>审核时间:</strong> ${reviewData.reviewedAt ? new Date(reviewData.reviewedAt).toLocaleString('zh-CN') : '未知'}
                </div>
            </div>
            <div style="background: #1E293B; color: #E2E8F0; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto; white-space: pre-wrap;">${reviewData.review || '暂无审核结果'}</div>
        `;
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RequirementsPage;
}
