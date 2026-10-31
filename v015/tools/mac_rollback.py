"""Non-destructive rollback: restore launch path by opening the preserved app.

This release never replaces the previous Ulak. Closing the new app and opening
the previous one is the rollback. No deletion or database restoration is needed.
This helper produces a recovery note only and makes no system change.
"""
import json
from pathlib import Path
if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'ROLLBACK_NOTE.json'
    with p.open('x') as f:json.dump({'action':'CLOSE_NEW_APP_OPEN_PRESERVED_ULAK',
        'old_apps_changed':False,'delete_performed':False,'restore_performed':False},f,indent=2)
    print(p)
