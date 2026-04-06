# Add this to backend/app.py before "# ==================== AI服务实现 ===================="


@app.route("/api/ai/optimize-testcases", methods=["POST"])
def optimize_testcases():
    """根据审核意见优化测试用例"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")
    testcases = data.get("testcases", [])
    review_comment = data.get("review_comment", "")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    try:
        ai_service = get_ai_service_from_config()

        prompt = f"""你是一个专业的测试工程师，请根据审核意见优化以下测试用例。

当前测试用例:
{json.dumps(testcases, ensure_ascii=False, indent=2)}

审核意见:
{review_comment}

请根据审核意见优化测试用例，返回优化后的测试用例JSON数组。每个用例应包含:
- id: 用例ID
- name: 用例名称
- priority: 优先级(P0/P1/P2)
- precondition: 前置条件
- input: 测试输入
- expected: 预期输出
- auto: 是否可自动化(true/false)
- steps: 测试步骤

只返回JSON数组，不要其他说明文字。"""

        response = ai_service.generate(prompt)
        duration = (datetime.now() - start_time).total_seconds()

        # 尝试解析JSON
        try:
            if "[" in response and "]" in response:
                start = response.index("[")
                end = response.rindex("]") + 1
                json_str = response[start:end]
                optimized_testcases = json.loads(json_str)
            else:
                optimized_testcases = testcases
        except:
            optimized_testcases = testcases

        record_ai_usage(
            skill_type="用例生成",
            content_summary=f"优化测试用例: {review_comment[:50]}",
            status="成功",
            duration=duration,
            tokens_used=len(response),
            project_id=project_id,
        )

        return jsonify({"success": True, "testcases": optimized_testcases})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "用例生成", "优化测试用例失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500
