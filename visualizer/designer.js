"use strict";

const svgNS = "http://www.w3.org/2000/svg";
const graph = document.querySelector("#graph");
const viewport = document.querySelector("#viewport");
const editor = document.querySelector("#editor");
const errorsEl = document.querySelector("#errors");
const validationEl = document.querySelector("#validation");
const summaryEl = document.querySelector("#summary");
const routeItems = document.querySelector("#route-items");
const linkPrompt = document.querySelector("#link-prompt");
const undoButton = document.querySelector("#undo");
const redoButton = document.querySelector("#redo");
const previewButton = document.querySelector("#preview");
const downloadButton = document.querySelector("#download");
const yamlDialog = document.querySelector("#yaml-dialog");
const yamlPreview = document.querySelector("#yaml-preview");

let schema;
let definitions;
let manifest;
let digest;
let draft = blankDraft();
let positions = {};
let selected = null;
let history = [];
let future = [];
let valid = false;
let validationTimer;
let validationSequence = 0;
let linkMode = false;
let linkStart = null;
let routeBuild = null;
let view = { x: 0, y: 0, scale: 1 };
let panState = null;
let nodeDrag = null;
let suppressGraphClick = false;

function blankDraft() {
  return {
    publishers: {},
    subscribers: {},
    routers: {},
    switches: {},
    links: [],
  };
}

function clone(value) {
  return structuredClone(value);
}

function snapshot() {
  return { draft: clone(draft), positions: clone(positions), selected: clone(selected) };
}

function restore(value) {
  draft = value.draft;
  positions = value.positions;
  selected = value.selected;
  renderAll();
  scheduleValidation();
  saveDraft();
}

function commit(change) {
  history.push(snapshot());
  if (history.length > 100) history.shift();
  future = [];
  change();
  renderAll();
  scheduleValidation();
  saveDraft();
}

function undo() {
  if (!history.length) return;
  future.push(snapshot());
  restore(history.pop());
}

function redo() {
  if (!future.length) return;
  history.push(snapshot());
  restore(future.pop());
}

function saveDraft() {
  if (!digest) return;
  localStorage.setItem(`quiclab-designer:${digest}`, JSON.stringify({ draft, positions }));
}

function resolveSchema(value) {
  let current = value || {};
  while (current.$ref) {
    current = definitions[current.$ref.split("/").pop()] || {};
  }
  if (current.anyOf) {
    const nonNull = current.anyOf.find((part) => part.type !== "null") || current.anyOf[0];
    return { ...resolveSchema(nonNull), default: current.default, nullable: true };
  }
  return current;
}

function schemaDefault(rawSchema) {
  const spec = resolveSchema(rawSchema);
  if (spec.default !== undefined && spec.default !== null) return clone(spec.default);
  if (spec.type === "object" || spec.properties) {
    const value = {};
    for (const [name, child] of Object.entries(spec.properties || {})) {
      const childDefault = schemaDefault(child);
      if (childDefault !== undefined) value[name] = childDefault;
    }
    return value;
  }
  return undefined;
}

function deepMerge(base, override) {
  const result = clone(base || {});
  for (const [name, value] of Object.entries(override || {})) {
    if (value && typeof value === "object" && !Array.isArray(value)
        && result[name] && typeof result[name] === "object" && !Array.isArray(result[name])) {
      result[name] = deepMerge(result[name], value);
    } else {
      result[name] = clone(value);
    }
  }
  return result;
}

function effectiveDefaults() {
  return deepMerge(schemaDefault(schema.properties.defaults), draft.defaults || {});
}

function inheritedNodeValues() {
  return {};
}

