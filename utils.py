import pathlib


def write_to_csv(data, _file):
    file_obj = pathlib.Path(__file__).parent.joinpath('data').joinpath('{}.csv'.format(_file)).resolve()
    with open(str(file_obj), 'a', encoding='utf-8') as f:
        f.write(','.join([str(e) for e in data])+'\n')
    return True


def read_csv_last_row(user_id=1):
    res = {}
    for f in ('schedule', 'sleep', 'traffic', 'weather'):
        header = None
        row = None
        rows = []
        file_obj = pathlib.Path(__file__).parent.joinpath('data').joinpath('{}.csv'.format(f)).resolve()
        with open(str(file_obj), 'r', encoding='utf-8') as fp:
            user_id_index = None
            for line in fp.readlines():
                line = line.strip().split(',')
                if header is None:
                    header = line
                    if 'UserID' in header:
                        user_id_index = header.index('UserID')
                    continue
                if f != 'schedule':
                    if user_id_index is not None and str(line[user_id_index]) == str(user_id):
                        row = line
                    elif user_id_index is None:
                        row = line
                else:
                    if user_id_index is not None and str(line[user_id_index]) == str(user_id):
                        rows.append(line)

        assert header is not None
        if f != 'schedule':
            assert row is not None, 'no data for user {}'.format(user_id)
            assert len(header) == len(row)
            res[f] = {k: v for k, v in zip(header, row)}
        else:
            assert rows, 'no data for user {}'.format(user_id)
            res[f] = [{k: v for k, v in zip(header, row)} for row in rows]
    return res


def calc_mood(user_id=1):
    tense = happy = excite = 0
    data = read_csv_last_row(user_id)

    if int(data['weather']['Temperature']) < 10:
        tense += 1
        happy += 1
        print('Temperature too low')
    elif int(data['weather']['Temperature']) >= 25:
        tense += 1
        happy += 1
        excite += 1
        print('Temperature too high')

    if int(data['weather']['WindPower']) > 4:
        tense += 1
        happy += 1
        print('WindPower too high')

    try:
        if int(data['weather']['AQI']) >= 100:
            tense += 1
            happy += 1
            excite += 1
            print('AQI too high')
    except (TypeError, ValueError):
        print('can not int AQI {}'.format(data['weather']['AQI']))

    if '晴' in data['weather']['GeneralWeather'] or '多云' in data['weather']['GeneralWeather']:
        print('GeneralWeather is good')
    else:
        tense += 1
        happy += 1
        excite += 1
        print('GeneralWeather is bad')

    if int(data['sleep']['WakeUpTimestamp']) - int(data['sleep']['SleepTimestamp']) < 6 * 3600:
        print('sleep too short!')
        tense += 1
        happy += 1

    if int(data['sleep']['DeepSleepTime']) < 90:
        print('DeepSleepTime too short!')
        tense += 1
        happy += 1

    if int(data['sleep']['WakeUpTimes']) > 1:
        print('WakeUpTimes too many!')
        tense += 1
        happy += 1
        excite += 1

    meeting_cnt = 0
    dating_cnt = 0
    party_cnt = 0
    for row in data['schedule']:
        if row['Content'] == 'Meeting':
            meeting_cnt += 1
        elif row['Content'] == 'Dating':
            dating_cnt += 1
        elif row['Content'] == 'Party':
            party_cnt += 1

    if meeting_cnt > 3:
        print('meeting_cnt too many!')
        tense += 1
        happy += 1
        excite += 1

    if dating_cnt > 0:
        print('Dating!')
        happy -= 1
        excite += 1

    if party_cnt > 0:
        print('Party!')
        happy -= 1
        excite += 1

    if int(data['traffic']['TrafficJam']) > 1:
        happy += 1

    return tense, happy, excite


def get_adj(t, h, e):
    res = []
    res.append('紧张') if t > 4 else res.append('放松')
    res.append('悲伤') if h > 5 else res.append('愉快')
    res.append('激动') if e > 2 else res.append('平静')
    return res


def get_image_and_text(adjs):
    config = pathlib.Path(__file__).parent.joinpath('config.txt').read_text(encoding='utf-8')
    d = {}
    for line in config.split('\n'):
        line = line.strip()
        if not line:
            continue
        adj, image, text = line.split()
        adj = [adj[0:2], adj[2:4], adj[4:]]
        adj = tuple(sorted(adj))
        d[adj] = {}
        d[adj]['image'] = image
        d[adj]['text'] = text
    return d[tuple(sorted(list(adjs)))]


if __name__ == '__main__':
    print(get_image_and_text(['紧张', '平静', '悲伤']))
