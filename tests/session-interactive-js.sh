#!/usr/bin/env bash
function expect() {
	if [ "$1" != "$2" ]; then
		echo "[!] Got '$1', expected '$2'"
	fi
}
cells eval -S test clear
cells eval -S test set slot=A inputs=B,C source=B+C type=js
expect $(cells eval -S test get slot=A) << EOF
undefined
EOF
# EOF
