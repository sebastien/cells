// --
// Cells kernel implementation for Deno. Run it like so:
// -- :shell|norun
// deno run --allow-net kernel.ts
// --
const hostname = "0.0.0.0";
const port = 8080;
const listener = Deno.listen({ hostname, port });

// SEE: https://www.typescriptlang.org/docs/handbook/2/basic-types.html
// SEE: https://doc.deno.land/builtin/stable
//
class Session {
  timestamp: Date;
  slots: Map<string, Slot>;

  constructor() {
    this.timestamp = new Date();
    this.slots = new Map();
  }
}

class Slot {
  inputs: Array<string>;
  definition: string;
  value: any;
  constructor() {
    this.inputs = [];
    this.definition = "";
    this.value = undefined;
  }
}

class Kernel {
  sessions: Map<string, Session>;
  constructor() {
    this.sessions = new Map();
  }
  handle(method: string, args: Array<any>): any {
    switch (method) {
      case "set":
        return this.set(args[0], args[1], args[2]);
      case "get":
        return this.get(args[0], args[1]);
      case "invalidate":
        return this.invalidate(args[0], args[1]);
      default:
        // TODO: Might want to throw an exception there
        return undefined;
    }
  }
  getSession(session: string): Session {
    return this.sessions.set(
      session,
      this.sessions.get(session) || new Session(),
    ).get(
      session,
    ) as Session;
  }
  getSlot(session: string, slot: string): Slot {
    const slots = this.getSession(session).slots;
    return slots.set(
      slot,
      slots.get(slot) || new Slot(),
    ).get(
      slot,
    ) as Slot;
  }
  set(
    session: string,
    slot: string,
    inputs: Array[string],
    source: string,
    value: any,
    type: string = "js",
  ): boolean {
    return true;
  }
  get(session: string, slot: string): any {
    return undefined;
  }

  invalidate(session: string, slots: Array<string>): boolean {
    return true;
  }
}

interface JSONRPCMessage {
  jsonrpc: string;
  method: string;
  params: Object;
  id: string;
}

const handle = (kernel: Kernel, message: JSONRPCMessage) => {
  const { jsonrpc, method, params, id } = message;
  return kernel.handle(method, Object.entries(params).map(([k, v]) => v));
};

const kernel: Kernel = new Kernel();
console.log(`Listening on ${hostname}:${port}`);
for await (const conn of listener) {
  const buffer = new Uint8Array(256_000);
  const strdec = new TextDecoder();
  // FIXME: That only works for a single connection
  while (true) {
    const n = await conn.read(buffer);
    if (!n) {
      console.warn("Maximum buffer size reached", n);
    } else {
      const s = strdec.decode(buffer).substring(0, n);
      if (n === buffer.length) {
        console.error("Maximum message size reached");
      } else {
        try {
          const value = JSON.parse(s);
          const result = handle(kernel, value);
          console.log("result", result);
        } catch (e) {
          console.error("Cannot parse JSON:", s);
        }
      }
      await conn.write(buffer);
    }
  }
}