function fieldTitle(name, fieldSchema) {
  return fieldSchema.title || name.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function renderObjectEditor(container, rawSchema, value, onReplace, options = {}) {
  const objectSchema = resolveSchema(rawSchema);
  const required = new Set(objectSchema.required || []);
  const common = document.createElement("div");
  const advanced = document.createElement("details");
  const advancedSummary = document.createElement("summary");
  advancedSummary.textContent = "Advanced attributes";
  advanced.append(advancedSummary);
  let advancedCount = 0;

  for (const [name, rawFieldSchema] of Object.entries(objectSchema.properties || {})) {
    if ((options.skip || []).includes(name)) continue;
    const fieldSchema = resolveSchema(rawFieldSchema);
    const fieldRequired = required.has(name) || options.alwaysSet?.includes(name);
    const target = fieldRequired || (fieldSchema.default !== undefined && fieldSchema.default !== null) || options.common?.includes(name)
      ? common
      : advanced;
    if (target === advanced) advancedCount += 1;
    target.append(renderField(name, rawFieldSchema, value?.[name], fieldRequired, (next, unset) => {
      const updated = clone(value || {});
      if (unset) delete updated[name];
      else updated[name] = next;
      onReplace(updated);
    }, options.inherited?.[name]));
  }
  container.append(common);
  if (advancedCount) container.append(advanced);
}

// Free-form maps and object lists have no form layout; edit them as JSON and
// let server-side validation report schema errors.
function isJsonField(spec) {
  const freeMap = spec.type === "object" && !spec.properties
    && spec.additionalProperties && typeof spec.additionalProperties === "object";
  const objectList = spec.type === "array" && resolveSchema(spec.items || {}).type === "object";
  return freeMap || objectList;
}

function renderJsonField(wrapper, spec, current, required, onChange) {
  const input = document.createElement("textarea");
  input.rows = 6;
  input.spellcheck = false;
  input.value = current === undefined || current === null ? "" : JSON.stringify(current, null, 2);
  input.placeholder = spec.type === "array" ? "JSON list, e.g. [{...}]" : "JSON object, e.g. {\"key\": ...}";
  input.addEventListener("change", () => {
    input.setCustomValidity("");
    if (!input.value.trim()) return required ? input.reportValidity() : onChange(undefined, true);
    try {
      const parsed = JSON.parse(input.value);
      const expectsArray = spec.type === "array";
      if (Array.isArray(parsed) !== expectsArray || parsed === null || typeof parsed !== "object") {
        throw new Error(expectsArray ? "expected a JSON list" : "expected a JSON object");
      }
      onChange(parsed, false);
    } catch (error) {
      input.setCustomValidity(error.message);
      input.reportValidity();
    }
  });
  wrapper.append(input);
  return wrapper;
}

function renderField(name, rawSchema, current, required, onChange, inherited) {
  const spec = resolveSchema(rawSchema);
  const wrapper = document.createElement("div");
  wrapper.className = "field";
  const label = document.createElement("label");
  label.textContent = `${fieldTitle(name, spec)}${required ? " *" : ""}`;
  wrapper.append(label);

  if (isJsonField(spec)) return renderJsonField(wrapper, spec, current, required, onChange);

  if (spec.type === "object" || spec.properties) {
    const fieldset = document.createElement("fieldset");
    const legend = document.createElement("legend");
    legend.textContent = fieldTitle(name, spec);
    fieldset.append(legend);
    const enabled = current !== undefined && current !== null;
    if (!required) {
      const toggleLabel = document.createElement("label");
      toggleLabel.className = "inline";
      const toggle = document.createElement("input");
      toggle.type = "checkbox";
      toggle.checked = enabled;
      toggle.addEventListener("change", () => onChange(toggle.checked ? {} : undefined, !toggle.checked));
      const inheritedText = inherited === undefined ? "" : `: ${JSON.stringify(inherited)}`;
      toggleLabel.append(toggle, document.createTextNode(`Override${enabled ? "" : ` inherited${inheritedText}`}`));
      fieldset.append(toggleLabel);
    }
    if (required || enabled) {
      renderObjectEditor(fieldset, spec, current || {}, (next) => onChange(next, false), { inherited });
    }
    wrapper.replaceChildren(fieldset);
    return wrapper;
  }

  if (spec.type === "array") {
    const input = document.createElement("textarea");
    input.rows = 2;
    input.value = Array.isArray(current) ? current.join(", ") : Array.isArray(inherited) ? inherited.join(", ") : "";
    input.placeholder = "Comma-separated values";
    input.addEventListener("change", () => {
      if (!input.value.trim() && !required) return onChange(undefined, true);
      const itemSpec = resolveSchema(spec.items || {});
      const items = input.value.split(",").map((item) => item.trim()).filter(Boolean).map((item) => {
        return itemSpec.type === "number" ? Number(item) : itemSpec.type === "integer" ? Number.parseInt(item, 10) : item;
      });
      onChange(items, false);
    });
    wrapper.append(input);
    return wrapper;
  }

  if (spec.type === "boolean") {
    const select = document.createElement("select");
    if (!required) select.append(new Option(inherited === undefined ? "Inherit / unset" : `Inherit (${inherited})`, ""));
    select.append(new Option("true", "true"), new Option("false", "false"));
    select.value = current === undefined || current === null ? "" : String(current);
    select.addEventListener("change", () => {
      if (select.value === "") onChange(undefined, true);
      else onChange(select.value === "true", false);
    });
    wrapper.append(select);
    return wrapper;
  }

  if (spec.enum || spec.const !== undefined) {
    const select = document.createElement("select");
    if (!required && spec.const === undefined) select.append(new Option(inherited === undefined ? "Inherit / unset" : `Inherit (${inherited})`, ""));
    const values = spec.enum || [spec.const];
    for (const item of values) select.append(new Option(String(item), String(item)));
    select.value = current ?? inherited ?? spec.default ?? "";
    select.addEventListener("change", () => {
      if (select.value === "") onChange(undefined, true);
      else onChange(select.value, false);
    });
    wrapper.append(select);
    return wrapper;
  }

  const input = document.createElement("input");
  input.type = spec.type === "integer" || spec.type === "number" ? "number" : "text";
  if (spec.type === "number") input.step = "any";
  if (spec.minimum !== undefined) input.min = spec.minimum;
  if (spec.exclusiveMinimum !== undefined) input.min = spec.exclusiveMinimum;
  if (spec.maximum !== undefined) input.max = spec.maximum;
  if (spec.minLength !== undefined) input.minLength = spec.minLength;
  if (spec.maxLength !== undefined) input.maxLength = spec.maxLength;
  if (spec.pattern) input.pattern = spec.pattern;
  input.value = current ?? inherited ?? "";
  if (current === undefined && inherited !== undefined) input.title = `Inherited value: ${inherited}`;
  else if (spec.default !== undefined) input.placeholder = `Default: ${spec.default}`;
  input.required = required;
  input.addEventListener("change", () => {
    if (input.value === "" && !required) return onChange(undefined, true);
    const next = spec.type === "number" ? Number(input.value)
      : spec.type === "integer" ? Number.parseInt(input.value, 10)
      : input.value;
    onChange(next, false);
  });
  wrapper.append(input);
  if (current === undefined && inherited !== undefined) {
    const help = document.createElement("small");
    help.textContent = "Inherited default; exported only when changed.";
    wrapper.append(help);
  }
  if (spec.description) {
    const help = document.createElement("small");
    help.textContent = spec.description;
    wrapper.append(help);
  }
  return wrapper;
}

function allNodes() {
  const nodes = [];
  for (const [role, property] of [["router", "routers"], ["switch", "switches"], ["publisher", "publishers"], ["subscriber", "subscribers"]]) {
    for (const id of Object.keys(draft[property] || {})) nodes.push({ id, role });
  }
  for (const endpoint of ["sender", "receiver"]) {
    for (const value of draft.traffic?.[`${endpoint}s`] || []) {
      nodes.push({ id: value.id, role: `traffic-${endpoint}` });
    }
  }
  return nodes;
}

function nodeExists(id) {
  return allNodes().some((node) => node.id === id);
}

function nextId(prefix) {
  if (!nodeExists(prefix)) return prefix;
  let index = 1;
  while (nodeExists(`${prefix}-${index}`)) index += 1;
  return `${prefix}-${index}`;
}

function portEntries() {
  const entries = [];
  const add = (path, value) => {
    if (value !== undefined && value !== null && value !== "") entries.push({ path, value: Number(value) });
  };
  for (const [id, publisher] of Object.entries(draft.publishers || {})) {
    add(`publishers.${id}.listen_port`, publisher.listen_port);
  }
  if (draft.traffic) {
    const traffic = effectiveDefaults().traffic;
    add("defaults.traffic.base_port", traffic.base_port);
  }
  return entries;
}

function portCollisionErrors() {
  const byPort = new Map();
  for (const entry of portEntries()) {
    if (!byPort.has(entry.value)) byPort.set(entry.value, []);
    byPort.get(entry.value).push(entry.path);
  }
  const errors = [];
  for (const [port, entries] of byPort) {
    if (entries.length > 1) {
      errors.push({ loc: entries, message: `port ${port} collides across ${entries.join(", ")}` });
    }
  }
  return errors;
}

function allocatePort(preferred) {
  const used = new Set(portEntries().map((entry) => entry.value));
  let port = preferred;
  while (used.has(port) && port <= 65535) port += 1;
  if (port > 65535) throw new Error("No free service port remains.");
  return port;
}

function availableTrafficDefaults() {
  const current = effectiveDefaults().traffic;
  const used = new Set(portEntries().map((entry) => entry.value));
  const next = (preferred) => {
    let port = preferred;
    while (used.has(port) && port <= 65535) port += 1;
    if (port > 65535) throw new Error("No free traffic port remains.");
    used.add(port);
    return port;
  };
  return { base_port: next(current.base_port) };
}

function firstPublisher() {
  return Object.keys(draft.publishers || {})[0] || "";
}

function nodeDefaults(role) {
  if (role === "router") return { id: nextId("router"), config: {} };
  if (role === "switch") return { id: nextId("switch"), config: {} };
  if (role === "publisher") {
    return { id: nextId("pub"), config: { listen_port: allocatePort(4433), cc_algo: "bbr" } };
  }
  if (role === "subscriber") {
    return { id: nextId("sub"), config: { connects_to: firstPublisher(), rate_kbps: 2500 } };
  }
  if (role === "traffic-sender") return { id: nextId("traffic-tx"), config: {} };
  return { id: nextId("traffic-rx"), config: {} };
}

function addNode(role, point) {
  const endpoint = role.startsWith("traffic-") ? role.slice(8) : null;
  const trafficDefaults = endpoint && !draft.traffic ? availableTrafficDefaults() : null;
  const value = nodeDefaults(role);
  commit(() => {
    if (endpoint) {
      if (trafficDefaults) {
        draft.defaults ||= {};
        draft.defaults.traffic = trafficDefaults;
      }
      draft.traffic ||= { routes: {} };
      (draft.traffic[`${endpoint}s`] ||= []).push({ id: value.id });
    } else {
      const property = propertyForRole(role);
      draft[property] ||= {};
      draft[property][value.id] = value.config;
    }
    positions[value.id] = point || nextCanvasPosition();
    selected = { kind: "node", role, id: value.id };
  });
}

function nextCanvasPosition() {
  const count = allNodes().length;
  return { x: 130 + (count % 5) * 190, y: 120 + Math.floor(count / 5) * 150 };
}

function propertyForRole(role) {
  return role === "switch" ? "switches" : `${role}s`;
}

function nodeConfig(role, id) {
  if (role.startsWith("traffic-")) return draft.traffic?.[`${role.slice(8)}s`]?.find((endpoint) => endpoint.id === id);
  return draft[propertyForRole(role)]?.[id];
}

function normalizedNodeConfig(role, next) {
  return clone(next);
}

function nodeDefinition(role) {
  if (role.startsWith("traffic-")) return definitions.TrafficEndpointConfig;
  return definitions[manifest.nodeCollections[role].definition];
}

function renameNode(role, oldId, newId) {
  newId = newId.trim();
  if (!newId || (newId !== oldId && nodeExists(newId))) {
    alert("Node id must be non-empty and globally unique.");
    renderInspector();
    return;
  }
  if (newId === oldId) return;
  commit(() => {
    if (role.startsWith("traffic-")) {
      nodeConfig(role, oldId).id = newId;
    } else {
      const property = propertyForRole(role);
      const replaced = {};
      for (const [id, value] of Object.entries(draft[property])) replaced[id === oldId ? newId : id] = value;
      draft[property] = replaced;
    }
    for (const item of Object.values(draft.subscribers || {})) {
      if (item.connects_to === oldId) item.connects_to = newId;
    }
    for (const link of draft.links || []) {
      if (link.from === oldId) link.from = newId;
      if (link.to === oldId) link.to = newId;
    }
    for (const route of Object.values(draft.traffic?.routes || {})) {
      route.path = route.path.map((id) => id === oldId ? newId : id);
    }
    positions[newId] = positions[oldId] || nextCanvasPosition();
    delete positions[oldId];
    selected.id = newId;
  });
}

function nodeReferences(id) {
  const refs = [];
  for (const [sid, sub] of Object.entries(draft.subscribers || {})) if (sub.connects_to === id) refs.push(`subscriber ${sid}`);
  for (const [name, route] of Object.entries(draft.traffic?.routes || {})) if (route.path.includes(id)) refs.push(`traffic route ${name}`);
  return refs;
}

function deleteNode(role, id) {
  const refs = nodeReferences(id);
  if (refs.length) {
    alert(`Cannot delete ${id}; referenced by ${refs.join(", ")}. Rewire first.`);
    return;
  }
  const attached = (draft.links || []).filter((link) => link.from === id || link.to === id).length;
  if (!confirm(`Delete ${id}${attached ? ` and ${attached} attached link(s)` : ""}?`)) return;
  commit(() => {
    if (role.startsWith("traffic-")) {
      const endpoints = draft.traffic[`${role.slice(8)}s`];
      endpoints.splice(endpoints.findIndex((endpoint) => endpoint.id === id), 1);
    } else delete draft[propertyForRole(role)][id];
    if (draft.traffic && !draft.traffic.senders?.length && !draft.traffic.receivers?.length
        && !Object.keys(draft.traffic.routes || {}).length) {
      delete draft.traffic;
    }
    draft.links = (draft.links || []).filter((link) => link.from !== id && link.to !== id);
    delete positions[id];
    selected = null;
  });
}

function duplicateNodes(role, id, count) {
  const source = clone(nodeConfig(role, id));
  const copyLinks = ["publisher", "subscriber"].includes(role) && confirm("Copy incident physical links too?");
  commit(() => {
    for (let index = 0; index < count; index += 1) {
      const newId = nextId(id.replace(/-\d+$/, ""));
      const config = clone(source);
      if (role === "publisher") config.listen_port = allocatePort(config.listen_port || 4433);
      if (role.startsWith("traffic-")) {
        config.id = newId;
        draft.traffic[`${role.slice(8)}s`].push(config);
      } else draft[propertyForRole(role)][newId] = config;
      const origin = positions[id] || nextCanvasPosition();
      positions[newId] = { x: origin.x + 45 * (index + 1), y: origin.y + 45 * (index + 1) };
      if (copyLinks) {
        for (const link of [...draft.links]) {
          if (link.from !== id && link.to !== id) continue;
          const copied = clone(link);
          if (copied.from === id) copied.from = newId;
          if (copied.to === id) copied.to = newId;
          draft.links.push(copied);
        }
      }
      selected = { kind: "node", role, id: newId };
    }
  });
}

function canonicalPair(a, b) {
  return [a, b].sort().join("\0");
}

function addPhysicalLink(a, b) {
  if (a === b) { alert("Link endpoints must differ."); return false; }
  if ((draft.links || []).some((link) => canonicalPair(link.from, link.to) === canonicalPair(a, b))) {
    alert("Physical link already exists.");
    return false;
  }
  commit(() => {
    draft.links ||= [];
    draft.links.push({ from: a, to: b });
    selected = { kind: "link", index: draft.links.length - 1 };
    linkStart = null;
  });
  return true;
}

function linkUsedByRoute(link) {
  const wanted = canonicalPair(link.from, link.to);
  for (const [name, route] of Object.entries(draft.traffic?.routes || {})) {
    for (let index = 0; index + 1 < route.path.length; index += 1) {
      if (canonicalPair(route.path[index], route.path[index + 1]) === wanted) return name;
    }
  }
  return null;
}

function deleteLink(index) {
  const route = linkUsedByRoute(draft.links[index]);
  if (route) return alert(`Link is used by traffic route ${route}. Change route first.`);
  if (!confirm("Delete physical link?")) return;
  commit(() => {
    draft.links.splice(index, 1);
    selected = null;
  });
}

function defaultTrafficEndpoints() {
  const senders = (draft.traffic?.senders || []).filter((endpoint) =>
    selected?.kind !== "node" || selected.role !== "traffic-sender" || selected.id === endpoint.id);
  const receivers = (draft.traffic?.receivers || []).filter((endpoint) =>
    selected?.kind !== "node" || selected.role !== "traffic-receiver" || selected.id === endpoint.id);
  for (const sender of senders) {
    for (const receiver of receivers) {
      if (shortestTrafficPath(sender.id, receiver.id)) return [sender.id, receiver.id];
    }
  }
  return [senders[0]?.id, receivers[0]?.id];
}

function shortestTrafficPath(...endpoints) {
  const [sender, receiver] = endpoints.length ? endpoints : defaultTrafficEndpoints();
  if (!sender || !receiver) return null;
  const allowed = new Set([
    sender,
    receiver,
    ...Object.keys(draft.routers || {}),
    ...Object.keys(draft.switches || {}),
  ]);
  const adjacency = new Map();
  for (const link of draft.links || []) {
    if (!allowed.has(link.from) || !allowed.has(link.to)) continue;
    if (!adjacency.has(link.from)) adjacency.set(link.from, []);
    if (!adjacency.has(link.to)) adjacency.set(link.to, []);
    adjacency.get(link.from).push(link.to);
    adjacency.get(link.to).push(link.from);
  }
  const queue = [[sender]];
  const seen = new Set([sender]);
  while (queue.length) {
    const path = queue.shift();
    const last = path[path.length - 1];
    if (last === receiver) return path.length >= 3 ? path : null;
    for (const next of (adjacency.get(last) || []).sort()) {
      if (!seen.has(next)) {
        seen.add(next);
        queue.push([...path, next]);
      }
    }
  }
  return null;
}

function appendRouteNode(id) {
  const route = draft.traffic?.routes?.[routeBuild];
  if (!route) { routeBuild = null; return; }
  const returnSelection = { kind: "route", name: routeBuild };
  const receiver = draft.traffic.receivers?.some((endpoint) => endpoint.id === id);
  if (draft.traffic.senders?.some((endpoint) => endpoint.id === id)) {
    commit(() => { route.path = [id]; selected = returnSelection; });
    linkPrompt.textContent = "Route reset. Select connected router or switch.";
    return;
  }
  const last = route.path[route.path.length - 1];
  const linked = (draft.links || []).some((link) => canonicalPair(link.from, link.to) === canonicalPair(last, id));
  if (!linked) return alert(`${id} is not physically linked to ${last}.`);
  if (route.path.includes(id)) return alert("Traffic route cannot repeat a node.");
  const intermediate = id in (draft.routers || {}) || id in (draft.switches || {});
  if (!receiver && !intermediate) return alert("Intermediate traffic nodes must be routers or switches.");
  if (receiver && route.path.length < 2) return alert("Route needs at least one intermediate node.");
  commit(() => { route.path.push(id); selected = returnSelection; });
  if (receiver) {
    routeBuild = null;
    linkPrompt.textContent = "Traffic route complete.";
  } else {
    linkPrompt.textContent = `Route ends at ${id}. Select connected router, switch, or receiver.`;
  }
}

function addRoute() {
  if (!draft.traffic?.senders?.length || !draft.traffic?.receivers?.length) return alert("Add traffic sender and receiver first.");
  let name = "route";
  let index = 1;
  while (draft.traffic.routes?.[name]) name = `route-${index++}`;
  const path = shortestTrafficPath() || defaultTrafficEndpoints();
  commit(() => {
    draft.traffic.routes ||= {};
    draft.traffic.routes[name] = { path };
    selected = { kind: "route", name };
  });
}

function renameRoute(oldName, newName) {
  newName = newName.trim();
  if (!newName || (newName !== oldName && draft.traffic.routes[newName])) return alert("Route name must be unique.");
  if (newName === oldName) return;
  commit(() => {
    const routes = {};
    for (const [name, route] of Object.entries(draft.traffic.routes)) routes[name === oldName ? newName : name] = route;
    draft.traffic.routes = routes;
    selected.name = newName;
  });
}

function deleteRoute(name) {
  if (!confirm(`Delete route ${name}?`)) return;
  commit(() => {
    delete draft.traffic.routes[name];
    selected = null;
  });
}

function autoLayout(pushHistory = true) {
  const action = () => {
    const groups = { publisher: 0, "traffic-sender": 0, router: 1, switch: 2, subscriber: 3, "traffic-receiver": 3 };
    const rows = new Map();
    for (const node of allNodes()) {
      const column = groups[node.role] ?? 1;
      const row = rows.get(column) || 0;
      positions[node.id] = { x: 130 + column * 240, y: 110 + row * 130 };
      rows.set(column, row + 1);
    }
  };
  if (pushHistory) commit(action);
  else action();
}

function renderGraph() {
  viewport.replaceChildren();
  for (const node of allNodes()) if (!positions[node.id]) positions[node.id] = nextCanvasPosition();
  const nodeMap = new Map(allNodes().map((node) => [node.id, node]));

  const applicationEdges = [];
  for (const [id, item] of Object.entries(draft.subscribers || {})) if (item.connects_to) applicationEdges.push([id, item.connects_to]);
  for (const [a, b] of applicationEdges) drawLine(a, b, "edge application");

  (draft.links || []).forEach((link, index) => {
    drawLine(link.from, link.to, `edge${selected?.kind === "link" && selected.index === index ? " selected" : ""}`, () => {
      selected = { kind: "link", index };
      renderAll();
    });
  });

  if (selected?.kind === "route") {
    const path = draft.traffic?.routes?.[selected.name]?.path || [];
    for (let index = 0; index + 1 < path.length; index += 1) drawLine(path[index], path[index + 1], "edge route");
  }

  for (const node of nodeMap.values()) drawNode(node);
  viewport.setAttribute("transform", `translate(${view.x} ${view.y}) scale(${view.scale})`);
}

function drawLine(aId, bId, className, onSelect) {
  const a = positions[aId];
  const b = positions[bId];
  if (!a || !b) return;
  if (onSelect) {
    const hit = document.createElementNS(svgNS, "line");
    setLine(hit, a, b);
    hit.setAttribute("class", "edge-hit");
    hit.addEventListener("click", (event) => { event.stopPropagation(); onSelect(); });
    viewport.append(hit);
  }
  const line = document.createElementNS(svgNS, "line");
  setLine(line, a, b);
  line.setAttribute("class", className);
  if (onSelect) line.addEventListener("click", (event) => { event.stopPropagation(); onSelect(); });
  viewport.append(line);
}

function setLine(line, a, b) {
  line.setAttribute("x1", a.x);
  line.setAttribute("y1", a.y);
  line.setAttribute("x2", b.x);
  line.setAttribute("y2", b.y);
}

function drawNode(node) {
  const point = positions[node.id];
  const group = document.createElementNS(svgNS, "g");
  group.setAttribute("class", `node ${node.role}${selected?.kind === "node" && selected.id === node.id ? " selected" : ""}`);
  group.setAttribute("transform", `translate(${point.x} ${point.y})`);
  group.setAttribute("tabindex", "0");
  group.setAttribute("role", "button");
  group.setAttribute("aria-label", `${node.role} ${node.id}`);
  group.dataset.nodeId = node.id;
  group.addEventListener("click", (event) => {
    event.stopPropagation();
    suppressGraphClick = false;
    if (routeBuild) {
      appendRouteNode(node.id);
      return;
    }
    if (linkMode) {
      if (!linkStart) {
        linkStart = node.id;
        linkPrompt.textContent = `First endpoint: ${linkStart}. Select second node.`;
      } else if (linkStart !== node.id) {
        if (addPhysicalLink(linkStart, node.id)) {
          linkMode = false;
          linkPrompt.textContent = "Physical link added.";
        }
      }
      return;
    }
    selected = { kind: "node", role: node.role, id: node.id };
    renderAll();
  });
  group.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      group.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    }
  });
  group.addEventListener("contextmenu", (event) => {
    event.preventDefault();
    event.stopPropagation();
    routeBuild = null;
    linkMode = true;
    linkStart = node.id;
    selected = { kind: "node", role: node.role, id: node.id };
    linkPrompt.textContent = `Connect ${node.id} to another node.`;
    renderAll();
  });
  group.addEventListener("pointerdown", (event) => startNodeDrag(event, node));
  const circle = document.createElementNS(svgNS, "circle");
  circle.setAttribute("r", "34");
  const id = document.createElementNS(svgNS, "text");
  id.setAttribute("y", "53");
  id.textContent = node.id;
  const role = document.createElementNS(svgNS, "text");
  role.setAttribute("class", "role");
  role.setAttribute("y", "69");
  role.textContent = node.role;
  group.append(circle, id, role);
  viewport.append(group);
}

