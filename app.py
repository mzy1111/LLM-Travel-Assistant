"""Flask Web应用入口"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from src.agent.travel_agent import TravelAgent
from src.config import config
from src.models.user import user_manager
from functools import wraps
import uuid

app = Flask(__name__)
app.secret_key = 'travel-assistant-secret-key-change-in-production'

# 存储每个会话的Agent实例
agents = {}


def login_required(f):
    """登录装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_or_create_agent(user_id: str = None, session_id: str = None):
    """
    获取或创建Agent实例
    
    Args:
        user_id: 用户ID（如果已登录）
        session_id: 会话ID（如果未登录）
    """
    # 优先使用user_id，如果没有则使用session_id
    agent_key = user_id or session_id
    if not agent_key:
        return None, "缺少用户ID或会话ID"
    
    if agent_key not in agents:
        try:
            print(f'\n--- 创建新的Agent实例 ---', flush=True)
            print(f'用户ID: {user_id[:8] if user_id else "未登录"}...', flush=True)
            print(f'会话ID: {session_id[:8] if session_id else "N/A"}...', flush=True)
            # 使用user_id作为session_id传递给Agent（用于偏好管理）
            agents[agent_key] = TravelAgent(verbose=True, session_id=user_id or session_id)
            print('Agent实例创建成功\n', flush=True)
        except Exception as e:
            import traceback
            print(f'\n--- Agent创建失败 ---', flush=True)
            print(f'错误: {e}', flush=True)
            traceback.print_exc()
            return None, str(e)
    else:
        print(f'使用现有Agent实例，用户ID: {user_id[:8] if user_id else "未登录"}...', flush=True)
    return agents[agent_key], None


@app.route('/')
def index():
    """主页"""
    # 如果已登录，跳转到聊天页面；否则跳转到登录页面
    if 'user_id' in session:
        return redirect(url_for('chat_page'))
    return redirect(url_for('login_page'))


@app.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')


@app.route('/chat')
def chat_page():
    """聊天页面"""
    # 如果未登录，跳转到登录页面
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # 为每个新会话创建唯一ID（用于未登录用户）
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')


