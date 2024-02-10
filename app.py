from flask import Flask, request, jsonify
from module import *

# 初始化Flask伺服器
app = Flask(__name__)

# 給定bgn_time(時間範圍開始) / end_time(時間範圍結束) / location / capacity, 回傳條件內的活動
@app.route('/show_events')
def show_events():
    '''
    Input parameters: 
    1. range_bgn_time (str, 'yyyy-mm-ddThh:mm:ss')
    2. range_end_time (str, 'yyyy-mm-ddThh:mm:ss')
    3. location (str)
    4. capacity (str, '3-5' or '6-10' or '11-20' or '21-50' or '51-100')
    '''
    filter_dict = {}


    # ----- time range -----
    range_bgn_time = request.args.get('range_bgn_time')
    if range_bgn_time:
        # range_bgn_time = datetime.strptime(range_bgn_time, '%Y-%m-%dT%H:%M')
        range_bgn_time = datetime.strptime(range_bgn_time, '%Y-%m-%d')
        filter_dict['event_end_time'] = {'$gt': range_bgn_time}

    range_end_time = request.args.get('range_end_time')
    if range_end_time:
        # range_end_time = datetime.strptime(range_end_time, '%Y-%m-%dT%H:%M')
        range_end_time = datetime.strptime(range_end_time, '%Y-%m-%d')
        filter_dict['event_bgn_time'] = {'$lt': range_end_time}
    

    # ----- location -----
    location = request.args.get('location') # 輸入場地名稱
    capacity = request.args.get('capacity') # 單純是輸入人數區間
    if location and capacity:
        space_name_lst = space_info_collection.find({'space_capacity': {'$eq': capacity}}).distinct('space_name')
        fin_loc_list = list(set(space_name_lst) & set([location]))
        filter_dict['event_location'] = {'$in': fin_loc_list}
    if location and (not capacity):
        filter_dict['event_location'] = {'$eq': location}
    if (not location) and capacity:
        space_name_lst = space_info_collection.find({'space_capacity': {'$eq': capacity}}).distinct('space_name')
        filter_dict['event_location'] = {'$in': space_name_lst}

    range_event = list(event_info_collection.find({'$and': [filter_dict]}))
    return jsonify(dumps(range_event))

# 給定 attendees (人數), 回傳適合的活動場地
@app.route('/show_locations')
def show_locations():
    '''
    Input parameters: 
    1. attendees (str in int format)
    '''
    attendees = int(request.args.get('attendees'))
    if attendees:
        if attendees <= 5:
            range_space = list(space_info_collection.find({'space_capacity': {'$eq': '3-5'}}))
        elif attendees <= 10:
            range_space = list(space_info_collection.find({'space_capacity': {'$eq': '6-10'}}))
        elif attendees <= 20:
            range_space = list(space_info_collection.find({'space_capacity': {'$eq': '11-20'}}))
        elif attendees <= 50:
            range_space = list(space_info_collection.find({'space_capacity': {'$eq': '21-50'}}))
        elif attendees <= 100:
            range_space = list(space_info_collection.find({'space_capacity': {'$eq': '51-100'}}))
        else:
            range_space = ['Too many attendees! The largest space can accommodate up to 100 people at most.']
    else:
        range_space = ['Please specify the number of attendees for your event.']

    return jsonify(dumps(range_space))

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
#@app.route('/attend_events', methods = ['POST'])
#def attend_events():
#    data = request.get_json()
#    add_attendees(data['gcalendar_id'], data['attendee_email'])
#    return jsonify(data)

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