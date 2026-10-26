#!/usr/bin/env python3
"""Finite-state transitions for isolated review-only install model."""
import json
TRANS={"DEFINED":{"INVENTORY"},"INVENTORY":{"BUILT","HOLD"},"BUILT":{"TESTED","HOLD"},"TESTED":{"PACKAGED","HOLD"},"PACKAGED":{"STAGED","HOLD"},"STAGED":{"INSTALLED","RECOVERY","HOLD"},"RECOVERY":{"ROLLED_BACK","HOLD"},"INSTALLED":{"HEALTHY","RECOVERY"},"HEALTHY":{"FIELD_REVIEW","RECOVERY"},"FIELD_REVIEW":{"ACCEPTED","HOLD"},"ROLLED_BACK":set(),"ACCEPTED":set(),"HOLD":set()}
def transition(current,target,source_ok=True,authority_ok=True):
 if current not in TRANS or target not in TRANS:return "HOLD_UNKNOWN_STATE"
 if not source_ok:return "HOLD_SOURCE_DRIFT"
 if not authority_ok:return "HOLD_REVOKED_AUTHORITY"
 if target not in TRANS[current]:return "HOLD_ILLEGAL_TRANSITION"
 return target
def simulate():
 checks=0
 for _ in range(3):
  state="DEFINED"
  for dest in ["INVENTORY","BUILT","TESTED","PACKAGED","STAGED","INSTALLED","HEALTHY","FIELD_REVIEW","ACCEPTED"]:
   state=transition(state,dest);assert state==dest;checks+=1
  assert transition("STAGED","RECOVERY")=="RECOVERY";checks+=1
  assert transition("RECOVERY","ROLLED_BACK")=="ROLLED_BACK";checks+=1
  assert transition("STAGED","ACCEPTED")=="HOLD_ILLEGAL_TRANSITION";checks+=1
  assert transition("STAGED","INSTALLED",source_ok=False)=="HOLD_SOURCE_DRIFT";checks+=1
  assert transition("STAGED","INSTALLED",authority_ok=False)=="HOLD_REVOKED_AUTHORITY";checks+=1
 print(json.dumps({"three_rounds":3,"transition_checks":checks,"state":"PASS_THEORETICAL_STATE_MACHINE","crash_persistence":"HOLD","osi_mutation":0}))
if __name__=="__main__":simulate()
