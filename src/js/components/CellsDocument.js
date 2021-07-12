import { component, jsx } from "../jsx.js";
import CodeEditor from "./CodeEditor.js";
import parseMarkdown from "../md.js";

const MarkdownConverter = new showdown.Converter();

const MarkdownCell = (props) => {
  //const text = `<div>${parseMarkdown(props.content.join(""))}</div>`;
  const text = `<div>${
    MarkdownConverter.makeHtml(
      props.content.join(""),
    )
  }</div>`;
  const tree = jsx(text);
  return tree;
};

const CodeCell = (props) => {
  const lines = props.content;
  return CodeEditor({ lines });
};

const ContentTypes = {
  markdown: MarkdownCell,
  javascript: CodeCell,
  python: CodeCell,
};

export default component(function CellsDocument(props) {
  return jsx`
	  <div class="MarkupDocument">${
    props.content.map((_) => (ContentTypes[_.type] ?? MarkdownCell)(_))
  }</div>
   	`;
});
