import { component, jsx } from "../jsx.js";

export default component(function Button(props) {
  return jsx`
	  <button class="Button control"><span class="Button-label">${props.name}</span></button>
	`;
});
