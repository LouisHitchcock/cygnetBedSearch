import { D1Database } from "@cloudflare/workers-types";

export interface Env {
  DB: D1Database;
  API_TOKEN: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      if (path === "/api/data" && request.method === "POST") {
        return await handleInsert(request, env, corsHeaders);
      }

      if (path === "/api/data/today" && request.method === "GET") {
        return await handleGetToday(env, corsHeaders);
      }

      if (path === "/api/data/all" && request.method === "GET") {
        return await handleGetAll(env, corsHeaders);
      }

      if (path === "/api/data/range" && request.method === "GET") {
        return await handleGetRange(request, env, corsHeaders);
      }

      if (path === "/api/data/changes" && request.method === "GET") {
        return await handleGetChanges(request, env, corsHeaders);
      }

      if (path === "/api/migrate" && request.method === "POST") {
        return await handleMigrate(request, env, corsHeaders);
      }

      return new Response(JSON.stringify({ error: "Not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json", ...corsHeaders },
      });
    } catch (err: any) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders },
      });
    }
  },
};

function auth(request: Request, env: Env): boolean {
  const authHeader = request.headers.get("Authorization");
  return authHeader === `Bearer ${env.API_TOKEN}`;
}

async function handleInsert(
  request: Request, env: Env, headers: Record<string, string>
): Promise<Response> {
  if (!auth(request, env)) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401, headers: { "Content-Type": "application/json", ...headers },
    });
  }
  const { rows }: { rows: [string, string, number, string, string, string][] } = await request.json();
  if (!rows || rows.length === 0) {
    return new Response(JSON.stringify({ error: "No rows provided" }), {
      status: 400, headers: { "Content-Type": "application/json", ...headers },
    });
  }
  const stmt = env.DB.prepare(
    "INSERT INTO bed_data (name, sex, beds, purpose, date, time) VALUES (?, ?, ?, ?, ?, ?)"
  );
  const batch = rows.map((r) => stmt.bind(r[0], r[1], r[2], r[3], r[4], r[5]));
  const results = await env.DB.batch(batch);
  return new Response(JSON.stringify({ inserted: results.length }), {
    status: 201, headers: { "Content-Type": "application/json", ...headers },
  });
}

async function handleGetToday(env: Env, headers: Record<string, string>): Promise<Response> {
  const { results } = await env.DB.prepare(
    `SELECT * FROM bed_data WHERE date = (SELECT MAX(date) FROM bed_data) ORDER BY purpose, name`
  ).all();
  return new Response(JSON.stringify(results), {
    headers: { "Content-Type": "application/json", ...headers },
  });
}

async function handleGetAll(env: Env, headers: Record<string, string>): Promise<Response> {
  const { results } = await env.DB.prepare(
    `SELECT * FROM bed_data ORDER BY date, time, purpose, name`
  ).all();
  return new Response(JSON.stringify(results), {
    headers: { "Content-Type": "application/json", ...headers },
  });
}

async function handleGetRange(
  request: Request, env: Env, headers: Record<string, string>
): Promise<Response> {
  const from = urlQuery(request, "from");
  const to = urlQuery(request, "to");
  if (!from || !to) {
    return new Response(JSON.stringify({ error: "from and to query params required" }), {
      status: 400, headers: { "Content-Type": "application/json", ...headers },
    });
  }
  const { results } = await env.DB.prepare(
    `SELECT * FROM bed_data WHERE date >= ? AND date <= ? ORDER BY date, time, purpose, name`
  ).bind(from, to).all();
  return new Response(JSON.stringify(results), {
    headers: { "Content-Type": "application/json", ...headers },
  });
}

async function handleGetChanges(
  request: Request, env: Env, headers: Record<string, string>
): Promise<Response> {
  const dateParam = urlQuery(request, "date");
  if (!dateParam) {
    return new Response(JSON.stringify({ error: "date query param required" }), {
      status: 400, headers: { "Content-Type": "application/json", ...headers },
    });
  }
  const dt = new Date(dateParam);
  const prev = new Date(dt);
  prev.setDate(prev.getDate() - 1);
  const prevStr = prev.toISOString().split("T")[0];

  const today = await env.DB.prepare(`SELECT * FROM bed_data WHERE date = ?`).bind(dateParam).all();
  const yesterday = await env.DB.prepare(`SELECT * FROM bed_data WHERE date = ?`).bind(prevStr).all();

  const yMap = new Map<string, number>();
  for (const row of yesterday.results as any[]) {
    yMap.set(`${row.name}|${row.purpose}`, row.beds);
  }

  const changes: any[] = [];
  for (const row of today.results as any[]) {
    const key = `${row.name}|${row.purpose}`;
    const yBeds = yMap.get(key);
    if (yBeds !== undefined && yBeds !== row.beds) {
      changes.push({
        name: row.name, purpose: row.purpose, sex: row.sex,
        beds_yesterday: yBeds, beds_today: row.beds,
      });
    }
  }
  return new Response(JSON.stringify({ date: dateParam, changes }), {
    headers: { "Content-Type": "application/json", ...headers },
  });
}

async function handleMigrate(
  request: Request, env: Env, headers: Record<string, string>
): Promise<Response> {
  if (!auth(request, env)) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401, headers: { "Content-Type": "application/json", ...headers },
    });
  }
  const { rows }: { rows: [string, string, number, string, string, string][] } = await request.json();
  if (!rows || rows.length === 0) {
    return new Response(JSON.stringify({ error: "No rows provided" }), {
      status: 400, headers: { "Content-Type": "application/json", ...headers },
    });
  }
  const stmt = env.DB.prepare(
    "INSERT INTO bed_data (name, sex, beds, purpose, date, time) VALUES (?, ?, ?, ?, ?, ?)"
  );
  let total = 0;
  for (let i = 0; i < rows.length; i += 100) {
    const batch = rows.slice(i, i + 100).map((r) => stmt.bind(r[0], r[1], r[2], r[3], r[4], r[5]));
    await env.DB.batch(batch);
    total += batch.length;
  }
  return new Response(JSON.stringify({ inserted: total }), {
    status: 201, headers: { "Content-Type": "application/json", ...headers },
  });
}

function urlQuery(request: Request, key: string): string | null {
  return new URL(request.url).searchParams.get(key);
}
