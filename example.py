from library.InformaticsApi import InformaticsApi

api = InformaticsApi()

res = api.authorize(input('Login: '), input('Password: '))

problem = api.get_problem(111347)

res2 = api.submit_problem(3443, 'test.py', 27)

res3 = api.get_self_runs(3443)

res4 = api.get_run(res3.data.runs[0].id)

res5 = api.get_protocol(res3.data.runs[0].id)

pass
