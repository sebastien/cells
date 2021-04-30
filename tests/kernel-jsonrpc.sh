HOST=localhost
PORT=8000
# Sends the given JSONRPC message, and expects the given receive. Usage is
# like: call METHOD PARAMS expects VALUE
function send() {
	result=$(echo "{\"jsonrpc\":\"2.0\",\"method\":\"$1\",\"params\":$2}" | timeout 0.25 nc $HOST $PORT)
	if [ "$4" != "$result" ]; then
		echo "[!] Command '$1' got '$result', expected '$4'"
	fi
}
# The tests
send    set '{"session":"A","slot":"a","inputs":[],"source":"1.0","type":"js"}'\
	expects '{"jsonrpc":"2.0","result":true}'

send    get '{"session":"A","slot":"a"}'\
	expects '{"jsonrpc":"2.0","result":1.0}'
# EOF
