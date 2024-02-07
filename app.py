from flask import Flask, request, jsonify
from module import *

# 初始化Flask伺服器
app = Flask(__name__)

@app.route('/show_events')
def show_events():

    filter_dict = {}

    range_bgn_time = request.args.get('range_bgn_time')
    if range_bgn_time:
        # range_bgn_time = datetime.strptime(range_bgn_time, '%Y-%m-%dT%H:%M')
        range_bgn_time = datetime.strptime(range_bgn_time, '%Y-%m-%d')
        filter_dict['event_end_time'] = {'$gt': range_bgn_time}
    else:
        range_bgn_time = None

    range_end_time = request.args.get('range_end_time')
    if range_end_time:
        # range_end_time = datetime.strptime(range_end_time, '%Y-%m-%dT%H:%M')
        range_end_time = datetime.strptime(range_end_time, '%Y-%m-%d')
        filter_dict['event_bgn_time'] = {'$lt': range_end_time}
    else:
        range_end_time = None
    
    location = request.args.get('location')
    if location:
        filter_dict['event_location'] = {'$eq': location}
    else:
        location = None

    range_event = list(event_info_collection.find({'$and': [filter_dict]}))
    return jsonify(dumps(range_event))

# 利用API建立活動
@app.route('/create_events', methods = ['POST'])
def create_events():
    '''
    Request: 
    1. event_name (str)
    2. event_bgn_time (str, 'yyyy-mm-ddThh:mm:ss')
    3. event_end_time (str, 'yyyy-mm-ddThh:mm:ss')
    4. event_location (str)
    5. event_host (str)
    '''
    data = request.get_json()
    
    data['event_bgn_time'] = datetime.fromisoformat(data['event_bgn_time']) 
    data['event_end_time'] = datetime.fromisoformat(data['event_end_time']) 

    build_event(**data)
    return jsonify(data)

# 暫時無法使用, 因為service account無法寄google calendar邀請, 且目前的calendar帳號非Google Workspace帳號
'''
@app.route('/attend_events', methods = ['POST'])
def attend_events():
    data = request.get_json()
    add_attendees(data['gcalendar_id'], data['attendee_email'])
    return jsonify(data)
'''

# 利用API建立活動場所
@app.route('/create_spaces', methods = ['POST'])
def create_spaces():
    '''
    Request: 
    1. space_name (str)
    2. space_capacity (str)
    3. type (str)
    '''
    data = request.get_json()

    build_space(**data)
    return jsonify(data)

# 啟動網站伺服器 可透過 port 參數指定埠號
if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 3000)