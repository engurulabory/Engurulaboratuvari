"""Five-sortie source-only simulation in GitHub OSi Twin (never native acceptance)."""
import json
from pathlib import Path
from tools.enguru_suzgec_v24_delivery_inventory import FILES, build
from tools.enguru_suzgec_v24_transitive_closure import assess

SORTIES=("SOURCE_DELIVERY","LOCAL_TEST_EXECUTION","TWIN_PARITY","NATIVE_AUTHORITY","VERIFIED_FINISH")
def simulate(root):
    root=Path(root).resolve()
    inv=build(root)
    closure=assess(root,FILES)
    basic=inv["state"]=="PASS_BOUNDED_GITHUB_SOURCE_INVENTORY_ONLY" and len(inv["files"])==len(FILES)
    static=closure["state"]=="PASS_BOUNDED_STATIC_CLOSURE_ONLY"
    records=[
        {"sortie":SORTIES[0],"simulation":"PASS_CANDIDATE_SOURCE_SCOPE_ONLY" if basic else "HOLD_GUVENLI_DUR","field":"HOLD_OSi_DELIVERY_NOT_OBSERVED"},
        {"sortie":SORTIES[1],"simulation":"PASS_GITHUB_CI_TESTS_REQUIRED_SEPARATELY" if basic else "HOLD_GUVENLI_DUR","field":"HOLD_LOCAL_OSi_EXECUTION_NOT_OBSERVED"},
        {"sortie":SORTIES[2],"simulation":"PASS_STATIC_IMPORT_CLOSURE_ONLY" if static else "HOLD_GUVENLI_DUR","field":"HOLD_BEHAVIOR_PARITY_NOT_OBSERVED"},
        {"sortie":SORTIES[3],"simulation":"HOLD_NO_NATIVE_ISSUER_GRANT_WRITER_PROOF","field":"HOLD_NATIVE_AUTHORITY"},
        {"sortie":SORTIES[4],"simulation":"HOLD_NO_NATIVE_PROGRESS_HUMAN_THRESHOLD","field":"HOLD_VERIFIED_FINISH"},
    ]
    return {"schema":"enguru.suzgec.v24.five-sortie-twin-simulation/v1",
            "goal":"HEDEF_KABUL_SINIRLARI_8_ASAMA_GERCEK_KANIT_VERIFIED_FINISH_BITTI_DUR",
            "scope":"GITHUB_CANDIDATE_SIMULATION_ONLY",
            "source_count":len(inv["files"]),"source_total":len(FILES),
            "static_closure":closure["state"],"sorties":records,
            "state":"PASS_BOUNDED_FIVE_SORTIE_SIMULATION_ONLY" if basic and static else "HOLD_GUVENLI_DUR",
            "nativeAuthority":"HOLD","verifiedFinish":"HOLD","osiRepositoryWrites":0}

if __name__=="__main__":
    result=simulate(Path(__file__).resolve().parents[1])
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result["state"]=="PASS_BOUNDED_FIVE_SORTIE_SIMULATION_ONLY" else 50)
