import datetime
import json
import os

from flask import Flask, jsonify, request

app = Flask(__name__)


def get_task(date):
    """

    :param date: datetime
    :return: []
    """
    f_name = "{}.json".format(date.strftime("%Y-%m-%d"))
    if not os.path.exists(f_name):
        os.mknod(f_name)
    with open(f_name, "rb") as fd:
        tasks = fd.read()
        if len(tasks) != 0:
            task_list = json.loads(tasks)
        else:
            task_list = []
    return task_list


def update_task(date, data):
    """

    :param date: datetime
    :param data: task list
    :return: true or false
    """
    f_name = "{}.json".format(date.strftime("%Y-%m-%d"))
    try:
        if not os.path.exists(f_name):
            os.mknod(f_name)
        with open(f_name, "wb") as fd:
            json.dump(data, fd)
        return True
    except Exception as e:
        print(e)
        return False


def get_week_task(date):
    """

    :param date: datetime
    :return: []
    """
    week_days = []
    week_num = date.isoweekday()
    for day in xrange(1, week_num):
        week_days.append(date - datetime.timedelta(days=day))
    week_days.append(date)
    task_list = reduce(lambda cur, nex: cur + nex, map(lambda cur: get_task(cur), week_days))
    return task_list


@app.route("/api_v1/date/<str_date>", methods=['GET', 'POST'])
def date(str_date):
    day_obj = datetime.datetime.strptime(str_date, "%Y-%m-%d")
    if request.method == 'POST' and request.is_json:
        data = request.json
        out = update_task(day_obj, data.get("tasks", []))
        return jsonify({"code": 200, "message": "", "date": out})
    elif request.method == 'GET':
        task_list = sorted(get_task(day_obj), key=lambda t: t["level"], reverse=True)
        out = {
            "date": day_obj,
            "week": day_obj.isoweekday(),
            "tasks": task_list or [
                {
                    "task": "This e.g ",
                    "level": 100,
                    "rate": 0.1
                }
            ]
        }
        return jsonify(out)


@app.route("/api_v1/weekly/<week_date>", methods=['GET'])
def weekly(week_date):
    day_obj = datetime.datetime.strptime(week_date, "%Y-%m-%d")
    weekly_list = sorted(get_week_task(day_obj), key=lambda t: t["level"], reverse=True)
    return jsonify({"weekly": weekly_list})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
