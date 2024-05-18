# This modul makes training plans for 10, 21, 42 K
def get_plan(ind, train_tempos):
    import csv
    from datetime import datetime, timedelta

    f_names = ['plan10K.csv', 'HMP.csv', '1-st_MP.csv', 'MP.csv']
    # select_d = ['10000 м', 'Полумарафон', 'Марафон']
    plan = dict()
    for k, val in train_tempos.items():
        exec(k +'= val')

    with open('../guides/' + f_names[ind], encoding='utf-8') as file:
        rows = list(csv.DictReader(file, delimiter=';'))
        for row in rows:
            plan.update({row['week']:[eval(row['key run #1']), eval(row['key run #2']), eval(row['key run #3'])]})

    return plan


def sent_plan(distance, Info_text, train_plan, ID):
    print('start')
    with open('../calc_plans/Plan for ' +distance + '_'+ str(ID) +'.txt', 'w', encoding='utf-8') as file:

        file.write('<h1 Plan for ' + distance + '</h2>\n')
        file.writelines(Info_text)
        file.writelines(['\n{} week  to race: \n-------\n1-st train: {}.\n2-nd train: {}.\n3-rd train: {}.'.format(k, *v)
                         for k, v in train_plan.items()])
        file.write('\n\nLegenda\n-------\n')
        file.write('8x400 (400 RI) - 8 times for 400 m with rest 400m\n')
        file.write('6x800 (90 sec RI) - 6 times for 400 m with rest 90 sec\n')
        file.write('1,5 км easy - 1,5 K on 2-nd pulse zone')


