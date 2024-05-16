# This modul makes training plans for 10, 21, 42 K
def get_plan(ind, train_tempos):
    import csv
    from datetime import datetime, timedelta

    f_names = ['plan10K.csv', 'HMP.csv', '1-st_MP.csv', 'MP.csv']
    # select_d = ['10000 м', 'Полумарафон', 'Марафон']
    plan = dict()
    for k, val in train_tempos.items():
        exec(k +'= val')
    print(f_names[ind])
    with open('../guides/' + f_names[ind], encoding='utf-8') as file:
        rows = list(csv.DictReader(file, delimiter=';'))
        for row in rows:
            plan.update({row['week']:[eval(row['key run #1']), eval(row['key run #2']), eval(row['key run #3'])]})

    return plan


