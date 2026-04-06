# AI 统计和监控 API 端点
# 添加到 app.py 中

from services.enhanced_ai_service import (
    get_enhanced_ai_service, 
    get_ai_stats, 
    clear_ai_cache, 
    reset_ai_stats,
    token_counter
)

# ===== AI 统计 API =====

@app.route('/api/ai/stats', methods=['GET'])
def get_ai_usage_stats():
    """获取 AI 使用统计"""
    try:
        stats = get_ai_stats()
        
        # 添加更多统计信息
        stats['uptime'] = {
            'start_time': app.config.get('START_TIME', datetime.now().isoformat()),
            'current_time': datetime.now().isoformat()
        }
        
        stats['services'] = {
            'backend': 'running',
            'database': 'connected',
            'ai_service': 'active' if get_ai_service() else 'inactive'
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/stats/reset', methods=['POST'])
def reset_ai_usage_stats():
    """重置 AI 统计"""
    try:
        reset_ai_stats()
        
        # 重置数据库中的统计
        ai_stats = load_ai_stats()
        ai_stats['total_calls'] = 0
        ai_stats['total_hours_saved'] = 0.0
        ai_stats['total_tokens_used'] = 0
        ai_stats['history'] = []
        save_ai_stats(ai_stats)
        
        return jsonify({
            'success': True,
            'message': 'AI 统计已重置'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/cache/clear', methods=['POST'])
def clear_ai_response_cache():
    """清空 AI 缓存"""
    try:
        clear_ai_cache()
        
        return jsonify({
            'success': True,
            'message': 'AI 缓存已清空'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/config', methods=['GET'])
def get_ai_configuration():
    """获取 AI 配置"""
    try:
        config = load_ai_config()
        
        # 掩码 API Key
        safe_config = config.copy()
        if safe_config.get('api_key'):
            key = safe_config['api_key']
            safe_config['api_key_masked'] = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
        
        return jsonify({
            'success': True,
            'config': safe_config
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/config', methods=['POST'])
def update_ai_configuration():
    """更新 AI 配置"""
    try:
        data = request.json
        
        # 验证必要字段
        if 'provider' not in data:
            return jsonify({'success': False, 'error': 'Missing provider'}), 400
        
        # 加载当前配置
        config = load_ai_config()
        
        # 更新配置
        config['provider'] = data.get('provider', config.get('provider'))
        config['model'] = data.get('model', config.get('model'))
        
        if 'api_key' in data and data['api_key']:
            config['api_key'] = data['api_key']
        
        if 'base_url' in data:
            config['base_url'] = data['base_url']
        
        if 'max_tokens' in data:
            config['max_tokens'] = int(data['max_tokens'])
        
        if 'temperature' in data:
            config['temperature'] = float(data['temperature'])
        
        # 保存配置
        save_ai_config(config)
        
        # 重新初始化 AI 服务
        # 注意：这可能需要重启服务才能完全生效
        
        return jsonify({
            'success': True,
            'message': 'AI 配置已更新',
            'config': config
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== AI 生成 API（增强版） =====

@app.route('/api/ai/generate-strategy', methods=['POST'])
def generate_test_strategy_enhanced():
    """生成测试策略（增强版）"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Missing project_id'}), 400
        
        # 获取项目需求
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        if not requirements:
            return jsonify({'success': False, 'error': 'No requirements found'}), 404
        
        req_text = '\n'.join([f"{r.id}: {r.name}\n{r.description}" for r in requirements])
        
        # 构建提示词
        prompt = f"""请根据以下需求生成完整的测试策略文档：

# 需求列表
{req_text}

# 要求
1. 定义测试范围和目标
2. 选择测试方法和工具
3. 制定测试计划和时间表
4. 识别风险和应对措施
5. 配置测试环境

请用 Markdown 格式输出完整的测试策略文档。"""

        # 调用增强版 AI 服务
        ai_service = get_enhanced_ai_service(
            service_type=load_ai_config().get('provider', 'mock'),
            api_key=load_ai_config().get('api_key')
        )
        
        start_time = time.time()
        content = ai_service.generate_with_cache(prompt, max_tokens=3000)
        elapsed_time = time.time() - start_time
        
        # 保存到数据库
        strategy_id = str(uuid.uuid4())
        strategy = TestStrategy(
            id=strategy_id,
            project_id=project_id,
            name=f"测试策略_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content
        )
        
        db.session.add(strategy)
        
        # 记录 AI 历史
        ai_history = AIHistory(
            id=str(uuid.uuid4()),
            project_id=project_id,
            type='strategy_generation',
            input=prompt[:500],  # 只保存前500字符
            output=content[:500],  # 只保存前500字符
            tokens_used=len(content)  # 估算
        )
        db.session.add(ai_history)
        
        db.session.commit()
        
        # 记录统计
        record_ai_usage(
            skill_type='策略生成',
            content_summary=f'为项目 {project_id} 生成测试策略',
            status='成功',
            duration=elapsed_time,
            tokens_used=len(content),
            project_id=project_id
        )
        
        return jsonify({
            'success': True,
            'strategy': strategy.to_dict(),
            'elapsed_time': round(elapsed_time, 2),
            'tokens_used': len(content)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/generate-design', methods=['POST'])
def generate_test_design_enhanced():
    """生成测试设计（增强版）"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Missing project_id'}), 400
        
        # 获取项目的测试策略
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        if not strategies:
            return jsonify({'success': False, 'error': 'No test strategies found, please generate strategy first'}), 404
        
        strategy_text = '\n\n'.join([s.content for s in strategies])
        
        # 构建提示词
        prompt = f"""请根据以下测试策略生成详细的测试设计文档：

# 测试策略
{strategy_text}

# 要求
1. 为每个测试场景设计具体的测试用例
2. 定义测试步骤和预期结果
3. 准备测试数据和测试环境
4. 设计测试脚本框架

请用 Markdown 格式输出完整的测试设计文档。"""

        # 调用增强版 AI 服务
        ai_service = get_enhanced_ai_service(
            service_type=load_ai_config().get('provider', 'mock'),
            api_key=load_ai_config().get('api_key')
        )
        
        start_time = time.time()
        content = ai_service.generate_with_cache(prompt, max_tokens=4000)
        elapsed_time = time.time() - start_time
        
        # 保存到数据库
        design_id = str(uuid.uuid4())
        design = TestDesign(
            id=design_id,
            project_id=project_id,
            name=f"测试设计_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content
        )
        
        db.session.add(design)
        
        # 记录 AI 历史
        ai_history = AIHistory(
            id=str(uuid.uuid4()),
            project_id=project_id,
            type='design_generation',
            input=prompt[:500],
            output=content[:500],
            tokens_used=len(content)
        )
        db.session.add(ai_history)
        
        db.session.commit()
        
        # 记录统计
        record_ai_usage(
            skill_type='设计生成',
            content_summary=f'为项目 {project_id} 生成测试设计',
            status='成功',
            duration=elapsed_time,
            tokens_used=len(content),
            project_id=project_id
        )
        
        return jsonify({
            'success': True,
            'design': design.to_dict(),
            'elapsed_time': round(elapsed_time, 2),
            'tokens_used': len(content)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
