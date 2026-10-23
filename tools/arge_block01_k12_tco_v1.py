"""Block 01 A08 K12 five-year TCO calculator: provenance-gated, no invented prices."""
from decimal import Decimal, InvalidOperation

REQUIRED=("license","infrastructure","people","operations","migration","risk")

def five_year_cost(record):
    """Return HOLD absent sourced, comparable costs; calculate only upon valid evidence."""
    periods=record.get("years")
    if not isinstance(periods,list) or len(periods)!=5:return {"state":"HOLD_INPUT_SCOPE"}
    values=[]
    for year in periods:
        if not isinstance(year,dict) or set(year)!=set(REQUIRED):return {"state":"HOLD_COST_FIELDS"}
        subtotal=Decimal("0")
        for key in REQUIRED:
            item=year[key]
            if not isinstance(item,dict):return {"state":"HOLD_SOURCE_OR_UNIT"}
            if not isinstance(item,dict) or not item.get("source_ref") or not item.get("unit") or item.get("value") is None:
                return {"state":"HOLD_SOURCE_OR_UNIT"}
            try:
                v=Decimal(str(item["value"]))
            except (InvalidOperation,ValueError):
                return {"state":"HOLD_NON_NUMERIC"}
            if not v.is_finite() or v<0:return {"state":"HOLD_COST_VALUE"}
            subtotal+=v
        values.append(subtotal)
    if len({item["unit"] for year in periods for item in year.values()})!=1:
        return {"state":"HOLD_UNIT_COMPARABILITY"}
    return {"state":"CALCULATION_ONLY_NEEDS_INDEPENDENT_REVIEW","total":str(sum(values,Decimal("0"))),
            "sensitivity_minus_20pct":str(sum(values,Decimal("0"))*Decimal("0.8")),
            "sensitivity_plus_20pct":str(sum(values,Decimal("0"))*Decimal("1.2"))}
