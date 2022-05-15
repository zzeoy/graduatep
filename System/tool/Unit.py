Pc = 0.95
# 内部杂交概率
P_inc = 0.85
# 变异概率
Pm = 0.05
# 迭代数量
T = 10
# 初始个体数
Num = 2000
# 初始个体(用于测试)
context = "{\"Task\":[{  \"name\": \"T1\",\"pred\": null,\"weight\": 3},{   \"name\": \"T2\",\"pred\": null, " \
          "\"weight\": 4},{\"name\":\"T3\",\"pred\":\"T1\",\"weight\":5},{\"name\":\"T4\",\"pred\":\"T1,T2\"," \
          "\"weight\":6},{\"name\":\"T5\",\"pred\":null,\"weight\":7},{\"name\":\"T6\",\"pred\":\"T3,T4\"," \
          "\"weight\":8},{\"name\":\"T7\",\"pred\":\"T4,T2,T5\",\"weight\":9},{\"name\":\"T8\",\"pred\":\"T6,T4,T7\"," \
          "\"weight\":10}]} "
context2="{\"Task\":[" \
         "{  \"name\": \"T1\",\"pred\": null,\"weight\": 3},{   \"name\": \"T2\",\"pred\": null,\"weight\": 4}," \
         "{   \"name\": \"T3\",\"pred\": \"T1\",\"weight\": 5},{   \"name\": \"T4\",\"pred\": \"T1,T2\",\"weight\": 6}," \
         "{   \"name\": \"T5\",\"pred\": null,\"weight\": 7},{   \"name\": \"T6\",\"pred\": \"T3,T4\",\"weight\": 8}," \
         "{   \"name\": \"T7\",\"pred\": \"T4,T2,T5\",\"weight\": 9},{   \"name\": \"T8\",\"pred\":\"T6,T4,T7\",\"weight\": 10}," \
         "{   \"name\": \"T9\",\"pred\":\"T6,T4,T7\",\"weight\": 11},{   \"name\": \"T10\",\"pred\":\"T6,T4,T7\",\"weight\": 12}," \
         "{   \"name\": \"T11\",\"pred\":\"T6,T4,T7\",\"weight\": 13},{   \"name\": \"T12\",\"pred\":\"T6,T5,T7\",\"weight\": 14}," \
         "{   \"name\": \"T13\",\"pred\":\"T6,T4,T7\",\"weight\": 15}" \
         "]}"