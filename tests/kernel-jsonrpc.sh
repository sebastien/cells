# -- title=Tests the basic RPC interface of a Kernel
# --
# This tests simple mathematical expressions that should work with most
# languages.
# --
HOST=localhost
PORT=8000

# Sends the given JSONRPC message, and expects the given receive. Usage is
# like: call METHOD PARAMS expects VALUE
function send() {
	# NOTE: We use timeout, but ideally we should disconnect on receiving an EOL
	# character.
	result=$(echo "{\"jsonrpc\":\"2.0\",\"method\":\"$1\",\"params\":$2}" | timeout 0.25 nc $HOST $PORT)
	if [ "$4" != "$result" ]; then
		echo "[!] Command '$1' got '$result', expected '$4'"
	fi
}

# --
# The test itself is a simple cell `C = A * B`.
# --

send    set '{"session":"A","slot":"a","inputs":[],"source":"10"}'\
	expects '{"jsonrpc":"2.0","result":true}'

send    get '{"session":"A","slot":"a"}'\
	expects '{"jsonrpc":"2.0","result":10}'

send    set '{"session":"A","slot":"b","inputs":[],"source":"5"}'\
	expects '{"jsonrpc":"2.0","result":true}'

send    set '{"session":"A","slot":"c","inputs":["a","b"],"source":"a * b"}'\
	expects '{"jsonrpc":"2.0","result":true}'

send    get '{"session":"A","slot":"c"}'\
	expects '{"jsonrpc":"2.0","result":50}'

# EOF
