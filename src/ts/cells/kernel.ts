// --
// Cells kernel implementation for Deno. Run it like so:
// -- :shell+norun
// deno run --allow-net kernel.ts
// --
const hostname = "0.0.0.0";
const port = 8080;

// SEE: https://www.typescriptlang.org/docs/handbook/2/basic-types.html
// SEE: https://doc.deno.land/builtin/stable

// --
// The `Session` object wraps a map of `slots`
// --
class Session {
  timestamp: Date;
  slots: Map<string, Slot>;

  constructor() {
    this.timestamp = new Date();
    this.slots = new Map();
  }
}

// --
// Each `Slot` has a definition (the source), a set of input cells (as a list of name)
// and a value (a serializable JavaScript object).
// --
class Slot {
  type: string;
  inputs: Array<string>;
  source: string;
  value: any;
  isDirty: boolean;
  definition: Function;
  constructor() {
    this.type = "js";
    this.inputs = [];
    this.source = "";
    this.value = undefined;
    this.isDirty = false;
    this.definition = () => undefined;
  }
}

// --
// The `Kernel` is the implementation of the Cells kernel protocol. It wraps basic
// operations around slots and exposes them through an API.
// --
class Kernel {
  sessions: Map<string, Session>;
  constructor() {
    this.sessions = new Map();
  }
  handle(method: string, args: Array<any>): any {
    switch (method) {
      case "set":
        // 0:SESSION 1:SLOT 2:INPUTS 3:SOURCE 4:TYPE
        return this.set(args[0], args[1], args[2], args[3], args[4]);
      case "get":
        // 0:SESSION 1:SLOT
        return this.get(args[0], args[1]);
      case "invalidate":
        // 0:SESSION 1:SLOTS
        return this.invalidate(args[0], args[1]);
      case "clear":
        // 0:SESSION 1:SLOTS?
        return this.clear(args[0], args[1]);
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
  hasSlot(session: string, slot: string): boolean {
    const s = this.sessions.get(session);
    return s ? s.slots.has(slot) : false;
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
  clear(session: string, slots?: Array<string>) {
    if (!slots || slots.length == 0) {
      this.sessions.delete(session);
    } else {
      const sessionSlots = this.getSession(session).slots;
      slots.forEach((s) => sessionSlots.delete(s));
    }
  }
  set(
    session: string,
    slot: string,
    inputs: Array<string>,
    source: string,
    type: string = "js",
  ): Slot {
    const s = this.getSlot(session, slot);
    s.type = type;
    s.inputs = inputs.map((_) => _);
    s.source = source;
    s.isDirty = true;
    this.defineSlot(session, slot);
    return s;
  }

  get(session: string, slot: string): any {
    if (!this.hasSlot(session, slot)) {
      throw new Error(`Undefined slot: '${session}.${slot}'`);
    }
    const s = this.getSlot(session, slot);
    if (s.isDirty) {
      s.value = this.evalSlot(session, slot);
      s.isDirty = false;
    }
    return s.value;
  }

  invalidate(session: string, slots: Array<string>): boolean {
    return true;
  }

  defineSlot(session: string, slot: string) {
    const s = this.getSlot(session, slot);
    // TODO: We'll need to do a bit of parsing of the source there
    // and extract the result.
    return new Function(
      `return function(${
        s.inputs.join(",")
      }){let ${slot}=undefined;${s.source}\n;return ${slot}}`,
    )();
  }

  evalSlot(session: string, slot: string): any {
    const s = this.getSlot(session, slot);
    const args = s.inputs.map((k) => this.get(session, k));
    return s.definition ? s.definition.apply(s, args) : undefined;
  }
}

// --
// The default way of interacting with Cells kernels is through *JSON RPC*, the `JSONRPCMessage`
// defines a simple type to capture the payload, which looks like `{jsonprc,method,params,id}`
// --
interface JSONRPCMessage {
  jsonrpc: string;
  method: string;
  params: Object;
  id: string;
}

interface JSONRPCResponse {
  jsonrpc: string;
  id: string;
  value: Object;
}

// --
// The JSON RPC adapter wraps a kernel and translates `JSONRPCMessages` into
// `Kernel` API calls.
// --
// TODO: Just like with the Python API, we should split the server as well, so that we have
// a pipe mode as well as a socket mode.
class JSONRPCAdapter {
  kernel: Kernel;
  constructor(kernel: Kernel = new Kernel()) {
    this.kernel = kernel;
  }
  // Unpacks the JSON RPC message and passes it to the kernel interface.
  handle(message: JSONRPCMessage) {
    const { jsonrpc, method, params, id } = message;
    // TODO: Type checking should happen there, to make sure that the method
    // is defined and that the params are what is expected.
    let result = undefined;
    try {
      result = this.kernel.handle(
        method,
        Object.entries(params || {}).map(([_, v]) => v),
      );
    } catch (e) {
      console.error("Could not handle RPC message", message, ":", e);
    }
    return { jsonrpc: jsonrpc || "2.0", id, result };
  }

  async serve(hostname = "localhost", port = 8000) {
    console.log(`Listening on ${hostname}:${port}`);
    const listener = Deno.listen({ hostname, port });
    for await (const conn of listener) {
      const buffer = new Uint8Array(256_000);
      const strdec = new TextDecoder();
      const strenc = new TextEncoder();
      // FIXME: That only works for a single connection
      while (true) {
        const n = await conn.read(buffer);
        if (n === null) {
          break;
        } else if (n === 0) {
          console.log("End of input");
        } else {
          const s = strdec.decode(buffer).substring(0, n);
          if (n === buffer.length) {
            console.error("Maximum message size reached");
          } else {
            let value = undefined;
            try {
              value = JSON.parse(s);
            } catch (e) {
              console.error(`Cannot parse JSON, ${e}: '${s}'`);
            }
            console.log("Handling RPC message", value, typeof (value));
            const result = this.handle(value);
            console.log("→", result);
            await conn.write(strenc.encode(JSON.stringify(result)));
          }
        }
      }
    }
  }
}

// TODO: This should be only when the kernel is started as a main
// script
await new JSONRPCAdapter().serve();

// EOF
