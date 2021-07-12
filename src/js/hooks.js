import {
  useEffect as _useEffect,
  useRef as _useRef,
  useState as _useState,
} from "https://unpkg.com/preact@latest/hooks/dist/hooks.module.js?module";
// SEE: https://github.com/preactjs/preact/issues/1961
export const useState = _useState;
export const useEffect = _useEffect;
export const useRef = _useRef;
// EOF
