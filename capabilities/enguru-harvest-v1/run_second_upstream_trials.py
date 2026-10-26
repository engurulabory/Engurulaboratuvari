"""Actual GitHub CI integration probes: reference Agent Skills and MCP v2.

Only pinned upstream packages are imported. No Mac OSi execution, network
server, paid model or external authorization is involved in these probes.
The CI results remain unreviewed *integration evidence*, not PROVEN acceptance.
"""
import asyncio
import hashlib
import json
import subprocess
import tempfile
from importlib.metadata import version
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def agent_skills_reference():
    from skills_ref import validate, read_properties, to_prompt
    locations=[
        ROOT/".agents/skills/enguru-evidence-harvest",
        ROOT/".claude/skills/enguru-evidence-harvest",
    ]
    properties=[]
    for location in locations:
        problems=validate(location)
        if problems:
            raise AssertionError(f"Agent Skills upstream validation failed: {problems!r}")
        props=read_properties(location)
        if props.name!="enguru-evidence-harvest":
            raise AssertionError("Unexpected skill name")
        properties.append({"path":str(location.relative_to(ROOT)),"name":props.name})
    xml=to_prompt(locations)
    if "enguru-evidence-harvest" not in xml or "<available_skills>" not in xml:
        raise AssertionError("Agent Skills prompt export failed")
    with tempfile.TemporaryDirectory() as temp:
        bad=Path(temp)/"bad-skill"
        bad.mkdir()
        (bad/"SKILL.md").write_text("---\nname: WRONG\ndescription: invalid\n---\n",encoding="utf-8")
        errors=validate(bad)
        if not errors:
            raise AssertionError("Invalid skill unexpectedly accepted")
    return {"state":"PASS_UPSTREAM_VALIDATOR_FIXTURE","validated":properties,
            "bad_skill_rejected":True,"prompt_export_checked":True,
            "scope":"P03_AGENT_SKILLS_REFERENCE_ONLY"}

async def _mcp_fixture():
    from mcp import Client
    from mcp.server import MCPServer
    server=MCPServer("ENGURU-Harvest-InProcess")

    @server.tool()
    def sha256_text(text: str) -> str:
        """Return SHA256 for a UTF-8 string; no external resources."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async with Client(server,raise_exceptions=True) as client:
        tools=await client.list_tools()
        if "sha256_text" not in [t.name for t in tools.tools]:
            raise AssertionError("MCP tool discovery failed")
        digest=hashlib.sha256(b"ENGURU").hexdigest()
        reply=await client.call_tool("sha256_text",{"text":"ENGURU"})
        if reply.is_error or digest not in json.dumps(reply.model_dump(),ensure_ascii=False):
            raise AssertionError("MCP actual call failed: "+str(reply))
        if not client.protocol_version:
            raise AssertionError("Missing actual negotiated MCP version")
        return {"state":"PASS_MCP_INPROCESS_REAL_PROTOCOL","server":"ENGURU-Harvest-InProcess",
                "negotiated_version":str(client.protocol_version),
                "digest":digest,"tool_count":len(tools.tools),
                "scope":"P06_PROTOCOL_FIXTURE_ONLY_NO_NETWORK"}

def main():
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    output={"schema":"enguru.harvest.github-integration-trials/v1","github_head":head,
            "dependency_versions":{"mcp":version("mcp"),"skills_ref":version("skills-ref")},
            "source_executed_on":"GITHUB_RUNNER_ONLY","osi_execution":0,
            "mandatory_paid_api":0,"external_proven_skills":0,"review":"HOLD"}
    output["P03"]=agent_skills_reference()
    output["P06"]=asyncio.run(_mcp_fixture())
    output["status"]="PASS_GITHUB_REAL_INTEGRATION_UNREVIEWED"
    file=Path("second-upstream-trial-receipt.json")
    file.write_text(json.dumps(output,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(output,sort_keys=True,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
