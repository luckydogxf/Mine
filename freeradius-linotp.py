1. Python3 和lintop3.2.3
2. 发送验证请求到lintop, 用freeradius的Python3模块去验证。
3. Linotp在以后的版本，将废弃HTTP Get。
4. Access-Request是一个dict/tuples的数据类型。

#!/usr/bin/env python3

import radiusd,requests,json

url="https://172.16.205.114/validate/check"

# Check post_auth for the most complete example using different
# input and output formats

def instantiate(p):
  print("*** instantiate ***")
  print(p)
  # return 0 for success or -1 for failure

def preacct(p):
  print("*** preacct ***")
  print(p)
  return radiusd.RLM_MODULE_OK

def authorize(p):
  radiusd.radlog(radiusd.L_INFO, '*** radlog call in authorize ***')
  #print(p)
  print(radiusd.config)
  return radiusd.RLM_MODULE_OK


def authenticate(p):
  print("*** authenticate ***")
  # debug purpose
  print(p)
  # check OTP logic

  # if check_otp failed
  #  return LM_MODULE_REJECT/FAILED
  #  else
  #return radiusd.RLM_MODULE_HANDLED
  post_params = {"user": p['request'][0][1],
                     "pass": p['request'][1][1],
                     "realm": "pthl.hk"}
  # do request
  # self-signed certificate.
  response = requests.post(url, data=post_params,verify=False)

  # parse response as json
  json_response = json.loads(response.text)

  authenticated = json_response[u"result"][u"value"]

  if authenticated:

     return radiusd.RLM_MODULE_OK

  else:
     print("json response: {}".format(json_response))

     return radiusd.RLM_MODULE_FAIL
