/** ENGÜRÜ P07: real TypeScript MCP v2 SDK, in-memory fixture, no remote ports. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { writeFileSync } from 'node:fs';
import { McpServer, InMemoryTransport } from '@modelcontextprotocol/server';
import { Client } from '@modelcontextprotocol/client';
import * as z from 'zod/v4';

const server = new McpServer({ name: 'ENGURU-TS-V2-Fixture', version: '1.0.0' });
server.registerTool(
  'sha256_text',
  { description: 'Compute SHA256 of a deterministic fixture', inputSchema: z.object({ text: z.string() }) },
  async ({ text }) => ({
    content: [{ type: 'text', text: createHash('sha256').update(text, 'utf8').digest('hex') }]
  }),
);
const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
const client = new Client({ name: 'ENGURU-Harvest-Client', version: '1.0.0' });
try {
  await server.connect(serverTransport);
  await client.connect(clientTransport);
  const tools = await client.listTools();
  assert.ok(tools.tools.some(t => t.name === 'sha256_text'), 'tool discovery');
  const expected = createHash('sha256').update('ENGURU', 'utf8').digest('hex');
  const output = await client.callTool({ name: 'sha256_text', arguments: { text: 'ENGURU' } });
  assert.notEqual(output.isError, true, 'tool call should not have an error');
  assert.ok(JSON.stringify(output).includes(expected), 'returned digest');
  let invalidRejected = false;
  try {
    const bad = await client.callTool({ name: 'sha256_text', arguments: { text: 123 } });
    invalidRejected = bad.isError === true;
  } catch {
    invalidRejected = true;
  }
  assert.ok(invalidRejected, 'schema rejects invalid input');
  const result = {
    schema: 'enguru.harvest.p07-typescript-mcp/v1',
    state: 'PASS_TYPESCRIPT_SDK_REAL_IN_MEMORY_UNREVIEWED',
    tool_count: tools.tools.length,
    actual_client_server_call: true,
    invalid_argument_rejected: true,
    digest: expected,
    sdk_version: '2.4.0',
    runtime: process.version,
    note: 'Linked InMemoryTransport is 2025-era compatibility transport, not a 2026 wire acceptance test',
    actual_model_used: false,
    paid_api_required: 0,
    osi_execution: 0,
    independent_review: 'HOLD'
  };
  writeFileSync('mcp-typescript-receipt.json', JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result));
} finally {
  await client.close();
  await server.close();
}
