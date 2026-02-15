"""
纯本地景点查询API
不依赖任何外部API，只使用本地CSV数据
"""
from flask import Flask, request, jsonify
import json
from src.agent.attraction_loader_simple import AttractionDataLoader
from src.agent.attraction_vector_store_simple import AttractionVectorStore

app = Flask(__name__)

# 全局实例
_attraction_loader = None
_attraction_vector_store = None

def get_attraction_components():
    """获取景点数据加载器和向量存储"""
    global _attraction_loader, _attraction_vector_store

    if _attraction_loader is None:
        _attraction_loader = AttractionDataLoader(data_dir="jingdian")

    if _attraction_vector_store is None:
        _attraction_vector_store = AttractionVectorStore(_attraction_loader)

    return _attraction_loader, _attraction_vector_store

# 初始化
print("初始化本地景点数据库...")
get_attraction_components()
print("初始化完成！")


@app.route('/api/local/search', methods=['POST'])
def search_attraction():
    """搜索景点"""
    try:
        data = request.json
        query = data.get('query', '')
        city = data.get('city', None)
        
        if not query:
            return jsonify({'error': '查询不能为空'}), 400
        
        _, vector_store = get_attraction_components()
        results = vector_store.search(query=query, city=city, k=3)
        
        # 格式化结果
        formatted_results = []
        for doc in results:
            formatted_results.append({
                'name': doc.metadata.get('name', ''),
                'city': doc.metadata.get('city', ''),
                'address': doc.metadata.get('address', ''),
                'content': doc.page_content
            })
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'total': len(formatted_results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/local/details', methods=['POST'])
def get_attraction_details():
    """获取景点详情"""
    try:
        data = request.json
        name = data.get('name', '')
        city = data.get('city', None)
        
        if not name:
            return jsonify({'error': '景点名称不能为空'}), 400
        
        loader, _ = get_attraction_components()
        attraction = loader.get_attraction_by_name(city, name)
        
        if not attraction:
            return jsonify({'error': '景点不存在'}), 404
        
        return jsonify({
            'success': True,
            'attraction': attraction
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/local/list', methods=['POST'])
def list_attractions():
    """列出景点"""
    try:
        data = request.json
        city = data.get('city', None)
        
        loader, _ = get_attraction_components()
        
        if city:
            attractions = loader.get_attractions(city)
        else:
            # 列出所有城市的景点
            attractions = []
            for city_name in loader.get_cities():
                city_attractions = loader.get_attractions(city_name)
                for attraction in city_attractions:
                    attraction['city'] = city_name
                    attractions.append(attraction)
        
        return jsonify({
            'success': True,
            'attractions': attractions,
            'total': len(attractions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/local/cities', methods=['GET'])
def list_cities():
    """列出所有城市"""
    try:
        loader, _ = get_attraction_components()
        cities = loader.get_cities()
        
        return jsonify({
            'success': True,
            'cities': cities
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/local/test', methods=['GET'])
def test_endpoint():
    """测试API"""
    try:
        loader, _ = get_attraction_components()
        cities = loader.get_cities()
        
        test_results = []
        for city in cities:
            attractions = loader.get_attractions(city)
            test_results.append({
                'city': city,
                'count': len(attractions)
            })
        
        return jsonify({
            'success': True,
            'message': '本地API运行正常',
            'test_results': test_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("启动本地景点API服务器...")
    print("访问 http://localhost:5001/api/local/test 测试连接")
    print("访问 http://localhost:5001/api/local/cities 获取城市列表")
    app.run(port=5001, debug=True)