function graphPoint(event) {
  const rect = graph.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left - view.x) / view.scale,
    y: (event.clientY - rect.top - view.y) / view.scale,
  };
}

function startNodeDrag(event, node) {
  if (event.button !== 0 || linkMode || routeBuild) return;
  event.stopPropagation();
  suppressGraphClick = true;
  selected = { kind: "node", role: node.role, id: node.id };
  renderInspector();
  for (const element of document.querySelectorAll(".node")) {
    element.classList.toggle("selected", element.dataset.nodeId === node.id);
  }
  history.push(snapshot());
  if (history.length > 100) history.shift();
  future = [];
  nodeDrag = { id: node.id, pointerId: event.pointerId };
  graph.setPointerCapture(event.pointerId);
}

graph.addEventListener("pointermove", (event) => {
  if (nodeDrag) {
    positions[nodeDrag.id] = graphPoint(event);
    renderGraph();
  } else if (panState) {
    view.x += event.clientX - panState.x;
    view.y += event.clientY - panState.y;
    panState = { x: event.clientX, y: event.clientY };
    renderGraph();
  }
});

graph.addEventListener("pointerup", (event) => {
  if (nodeDrag) {
    nodeDrag = null;
    saveDraft();
    updateHistoryButtons();
  }
  panState = null;
  graph.classList.remove("panning");
  if (graph.hasPointerCapture(event.pointerId)) graph.releasePointerCapture(event.pointerId);
});

