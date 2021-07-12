import { component, jsx } from "../jsx.js";
// FIXME: This does not quite work yet
//import { useEffect, useRef } from "../hooks.js";

import {
  basicSetup,
  EditorState,
  EditorView,
} from "https://unpkg.com/@codemirror/basic-setup?module";
import { javascript } from "https://unpkg.com/@codemirror/lang-javascript?module";
import { python } from "https://unpkg.com/@codemirror/lang-python?module";

export default component(function CodeEditor({ lines }) {
  const wrapper = 1.0; //useRef(null);
  useEffect(() => {
    console.log("WRAPPER", wrapper);
  }, [wrapper]);
  // const
  // const editor = new EditorView({
  // 	state: EditorState.create({
  // 	  doc: Text.of(lines),
  // 	}),
  // 	parent: null,
  //   }
  return jsx`
	  <div class="CodeEditor">X</div>
   	`;
});
