"""Read-only classification of historical receipt against observed current main.
A historical receipt is not current-main acceptance.
"""
import json
import re
import sys
def classify(record, current):
  a=record.get("source_commit")
  b=current.get("main_sha")
  valid=lambda x:isinstance(x,str) and bool(re.fullmatch("[0-9a-f]{40}",x))
  if not (valid(a) and valid(b)):
    return {"state":"HOLD_GUVENLI_DUR","reason":"SOURCE_IDENTITY_REQUIRED","current_main_accepted":False}
  if a!=b:
    return {"state":"PASS_HISTORICAL_DRIFT_CLASSIFIED","reason":"NEW_CURRENT_MAIN_RECEIPT_REQUIRED","current_main_accepted":False,"historical_commit":a,"current_main":b,"official_finish":"HOLD"}
  return {"state":"HOLD_GUVENLI_DUR","reason":"AUTHENTIC_CURRENT_MAIN_RECEIPT_REQUIRED","current_main_accepted":False,"official_finish":"HOLD"}
if __name__=="__main__":
  print(json.dumps(classify(json.load(open(sys.argv[1])),json.load(open(sys.argv[2]))),sort_keys=True))