graph.addEventListener("pointerdown", (event) => {
  if (event.target.closest?.(".node, .edge, .edge-hit") || event.button !== 0) return;
  panState = { x: event.clientX, y: event.clientY };
  graph.setPointerCapture(event.pointerId);
  graph.classList.add("panning");
});

graph.addEventListener("wheel", (event) => {
  event.preventDefault();
  view.scale = Math.max(.3, Math.min(3, view.scale * (event.deltaY < 0 ? 1.12 : 1 / 1.12)));
  renderGraph();
}, { passive: false });

graph.addEventListener("dragover", (event) => event.preventDefault());
graph.addEventListener("drop", (event) => {
  event.preventDefault();
  const role = event.dataTransfer.getData("text/quiclab-role");
  if (role) addNode(role, graphPoint(event));
});

graph.addEventListener("click", () => {
  if (suppressGraphClick) {
    suppressGraphClick = false;
    return;
  }
  if (routeBuild) {
    routeBuild = null;
    linkPrompt.textContent = "Route building cancelled.";
  } else if (linkMode) {
    linkMode = false;
    linkStart = null;
    linkPrompt.textContent = "Link creation cancelled.";
  } else {
    selected = null;
    renderAll();
  }
});

function renderInspector() {
  editor.replaceChildren();
  if (!selected) {
    const title = document.createElement("h2");
    title.textContent = "Inspector";
    const text = document.createElement("p");
    text.textContent = "Select node, link, route, defaults, or startup.";
    editor.append(title, text);
    return;
  }
  if (selected.kind === "global") return renderGlobalInspector();
  if (selected.kind === "node") return renderNodeInspector();
  if (selected.kind === "link") return renderLinkInspector();
  if (selected.kind === "route") return renderRouteInspector();
}

