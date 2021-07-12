// --
// # JSX React template literal
//
// This is an update of [Jonathan
// Raphaelson](https://gist.github.com/lygaret/a68220defa69174bdec5)'s JSX [tagged
// template](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates),
// formulated as an ES6 module. It has the following changes compared to
// the original:
//
// - Defined as an ES6 module ready to import
// - Does not depend on React, can be used with others
//
// You might know of [htm](https://github.com/developit/htm), but HTM
// is not exactly JSX, which means you can't reuse the code as-is if you wish
// to switch to JSX.
//
// # References
//
// - [JSX Quasi-Literal](https://gist.github.com/lygaret/a68220defa69174bdec5), 2015 the original implementation of this module
// - [Hyperscript Tagged Markup](https://github.com/developit/htm), 2021, a JSX alternative
// - [React without Webpack](https://datastation.multiprocess.io/blog/2021-07-08-react-without-webpack.html), 2021
// - [Introducing the new JSX Transform](https://reactjs.org/blog/2020/09/22/introducing-the-new-jsx-transform.html), 2020, mentions an alternative to `React.createElement`.
// - [https://github.com/lukejacksonn/es-react](https://github.com/lukejacksonn/es-react), 2020, as odd as it is, we still can't import React straight into the browser using ES6 modules.

const RE_SLOT = /\{__(\d)+__\}/;
const Factories = {};

// TODO: Support multiple children
// TODO: Whitespace handling seems off

// --
// We provide a transparent function that makes it possible to register
// components as they are imported. They then become available as a new
// node type.
export const component = (factory, name) => {
  Factories[factory.name ?? name] = factory;
  return factory;
};

// --
// The `createElement` function acts as a wrapper around the default
// element factory, looking first in the `Factories` map. This makes it
// possible to register custom elements that are then used first instead
// of the generic element factory.
export const createElement = (name, attrs, children) =>
  Factories[name]
    ? Factories[name](attrs, children)
    : createElement.factory
    ? createElement.factory(name, attrs, children)
    : { name, attrs, children };

// --
// Sets the default element factory.
export const setElementFactory = (factory) => {
  createElement.factory = factory;
  return factory;
};

// --
// Parses the given `text` as an XML/HTML DOM tree
const parseXML = (text) => {
  try {
    return new DOMParser().parseFromString(text, "text/xml");
  } catch (e) {
    throw new Error(`jsx:XML Parsing Error: ${e}\n${text}`);
  }
};

// --
// Transforms the array of string parts into a DOM,
// Turns `["<div class='", "'>Hi</div>"]`
// into `"<div class='__0'>Hi</div>"`
const parseJSX = (parts) => {
  const slotted = (parts || [])
    .reduce((r, v, i) => {
      r.push(`${v}${i < parts.length - 1 ? `{__${i}__}` : ""}`);
      return r;
    }, [])
    .join("");

  return parseXML(slotted).firstChild;
};

// --
// Resolves the given value from the slots array if it is a slot (`__N__`),
// returning the `N`th value of the slots array.
const unslot = (value, slots) => {
  const match = value.match(RE_SLOT);
  const slot = match ? slots[parseInt(match[1])] : value;
  return slot;
};

// --
// Transforms the DOM tree into a VDOM, replacing parameter placeholders (see
// `RE_SLOT`) with the corresponding arguments from from the `slots` array.
// Functions previously registered as `component`s will be used to create
// elements of the given type, taking `(props,children)` as arguments.
const toVDOM = (node, slots, createElement, key) => {
  if (node.nodeValue) {
    // We replace the trimmed node value by the corresponding argument.
    const v = node.nodeValue.trim();
    // TODO: We might want to check that the argument exists
    return unslot(v, slots);
  } else {
    // If the node name is a SLOT, then we evaluate it
    const type = unslot(node.localName, slots);

    // We populate the `props`, replacing the `slots` along the way.
    const props = { key: key };
    const attrs = node.attributes;
    for (let i = attrs.length - 1; i >= 0; i--) {
      const { name, value } = attrs.item(i);
      props[name] = unslot(value, slots);
    }

    // We populate the children
    const children = [];
    for (let i = 0; i < node.childNodes.length; i++) {
      const child = toVDOM(node.childNodes[i], slots, createElement, i);
      children.push(child);
    }

    return createElement(type, props, children);
  }
};

// --
// The template literal processor that turns the JSX into a VDOM.
export const jsx = (parts, ...slots) => {
  // TODO: We should test Fragment, Context, and the likes
  return toVDOM(
    parseJSX(typeof parts === "string" ? [parts] : parts),
    slots,
    createElement,
  );
};

// EOF
