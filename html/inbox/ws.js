var websocket;
function wsconnect(url, subscribe, message) {
	websocket = new WebSocket(url);
	websocket.onopen = function(evt) { 
		console.info('CONNECT:' + String(typeof subscribe));
		if ( typeof subscribe == 'function' ) {
			websocket.send(JSON.stringify(subscribe()));
		} else if (typeof subscribe == 'string') {
			websocket.send(JSON.stringify(subscribe));
		} else {
			console.info('skip subscribe');
		}
	};
	websocket.onclose = function(evt) { 
		console.info('onclose: try again in...15 seconds' + evt); 
		setTimeout(function () { wsconnect(url, subscribe, message) }, 15 * 1000); 
	};
	websocket.onmessage = function(evt) { console.info('onmessage:'); message(evt) };
	websocket.onerror = function(evt) { console.info('onerror'); };
}