function heading(text) {
  const title = document.createElement("h2");
  title.textContent = text;
  editor.append(title);
}

function idField(labelText, value, onChange) {
  const wrapper = document.createElement("div");
  wrapper.className = "field";
  const label = document.createElement("label");
  label.textContent = labelText;
  const input = document.createElement("input");
  input.value = value;
  input.required = true;
  input.addEventListener("change", () => onChange(input.value));
  wrapper.append(label, input);
  editor.append(wrapper);
}

function renderNodeInspector() {
  const { role, id } = selected;
  const config = nodeConfig(role, id);
  if (!config) { selected = null; return renderInspector(); }
  heading(`${role} node`);
  idField("Node id", id, (next) => renameNode(role, id, next));
  const relationship = manifest.relationships[role];
  if (relationship) {
    const wrapper = document.createElement("div");
    wrapper.className = "field";
    const label = document.createElement("label");
    label.textContent = fieldTitle(relationship, {});
    const select = document.createElement("select");
    select.append(new Option("Select publisher", ""));
    for (const publisherId of Object.keys(draft.publishers || {})) {
      select.append(new Option(publisherId, publisherId));
    }
    select.value = config[relationship] || "";
    select.addEventListener("change", () => commit(() => {
      config[relationship] = select.value;
    }));
    wrapper.append(label, select);
    editor.append(wrapper);
  }
  const commonFields = role === "publisher"
    ? ["cc_algo", "listen_port", "ladder_kbps", "fps", "gop_ms"]
    : role === "subscriber"
      ? ["rate_kbps", "phase_ms", "buffer_ms"]
      : role === "router" ? ["queue_metrics"] : [];
  renderObjectEditor(editor, nodeDefinition(role), config, (next) => commit(() => {
    if (role.startsWith("traffic-")) {
      const endpoints = draft.traffic[`${role.slice(8)}s`];
      endpoints[endpoints.findIndex((endpoint) => endpoint.id === id)] = next;
    } else draft[propertyForRole(role)][id] = normalizedNodeConfig(role, next);
  }), {
    skip: [
      ...(role.startsWith("traffic-") ? ["id"] : []),
      ...(relationship ? [relationship] : []),
    ],
    common: commonFields,
    alwaysSet: [],
    inherited: inheritedNodeValues(),
  });
  const actions = document.createElement("div");
  actions.className = "inspector-actions";
  const duplicate = document.createElement("button");
  duplicate.textContent = "Duplicate";
  duplicate.addEventListener("click", () => duplicateNodes(role, id, 1));
  const bulk = document.createElement("button");
  bulk.textContent = "Bulk add";
  bulk.addEventListener("click", () => {
    const count = Number.parseInt(prompt("Number of copies", "10"), 10);
    if (Number.isInteger(count) && count > 0 && (count <= 500 || confirm(`Create ${count} nodes?`))) duplicateNodes(role, id, count);
  });
  actions.append(duplicate, bulk);
  const remove = document.createElement("button");
  remove.className = "danger";
  remove.textContent = "Delete";
  remove.addEventListener("click", () => deleteNode(role, id));
  actions.append(remove);
  editor.append(actions);
}

