/**
 * 车载控制器测试AI平台 - 待使用页面模板
 */

const PendingPage = {
    render(num) {
        return `
            <div class="empty-state" style="padding: 80px;">
                <div class="empty-state-icon" style="font-size: 64px; color: var(--primary);"><i class="fas fa-puzzle-piece"></i></div>
                <div class="empty-state-title" style="font-size: 20px;">待使用${num}</div>
                <div style="font-size: 14px; color: var(--text-secondary); margin-top: 12px; max-width: 400px; margin-left: auto; margin-right: auto;">
                    此页面用于扩展自定义功能。可通过以下方式启用：
                </div>
                <div style="margin-top: 20px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
                    <div class="bench-card" style="margin-bottom: 12px; text-align: left;">
                        <div style="font-weight: 600; margin-bottom: 8px;"><i class="fas fa-file-code" style="color: var(--primary); margin-right: 8px;"></i>页面挂接说明</div>
                        <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.8;">
                            1. 在renderPage方法的methods对象中添加新的页面方法<br>
                            2. 实现renderXxxPage()方法返回页面HTML<br>
                            3. 在tabs数组中添加标签配置
                        </div>
                    </div>
                    <div class="bench-card" style="text-align: left;">
                        <div style="font-weight: 600; margin-bottom: 8px;"><i class="fas fa-plug" style="color: var(--secondary); margin-right: 8px;"></i>代码对接方式</div>
                        <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.8;">
                            页面通过switchTab('pageId')切换显示<br>
                            使用app.uploadFile(type)处理文件上传<br>
                            使用app.showModal(id)显示弹窗<br>
                            调用AI方法进行智能处理
                        </div>
                    </div>
                </div>
                <div style="margin-top: 24px;">
                    <button class="btn btn-primary" onclick="app.configurePendingPage(${num})"><i class="fas fa-cog"></i> 配置此页面</button>
                </div>
            </div>
        `;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PendingPage;
}
