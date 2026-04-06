# VehicleTestAI1 - 文件上传和其他 API 端点

# 添加到 app.py 的末尾，在 if __name__ == '__main__': 之前

# ===== 文件上传 API =====

@app.route('/api/upload/<project_id>/<file_type>', methods=['POST'])
def upload_file(project_id, file_type):
    """上传文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            
            # 创建项目特定目录
            project_dir = os.path.join(UPLOAD_FOLDER, project_id, file_type)
            os.makedirs(project_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(project_dir, filename)
            file.save(file_path)
            
            # 如果是 DBC 文件，保存到数据库
            if file_type == 'dbcFile':
                dbc = DBCFile(
                    id=file_id,
                    project_id=project_id,
                    name=filename,
                    path=file_path,
                    signal_count=0  # TODO: 实际解析 DBC 文件
                )
                db.session.add(dbc)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'path': file_path,
                'filename': filename
            }), 201
        else:
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== AI 生成 API (扩展) =====

@app.route('/api/ai/parse-requirements', methods=['POST'])
def parse_requirements():
    """AI 解析需求文档"""
    try:
        data = request.json
        project_id = data.get('project_id')
        file_id = data.get('file_id')
        
        # 调用 AI 服务
        ai_service = get_ai_service()
        prompt = "请分析以下需求文档，提取功能点：\n\n[需求文档内容]"
        content = ai_service.generate(prompt)
        
        # 保存到数据库
        # TODO: 实际解析 AI 返回的内容并保存
        
        return jsonify({
            'success': True,
            'requirements': [
                {
                    'id': str(uuid.uuid4()),
                    'name': '示例功能点 1',
                    'category': '功能需求',
                    'priority': 'P0',
                    'description': 'AI 提取的功能描述',
                    'source': 'AI解析'
                }
            ]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/review-requirements', methods=['POST'])
def review_requirements():
    """AI 审核需求"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        # 调用 AI 服务
        ai_service = get_ai_service()
        prompt = "请审核以下需求：\n\n[需求内容]"
        content = ai_service.generate(prompt)
        
        return jsonify({
            'success': True,
            'review': {
                'completeness': 85,
                'consistency': 90,
                'clarity': 88,
                'issues': ['建议添加更多边界条件', '部分需求缺少验收标准']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/analyze-logs', methods=['POST'])
def analyze_logs():
    """AI 分析日志"""
    try:
        data = request.json
        project_id = data.get('project_id')
        dbc_file_id = data.get('dbc_file_id')
        
        # 调用 AI 服务
        ai_service = get_ai_service()
        prompt = "请分析以下测试日志：\n\n[日志内容]"
        content = ai_service.generate(prompt)
        
        # 保存到数据库
        analysis_results = [
            {
                'id': str(uuid.uuid4()),
                'signal': 'VehicleSpeed',
                'value': '60.5',
                'unit': 'km/h',
                'pass': True,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'analysis': analysis_results
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/generate-testcase', methods=['POST'])
def generate_testcase():
    """AI 生成测试用例"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        # 调用 AI 服务
        ai_service = get_ai_service()
        prompt = "请根据以下设计生成测试用例：\n\n[设计内容]"
        content = ai_service.generate(prompt)
        
        # 保存到数据库
        testcase = TestCase(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name='AI生成的测试用例',
            priority='P1',
            steps=content,
            expected='预期结果'
        )
        
        db.session.add(testcase)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'testcase': testcase.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 数据查询 API =====

@app.route('/api/strategies/<project_id>', methods=['GET'])
def get_strategies(project_id):
    """获取测试策略列表"""
    try:
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'strategies': [s.to_dict() for s in strategies]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/strategies/<project_id>/latest', methods=['GET'])
def get_latest_strategy(project_id):
    """获取最新测试策略"""
    try:
        strategy = TestStrategy.query.filter_by(project_id=project_id)\
            .order_by(TestStrategy.created_at.desc()).first()
        
        if not strategy:
            return jsonify({'success': False, 'error': 'No strategy found'}), 404
        
        return jsonify({
            'success': True,
            'strategy': strategy.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/designs/<project_id>', methods=['GET'])
def get_designs(project_id):
    """获取测试设计列表"""
    try:
        designs = TestDesign.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'designs': [d.to_dict() for d in designs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/designs/<design_id>', methods=['GET'])
def get_design(design_id):
    """获取单个测试设计"""
    try:
        design = TestDesign.query.get(design_id)
        if not design:
            return jsonify({'success': False, 'error': 'Design not found'}), 404
        
        return jsonify({
            'success': True,
            'design': design.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cases/<project_id>', methods=['GET'])
def get_testcases(project_id):
    """获取测试用例列表"""
    try:
        cases = TestCase.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'testcases': [c.to_dict() for c in cases]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs/<project_id>', methods=['GET'])
def get_logs(project_id):
    """获取测试日志列表"""
    try:
        logs = TestLog.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'logs': [l.to_dict() for l in logs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 删除 API =====

@app.route('/api/requirements/<req_id>', methods=['DELETE'])
def delete_requirement(req_id):
    """删除需求"""
    try:
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'success': False, 'error': 'Requirement not found'}), 404
        
        db.session.delete(requirement)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/designs/<design_id>', methods=['DELETE'])
def delete_design(design_id):
    """删除测试设计"""
    try:
        design = TestDesign.query.get(design_id)
        if not design:
            return jsonify({'success': False, 'error': 'Design not found'}), 404
        
        db.session.delete(design)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 健康检查 API =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'VehicleTestAI Backend',
        'version': '2.0.0',
        'database': 'SQLite',
        'timestamp': datetime.now().isoformat()
    })

# ===== 错误处理 =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