function renderGlobalInspector() {
  const property = selected.property;
  const propertySchema = resolveSchema(schema.properties[property]);
  heading(fieldTitle(property, propertySchema));
  if (propertySchema.type === "array") {
    editor.append(renderField(property, schema.properties[property], draft[property], false, (next, unset) => commit(() => {
      if (unset) delete draft[property];
      else draft[property] = next;
    })));
    return;
  }
  const value = draft[property] || {};
  const fields = Object.keys(resolveSchema(schema.properties[property]).properties || {});
  renderObjectEditor(editor, schema.properties[property], value, (next) => commit(() => { draft[property] = next; }), {
    common: fields,
    inherited: schemaDefault(schema.properties[property]),
  });
}

function nodeOptions(select, selectedValue) {
  select.append(new Option("Select node", ""));
  for (const node of allNodes()) select.append(new Option(`${node.id} (${node.role})`, node.id));
  select.value = selectedValue;
}

function renderLinkInspector() {
  const index = selected.index;
  const link = draft.links?.[index];
  if (!link) { selected = null; return renderInspector(); }
  heading("Physical link");
  for (const side of ["from", "to"]) {
    const wrapper = document.createElement("div");
    wrapper.className = "field";
    const label = document.createElement("label");
    label.textContent = side;
    const select = document.createElement("select");
    nodeOptions(select, link[side]);
    select.addEventListener("change", () => {
      const other = side === "from" ? link.to : link.from;
      if (!select.value || select.value === other) return renderInspector();
      const duplicate = draft.links.some((item, otherIndex) => otherIndex !== index && canonicalPair(item.from, item.to) === canonicalPair(select.value, other));
      if (duplicate) { alert("Physical link already exists."); return renderInspector(); }
      commit(() => { draft.links[index][side] = select.value; });
    });
    wrapper.append(label, select);
    editor.append(wrapper);
  }
  const actions = document.createElement("div");
  actions.className = "inspector-actions";
  const swap = document.createElement("button");
  swap.textContent = "Swap direction";
  swap.addEventListener("click", () => commit(() => {
    [link.from, link.to] = [link.to, link.from];
  }));
  const remove = document.createElement("button");
  remove.className = "danger";
  remove.textContent = "Delete link";
  remove.addEventListener("click", () => deleteLink(index));
  actions.append(swap, remove);
  editor.append(actions);
}

