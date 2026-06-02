import json


def get_latest_jobs():
    with open('positions.json') as f:
        data = json.load(f)

    # print(data)
    all_jobs = []
    for k, v in data.items():
        print(k)
        all_jobs.append(k)
    print(len(all_jobs))
    return all_jobs