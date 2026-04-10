/**
 * 车载控制器测试AI平台 - 测试活动管理器
 * 基于test_system文档规范，管理测试活动流程
 */

const TEST_ACTIVITIES = {
    RA: { code: 'RA', name: '需求分析', dependencies: [] },
    TS: { code: 'TS', name: '测试策略', dependencies: ['RA'] },
    TD: { code: 'TD', name: '测试设计', dependencies: ['TS'] },
    TC: { code: 'TC', name: '测试用例', dependencies: ['TD'] },
    TScr: { code: 'TScr', name: '测试脚本', dependencies: ['TC'] },
    TE: { code: 'TE', name: '测试执行', dependencies: ['TScr'] },
    TL: { code: 'TL', name: '测试日志', dependencies: ['TE'] },
    TEval: { code: 'TEval', name: '测试评估', dependencies: ['TL'] },
    TR: { code: 'TR', name: '测试报告', dependencies: ['TEval'] }
};

const ACTIVITY_STATUS = {
    NOT_STARTED: 'not_started',
    IN_PROGRESS: 'in_progress',
    COMPLETED: 'completed',
    FAILED: 'failed'
};

class TestActivityManager {
    constructor(apiService) {
        this.apiService = apiService;
        this.activities = {};
        this.currentProject = null;
        this.resetActivities();
    }
    
    resetActivities() {
        for (const [code, activity] of Object.entries(TEST_ACTIVITIES)) {
            this.activities[code] = {
                ...activity,
                status: ACTIVITY_STATUS.NOT_STARTED,
                progress: 0,
                result: null
            };
        }
    }
    
    setProject(projectId) {
        this.currentProject = projectId;
        this.resetActivities();
    }
    
    checkDependencies(activityCode) {
        const activity = this.activities[activityCode];
        if (!activity) return false;
        for (const depCode of activity.dependencies) {
            if (this.activities[depCode]?.status !== ACTIVITY_STATUS.COMPLETED) {
                return false;
            }
        }
        return true;
    }
    
    getNextActivity() {
        const order = ['RA', 'TS', 'TD', 'TC', 'TScr', 'TE', 'TL', 'TEval', 'TR'];
        for (const code of order) {
            if (this.activities[code]?.status === ACTIVITY_STATUS.NOT_STARTED && 
                this.checkDependencies(code)) {
                return code;
            }
        }
        return null;
    }
    
    getProgressSummary() {
        let completed = 0;
        for (const activity of Object.values(this.activities)) {
            if (activity.status === ACTIVITY_STATUS.COMPLETED) completed++;
        }
        return {
            total: Object.keys(this.activities).length,
            completed,
            progress: Math.round((completed / Object.keys(this.activities).length) * 100)
        };
    }
}

if (typeof window !== 'undefined') {
    window.TestActivityManager = TestActivityManager;
    window.TEST_ACTIVITIES = TEST_ACTIVITIES;
    window.ACTIVITY_STATUS = ACTIVITY_STATUS;
}