function renderTrafficEndpoints(parent, route) {
  for (const [role, index] of [["sender", 0], ["receiver", -1]]) {
    const wrapper = document.createElement("div");
    wrapper.className = "field";
    const label = document.createElement("label");
    label.textContent = fieldTitle(role, {});
    const select = document.createElement("select");
    select.append(new Option(`Select ${role}`, ""));
    for (const endpoint of draft.traffic[`${role}s`] || []) select.append(new Option(endpoint.id, endpoint.id));
    select.value = route.path.at(index) || "";
    select.addEventListener("change", () => {
      if (!select.value) return;
      const sender = role === "sender" ? select.value : route.path[0];
      const receiver = role === "receiver" ? select.value : route.path.at(-1);
      commit(() => { route.path = shortestTrafficPath(sender, receiver) || [sender, receiver]; });
    });
    wrapper.append(label, select);
    parent.append(wrapper);
  }
}

function renderRouteInspector() {
  const name = selected.name;
  const route = draft.traffic?.routes?.[name];
  if (!route) { selected = null; return renderInspector(); }
  heading("Traffic route");
  idField("Route name", name, (next) => renameRoute(name, next));
  renderTrafficEndpoints(editor, route);
  editor.append(renderField("path", definitions.TrafficRouteConfig.properties.path, route.path, true, (next) => commit(() => { route.path = next; })));
  const actions = document.createElement("div");
  actions.className = "inspector-actions";
  const shortest = document.createElement("button");
  shortest.textContent = "Shortest router path";
  shortest.addEventListener("click", () => {
    const path = shortestTrafficPath(route.path[0], route.path.at(-1));
    if (!path) return alert("No sender-to-receiver path through routers exists.");
    commit(() => { route.path = path; });
  });
  const build = document.createElement("button");
  build.textContent = "Build on canvas";
  build.addEventListener("click", () => {
    const sender = route.path[0] || draft.traffic?.senders?.[0]?.id;
    if (!sender) return alert("Traffic sender missing.");
    routeBuild = name;
    linkMode = false;
    linkStart = null;
    commit(() => { route.path = [sender]; selected = { kind: "route", name }; });
    linkPrompt.textContent = `Route starts at ${sender}. Select connected router(s), then receiver.`;
  });
  const remove = document.createElement("button");
  remove.className = "danger";
  remove.textContent = "Delete route";
  remove.addEventListener("click", () => deleteRoute(name));
  actions.append(build, shortest, remove);
  editor.append(actions);
}

function renderRouteItems() {
  routeItems.replaceChildren();
  routeItems.className = "item-list";
  for (const name of Object.keys(draft.traffic?.routes || {})) {
    const button = document.createElement("button");
    button.textContent = `Route: ${name}`;
    button.addEventListener("click", () => { selected = { kind: "route", name }; renderAll(); });
    routeItems.append(button);
  }
}

function renderSummary() {
  const parts = [
    `${Object.keys(draft.routers || {}).length} routers`,
    `${Object.keys(draft.switches || {}).length} switches`,
    `${Object.keys(draft.publishers || {}).length} publishers`,
    `${Object.keys(draft.subscribers || {}).length} subscribers`,
    `${(draft.links || []).length} links`,
  ];
  summaryEl.textContent = parts.join(", ");
}

function updateHistoryButtons() {
  undoButton.disabled = !history.length;
  redoButton.disabled = !future.length;
}

function renderAll() {
  renderGraph();
  renderInspector();
  renderRouteItems();
  renderSummary();
  updateHistoryButtons();
}

function scheduleValidation() {
  valid = false;
  previewButton.disabled = true;
  downloadButton.disabled = true;
  validationEl.className = "validation pending";
  validationEl.textContent = "Validating…";
  clearTimeout(validationTimer);
  validationTimer = setTimeout(validate, 250);
}

