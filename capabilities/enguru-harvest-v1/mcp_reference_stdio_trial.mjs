/** P05: real upstream Everything reference server over child-process stdio.
 * Source server: npm @modelcontextprotocol/server-everything@2.0.1
 * Client: @modelcontextprotocol/client@2.4.0; GitHub Node 24 runner only.
 */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';

const binary = resolve('node_modules/@modelcontextprotocol/server-everything/dist/index.js');
assert.ok(existsSync(binary), 'Pinned upstream Everything executable exists');
const transport = new StdioClientTransport({
  command: process.execPath,
  args: [binary, 'stdio'],
  stderr: 'pipe',
});
const client = new Client({ name: 'ENGURU-P05-Reference-Client', version: '1.0.0' });
let connected = false;
try {
  await client.connect(transport);
  connected = true;
  const found = await client.listTools();
  assert.ok(found.tools.some(t => t.name === 'echo'), 'Real Everything echo tool discovered');
  const message = 'ENGURU-REFERENCE-STDIO';
  const reply = await client.callTool({ name: 'echo', arguments: { message } });
  assert.notEqual(reply.isError, true, 'Reference echo success');
  assert.ok(JSON.stringify(reply).includes(message), 'Real reference echoed the fixture');
  const receipt = {
    schema: 'enguru.harvest.p05-real-stdio/v1',
    state: 'PASS_UPSTREAM_REFERENCE_STDIO_UNREVIEWED',
    upstream_server: '@modelcontextprotocol/server-everything@2.0.1',
    client: '@modelcontextprotocol/client@2.4.0',
    node_version: process.version,
    protocol: client.getServerVersion?.() ?? null,
    discovered_tools: found.tools.length,
    echo_response_sha256: createHash('sha256').update(JSON.stringify(reply)).digest('hex'),
    actual_child_process: true,
    network_server: false,
    paid_api_required: 0,
    osi_execution: 0,
    official_proven: 'HOLD',
  };
  writeFileSync('mcp-reference-stdio-receipt.json', JSON.stringify(receipt, null, 2) + '\n');
  console.log(JSON.stringify(receipt));
} finally {
  if (connected) await client.close();
  else await transport.close();
}
