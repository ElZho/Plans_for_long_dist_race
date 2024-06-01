#This modul contains function to calculate VDOT, target tempo to different kind of training runs


def find_vdot(dist, my_time) -> tuple:
    # this func is looking in guide nearest time for selected distance and gets VDOT

    from datetime import timedelta, datetime
    import csv

    vdot = '85'
    level = None
    with open('../guides/vdot.csv', encoding='utf-8') as file:
        rows = list(csv.DictReader(file, delimiter=';'))

        for index, row in enumerate(rows):
            # looking for fist faster time in selected distance

            if datetime.strptime(row[dist], '%H:%M:%S') <= my_time:
                if index > 0:
                    hl = [my_time - datetime.strptime(row[dist], '%H:%M:%S'),
                          datetime.strptime(rows[index - 1][dist], '%H:%M:%S') - my_time]
                    level = index - hl.index(min(hl))
                    correct_vdot = 0
                # if first row has time slower then users time, user has to low VDOT level, so VDOT from guid needs to
                # be correct
                else:
                    level = index
                    t = datetime.strptime(row[dist], '%H:%M:%S')
                    refer_time = timedelta(seconds=t.second, minutes=t.minute, hours=t.hour)
                    correct_vdot = round(100 / 3 * (my_time - datetime.strptime(row[dist],
                                                '%H:%M:%S')).total_seconds() / refer_time.total_seconds(), 0)
                break
        if level:
            vdot = int(rows[level]['VD0T']) - correct_vdot

        return vdot, rows[level]


def count_target_tempo(time5k, vdot):
    #count tempo for training runs
    import csv
    from datetime import datetime, timedelta

    t = datetime.strptime(time5k, '%H:%M:%S')
    t = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
    # correct if vdot lower then 30
    if vdot < 30:
        t *= (1+0.03*(30-vdot))

    time5k = t
    difference = (time5k - timedelta(minutes=16)).total_seconds()

    times = dict()
    with open('../guides/base_koef.csv', encoding='utf-8') as file:
        rows = list(csv.DictReader(file, delimiter=';'))

        for row in rows:

            target = datetime.strptime(row['base'], '%H:%M:%S') + timedelta(seconds=float(row['koef'])*difference/10)
            target = timedelta(minutes=target.minute, seconds=target.second, microseconds=target.microsecond)
            target = target/float(row['dist'])
            times.update({row['name']: timedelta(seconds=round(target.total_seconds())) })

    return times