async function validate() {
  const sequence = ++validationSequence;
  try {
    const response = await fetch("/api/designer/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(draft),
    });
    const payload = await response.json();
    if (sequence !== validationSequence) return;
    const localErrors = portCollisionErrors();
    valid = response.ok && payload.valid && !localErrors.length;
    renderValidation([...(payload.errors || []), ...localErrors], payload.error);
  } catch (error) {
    if (sequence !== validationSequence) return;
    renderValidation([], error.message);
  }
}

function renderValidation(errors, requestError) {
  validationEl.className = `validation ${valid ? "valid" : "invalid"}`;
  validationEl.textContent = valid ? "Topology valid" : requestError || `${errors.length} validation error(s)`;
  errorsEl.replaceChildren();
  for (const error of errors.slice(0, 30)) {
    const item = document.createElement("div");
    item.className = "error";
    item.textContent = `${error.loc?.join(".") || "topology"}: ${error.message}`;
    errorsEl.append(item);
  }
  previewButton.disabled = !valid;
  downloadButton.disabled = !valid;
}

async function yamlResponse() {
  const response = await fetch("/api/designer/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(draft),
  });
  if (!response.ok) {
    const payload = await response.json();
    renderValidation(payload.errors || [], payload.error);
    throw new Error("Topology is not valid.");
  }
  return response;
}

async function previewYaml() {
  const response = await yamlResponse();
  yamlPreview.value = await response.text();
  yamlDialog.showModal();
}

async function downloadYaml() {
  const response = await yamlResponse();
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "topology.yaml";
  link.click();
  URL.revokeObjectURL(url);
}

async function importYaml(text) {
  const response = await fetch("/api/designer/import", {
    method: "POST",
    headers: { "Content-Type": "application/yaml" },
    body: text,
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Import failed");
  history.push(snapshot());
  future = [];
  draft = payload.config;
  positions = {};
  selected = null;
  autoLayout(false);
  renderAll();
  scheduleValidation();
  saveDraft();
}

async function loadExample() {
  const name = document.querySelector("#examples").value;
  if (!name) {
    if (!confirm("Replace current draft with blank topology?")) return;
    history.push(snapshot());
    draft = blankDraft();
    draft.defaults = schemaDefault(schema.properties.defaults);
    draft.startup = schemaDefault(schema.properties.startup);
  } else {
    if (!confirm(`Replace current draft with ${name}?`)) return;
    const response = await fetch(`/api/designer/examples/${encodeURIComponent(name)}`);
    const payload = await response.json();
    if (!response.ok) return alert(payload.error || "Could not load example.");
    history.push(snapshot());
    draft = payload.config;
    }
  future = [];
  positions = {};
  selected = null;
  autoLayout(false);
  renderAll();
  scheduleValidation();
  saveDraft();
}

async function initialize() {
  const [schemaResponse, examplesResponse] = await Promise.all([
    fetch("/api/designer/schema"),
    fetch("/api/designer/examples"),
  ]);
  const payload = await schemaResponse.json();
  const examplesPayload = await examplesResponse.json();
  schema = payload.schema;
  definitions = schema.$defs;
  manifest = payload.manifest;
  digest = payload.digest;
  draft = payload.initial_config || blankDraft();
  const savedText = localStorage.getItem(`quiclab-designer:${digest}`);
  let restored = false;
  if (savedText && confirm("Restore autosaved topology draft and layout?")) {
    try {
      const saved = JSON.parse(savedText);
      draft = saved.draft;
      positions = saved.positions || {};
      restored = true;
    } catch (_error) {
      localStorage.removeItem(`quiclab-designer:${digest}`);
    }
  }
  if (!payload.initial_config && !restored) {
    draft.defaults = schemaDefault(schema.properties.defaults);
    draft.startup = schemaDefault(schema.properties.startup);
  }
  if (!Object.keys(positions).length) autoLayout(false);
  const select = document.querySelector("#examples");
  for (const name of examplesPayload.examples) select.append(new Option(name, name));
  const globalButtons = document.querySelector("#global-config-buttons");
  for (const property of manifest.genericSections) {
    const button = document.createElement("button");
    button.className = "wide";
    button.type = "button";
    button.textContent = fieldTitle(property, schema.properties[property]);
    button.addEventListener("click", () => { selected = { kind: "global", property }; renderAll(); });
    globalButtons.append(button);
  }
  renderAll();
  scheduleValidation();
}

for (const button of document.querySelectorAll("#node-palette button")) {
  button.addEventListener("click", () => addNode(button.dataset.role));
  button.addEventListener("dragstart", (event) => event.dataTransfer.setData("text/quiclab-role", button.dataset.role));
}
document.querySelector("#link-mode").addEventListener("click", () => {
  routeBuild = null;
  linkMode = true;
  linkStart = null;
  linkPrompt.textContent = "Select first node, then second node.";
});
document.querySelector("#add-route").addEventListener("click", addRoute);
document.querySelector("#load-example").addEventListener("click", loadExample);
document.querySelector("#import-file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  try { await importYaml(await file.text()); } catch (error) { alert(error.message); }
  event.target.value = "";
});
undoButton.addEventListener("click", undo);
redoButton.addEventListener("click", redo);
document.querySelector("#auto-layout").addEventListener("click", () => autoLayout(true));
previewButton.addEventListener("click", () => previewYaml().catch((error) => alert(error.message)));
downloadButton.addEventListener("click", () => downloadYaml().catch((error) => alert(error.message)));
document.addEventListener("keydown", (event) => {
  if (!(event.ctrlKey || event.metaKey)) return;
  if (event.key.toLowerCase() === "z") {
    event.preventDefault();
    event.shiftKey ? redo() : undo();
  } else if (event.key.toLowerCase() === "y") {
    event.preventDefault();
    redo();
  }
});

initialize().catch((error) => {
  validationEl.className = "validation invalid";
  validationEl.textContent = `Designer failed to load: ${error.message}`;
});