@app.route('/plan')
def plan_page():
    """行程规划页面"""
    # 如果未登录，跳转到登录页面
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    query = request.args.get('q', '')
    itinerary_id = request.args.get('itinerary', '')
    
    # 为每个新会话创建唯一ID（用于未登录用户）
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # 如果有查询参数，跳转到聊天页面
    if query or itinerary_id:
        return render_template('index.html', initial_query=query)
    
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        # 检查登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        data = request.json
        user_input = data.get('message', '').strip()
        travel_info = data.get('travelInfo', {})
        
        # 获取用户ID（已登录用户）
        user_id = session.get('user_id')
        session_id = session.get('session_id')  # 保留session_id作为备用
        
        # 添加调试日志
        print('\n--- 收到聊天请求 ---')
        print(f'用户ID: {user_id[:8] if user_id else "未登录"}...')
        print(f'会话ID: {session_id[:8] if session_id else "N/A"}...')
        print(f'用户输入: {user_input}')
        print(f'收到的旅行信息: {travel_info}')
        
        # 保存旅行信息到session
        if travel_info:
            session['travel_info'] = travel_info
            print(f'已保存旅行信息到session: {session.get("travel_info")}')
        
        if not user_input:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 获取或创建Agent（使用user_id或session_id）
        agent, error = get_or_create_agent(user_id=user_id, session_id=session_id)
        if error:
            print(f'Agent初始化失败: {error}')
            return jsonify({'error': f'Agent初始化失败: {error}'}), 500
        
        # 如果有旅行信息，传递给Agent
        if travel_info:
            print(f'传递旅行信息给Agent: {travel_info}')
            agent.set_travel_info(travel_info)
        elif 'travel_info' in session:
            # 如果session中已有旅行信息，也传递给Agent
            saved_travel_info = session['travel_info']
            print(f'从session获取旅行信息: {saved_travel_info}')
            agent.set_travel_info(saved_travel_info)
        
        # 添加调试日志，检查Agent是否正确设置了旅行信息
        agent_travel_info = agent.get_travel_info()
        print(f'Agent中存储的旅行信息: {agent_travel_info}')
        
        # 获取回复
        response = agent.chat(user_input)
        
        return jsonify({
            'response': response,
            'user_id': user_id,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500


@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not email or not password:
            return jsonify({'error': '请填写所有必填项'}), 400
        
        if len(password) < 6:
            return jsonify({'error': '密码长度至少6位'}), 400
        
        user, error = user_manager.register(username, email, password)
        if error:
            return jsonify({'error': error}), 400
        
        # 注册成功后自动登录
        session['user_id'] = user.user_id
        session['username'] = user.username
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        return jsonify({'error': f'注册失败: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': '请填写用户名和密码'}), 400
        
        user, error = user_manager.login(username, password)
        if error:
            return jsonify({'error': error}), 401
        
        # 登录成功，保存到session
        session['user_id'] = user.user_id
        session['username'] = user.username
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    user_id = session.get('user_id')
    if user_id and user_id in agents:
        # 清理Agent实例
        del agents[user_id]
    
    session.clear()
    return jsonify({'success': True, 'message': '已登出'})


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取当前用户信息"""
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = user_manager.get_user(session['user_id'])
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    """重置对话"""
    try:
        # 获取用户ID或会话ID
        user_id = session.get('user_id')
        session_id = session.get('session_id')
        agent_key = user_id or session_id
        
        if agent_key and agent_key in agents:
            agents[agent_key].reset_memory()
        
        # 如果不是登录用户，创建新的会话ID
        if not user_id:
            session['session_id'] = str(uuid.uuid4())
        
        return jsonify({'message': '对话已重置'})
    except Exception as e:
        return jsonify({'error': f'重置失败: {str(e)}'}), 500


@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    """根据旅行信息生成旅行规划"""
    try:
        # 检查登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        data = request.json
        travel_info = data.get('travelInfo', {})
        
        # 验证必填字段
        if not travel_info.get('destination'):
            return jsonify({'error': '目的地不能为空'}), 400
        
        if not travel_info.get('departureDate') or not travel_info.get('returnDate'):
            return jsonify({'error': '出发日期和返回日期不能为空'}), 400
        
        # 保存旅行信息到session
        session['travel_info'] = travel_info
        
        # 获取用户ID或会话ID
        user_id = session.get('user_id')
        session_id = session.get('session_id')
        if not user_id and not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # 获取或创建Agent（使用user_id或session_id）
        agent, error = get_or_create_agent(user_id=user_id, session_id=session_id)
        if error:
            return jsonify({'error': f'Agent初始化失败: {error}'}), 500
        
        # 设置旅行信息
        agent.set_travel_info(travel_info)
        
        # 计算旅行天数
        from datetime import datetime
        try:
            departure = datetime.strptime(travel_info['departureDate'], '%Y-%m-%d')
            return_date = datetime.strptime(travel_info['returnDate'], '%Y-%m-%d')
            days = (return_date - departure).days + 1
        except:
            days = 7  # 默认7天
        
        # 构建规划请求
        destination = travel_info.get('destination', '')
        budget = travel_info.get('budget', '')
        preferences_parts = []
        
        if travel_info.get('travelStyle'):
            preferences_parts.append(f"旅行风格：{travel_info['travelStyle']}")
        if travel_info.get('interests'):
            preferences_parts.append(f"兴趣偏好：{travel_info['interests']}")
        if travel_info.get('hotelPreference'):
            preferences_parts.append(f"住宿偏好：{travel_info['hotelPreference']}")
        if travel_info.get('transportMode'):
            preferences_parts.append(f"出行方式：{travel_info['transportMode']}")
        
        preferences = '，'.join(preferences_parts) if preferences_parts else None
        
        # 构建用户请求，提示Agent查询所有相关信息
        user_request = f"请为我规划一个{days}天的{destination}旅行行程"
        if budget:
            user_request += f"，预算{budget}元"
        if preferences:
            user_request += f"，偏好：{preferences}"
        user_request += "。\n\n"
        user_request += "重要提示：\n"
        user_request += "1. 请先使用 get_weather_info 工具查询出发日期和目的地的天气信息\n"
        if travel_info.get('hotelPreference'):
            user_request += "2. 请使用 get_hotel_prices 工具查询酒店价格信息，以便提供准确的预算估算\n"
        if travel_info.get('departureCity') and travel_info.get('transportMode'):
            user_request += f"3. 请使用 get_transport_route 工具查询从{travel_info.get('departureCity')}到{destination}的{travel_info.get('transportMode')}路线和费用\n"
        if travel_info.get('interests'):
            user_request += f"4. 请使用 get_attraction_ticket_prices 工具查询{destination}的景点门票价格（根据兴趣偏好：{travel_info.get('interests')}）\n"
        user_request += "5. 然后使用 plan_travel_itinerary 工具生成详细行程，该工具会自动集成所有查询到的信息\n"
        user_request += "6. 根据天气情况调整活动建议（如雨天推荐室内活动，晴天推荐户外活动）\n"
        user_request += "7. 根据酒店价格、交通费用、景点门票信息调整预算分配，提供更准确的费用估算\n"
        user_request += "\n请提供详细的每日行程安排，包括景点、餐饮、住宿、交通和预算分配。"
        
        # 调用Agent生成规划
        print(f'\n--- 开始生成规划 ---')
        print(f'请求内容: {user_request[:100]}...')
        try:
            plan_response = agent.chat(user_request)
            print(f'规划生成成功，响应长度: {len(plan_response) if plan_response else 0}')
        except Exception as agent_error:
            import traceback
            print(f'Agent执行异常: {agent_error}')
            traceback.print_exc()
            raise
        
        # 检查响应是否包含错误信息
        if plan_response and ("错误" in plan_response or "❌" in plan_response):
            # 如果响应包含错误，返回错误信息但标记为失败
            return jsonify({
                'success': False,
                'error': plan_response,
                'travelInfo': travel_info,
                'days': days,
                'plan': plan_response  # 仍然返回规划内容，让前端可以显示错误信息
            }), 200  # 返回200，让前端可以处理错误显示
        
        return jsonify({
            'success': True,
            'plan': plan_response,
            'travelInfo': travel_info,
            'days': days
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        
        # 提供更友好的错误提示
        if "Connection" in error_msg or "connection" in error_msg.lower():
            friendly_error = "无法连接到AI服务。请检查：\n1. API密钥是否正确配置\n2. 网络连接是否正常\n3. API服务是否可用"
        elif "API" in error_msg or "api" in error_msg.lower():
            friendly_error = "API调用失败。请检查：\n1. API密钥是否有效\n2. API余额是否充足\n3. API服务地址是否正确"
        else:
            friendly_error = f"生成规划时出错: {error_msg}"
        
        return jsonify({
            'success': False,
            'error': friendly_error,
            'travelInfo': travel_info,
            'days': days
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """获取系统状态"""
    try:
        # 检查API密钥
        has_api_key = bool(config.openai_api_key)
        
        return jsonify({
            'api_configured': has_api_key,
            'status': 'ready' if has_api_key else 'api_key_missing'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 检查API密钥
    if not config.openai_api_key:
        print("警告：未设置 OPENAI_API_KEY 环境变量")
        print("请在 .env 或 env 文件中设置您的 OpenAI API 密钥")
    
    # 启动Flask应用
    print("\n" + "=" * 60)
    print("智能旅行助手 Web 界面")
    print("=" * 60)
    print("访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

