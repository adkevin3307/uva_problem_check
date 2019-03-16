import os
import re
import json
import pickle
import argparse
from requests_html import HTMLSession

problems = {}
conf = {}

def load_problems(state):
    global problems
    if state:
        print('get problems by website')
        for i in range(5):
            problems[str(i + 1)] = []
        session = HTMLSession()
        r = session.get('http://par.cse.nsysu.edu.tw/~advprog/star.php')
        if r.status_code == 200:
            r.html.render()
            for tr in r.html.find('#list0 tbody tr'):
                value, key = tuple(map(lambda x: x.text, tr.find('.list_problem')))
                if (key in problems.keys()) and (value not in problems[key]):
                    problems[key].append(value)
        with open('problems.pkl', 'wb') as file:
            pickle.dump(problems, file)
    else:
        print('get problems by problems.pkl')
        with open('problems.pkl', 'rb') as file:
            problems = pickle.load(file)

def update_path(path):
    global conf
    if path != None:
        conf['folder'] = path
        return True
    return False

def update_re(re):
    global conf
    if re != None:
        conf['re'] = re
        return True
    return False

def update_configure(path, re):
    global conf
    if os.path.exists('configure.json'):
        with open('configure.json', 'r') as file:
            conf = json.load(file)
    if (not update_path(path)) and (not os.path.exists('configure.json')):
        conf['folder'] = './'
    if (not update_re(re)) and (not os.path.exists('configure.json')):
        conf['re'] = '(UVa_)?([0-9]+)(\([0-9a-zA-Z]*\))?.([a-zA-Z]+)'

    with open('configure.json', 'w') as file:
        json.dump(conf, file)


def file_check(dir_path):
    for path, _, files in os.walk(dir_path):
        for file in files:
            if os.path.isfile(os.path.join(path, file)):
                problem = re.match(conf['re'], file)
                if problem != None:
                    for key in problems.keys():
                        if problem[2] in problems[key]:
                            problems[key].remove(problem[2])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'UVa Problems Check')
    parser.add_argument('-u', '--update', action = 'store_true', help = 'update website data')
    parser.add_argument('-p', '--path', type = str, help = 'directory path')
    parser.add_argument('-r', '--re', type = str, help = 'regular expression for filename')
    args = parser.parse_args()

    load_problems((args.update or (not os.path.exists('problems.pkl'))))

    update_configure(args.path, args.re)
    file_check(conf['folder'])

    n = input('Problem Level: ')
    print(problems[n][0])