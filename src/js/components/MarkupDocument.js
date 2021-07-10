import { component, createElement, jsx } from "../jsx.js";
import {
  basicSetup,
  EditorState,
  EditorView,
} from "https://unpkg.com/@codemirror/basic-setup?module";
import { javascript } from "https://unpkg.com/@codemirror/lang-javascript?module";
import { python } from "https://unpkg.com/@codemirror/lang-python?module";

const MARKUP = {
  title: "h2",
  section: "section",
  pre: "pre",
  code: "code",
  p: "p",
};

const markup = ([name, attrs, children]) =>
  createElement(
    MARKUP[name] ?? "div",
    Object.assign(attrs, { class: name }),
    (children || []).map((_) => (typeof _ === "string" ? _ : markup(_))),
  );

export default component(function MarkupDocument(props) {
  return jsx`
   	  <div class="MarkupDocument">${markup(props.content)}</div>
   	`;
});
