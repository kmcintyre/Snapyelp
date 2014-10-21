define(["jquery","playbook"], function($,playbook) {	
				
	function open_socket(ws_url) {	
		if (ws_url) {
			console.log('attempt reconnect!');
		}
		
		var attempt_url = playbook.connection(ws_url);				
		var websocket = new WebSocket(attempt_url);		
		
		function reconnect() {
			console.log('reconnect')
			websocket = open_socket(attempt_url);
		}				
				
		websocket.onopen = function(evt) {			
			console.log('on open');				
		}; 
		
		websocket.onclose = function(evt) { 
			console.log('onclose')
			if ( evt.code == 1006 ) {
				setTimeout(function() { reconnect(websocket.attempted_url); }, 15 );
			} else {
				console.log('onclose:' + evt.code);
			}
		};
		
		websocket.onerror = function(evt) {
			console.log('onerror')
		};
		
		websocket.onmessage = function(evt) {
			try {
				var ip = JSON.parse(evt.data);
				console.log(ip)
				if (ip['reservation']) {
					console.log('got response')
					$('#randombutton').html(ip['reservation'])
				}
			} catch (err) {
				playbook.swkey = evt.data;
				console.log('set swkey:' + playbook.swkey);
				websocket.send(JSON.stringify(playbook));					
			}
		};
		
		return websocket; 
	}	
		
	var websocket = open_socket();
	
	return {
		send : function(msg) {
			console.log('sending')
			if (websocket.readyState == 1) {
				if (!msg) {
					console.log(playbook);
					websocket.send(JSON.stringify(playbook));
				} else {
					for (var key in playbook) { msg[key] = playbook[key]; }
					console.log(msg);
					websocket.send(JSON.stringify(msg));
				}
			}
		}	
	};	
});