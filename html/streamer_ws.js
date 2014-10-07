define(["jquery","playbook",'page_title','tool',"cookies.min"], function($,playbook,page_title,tool,cookies) {	
		
	function connection_state(color,backward){
		console.log('color:' + color);
		$('svg:first g').attr('fill',color);
		$('svg g').first().css('opacity','.50');
		var spin = backward ? -16 : 8;
		page_title.spinbug(spin);
		setTimeout(function() { $('svg g').first().css('opacity','1'); }, 500 );
	}
		
	function open_socket(ws_url) {	
		connection_state(playbook.lookup('color').onopen);
		if (ws_url) {
			console.log('attempt reconnect!');
		} else {
			page_title.messaging(playbook.lookup('init'), 'announcement');
		}
		
		var attempt_url = playbook.connection(ws_url);				
		var websocket = new WebSocket(attempt_url);		
		
		function reconnect() {
			console.log('reconnect')
			websocket = open_socket(attempt_url);
		}				
				
		websocket.onopen = function(evt) {			
			console.log('on open');			
			page_title.messaging(playbook.lookup('onopen'), 'announcement');
		}; 
		
		websocket.onclose = function(evt) { 
			console.log('onclose')
			if ( evt.code == 1006 ) {
				connection_state(playbook.lookup('color').onclose, true);
				page_title.messaging(playbook.lookup('onclose'), 'announcement', true);				
				setTimeout(function() { reconnect(websocket.attempted_url); }, playbook.reconnect);
			} else {
				console.log('onclose:' + evt.code);
			}
		};
		
		websocket.onerror = function(evt) {
			console.log('onerror')
		};
		
		websocket.onmessage = function(evt) {
			connection_state(playbook.lookup('color').onmessage);			
			if ( evt.data instanceof Blob ) {
				var lenreader = new window.FileReader();					
				lenreader.readAsText(evt.data.slice(0,4));
				lenreader.onloadend = function() {				
					var meta_length = parseInt(lenreader.result)
					var jsonreader = new window.FileReader();					
					jsonreader.readAsText(evt.data.slice(4,meta_length+4));
					jsonreader.onloadend = function() {
						tool.display_tweet(JSON.parse(jsonreader.result),evt.data.slice(meta_length+4));
						connection_state(playbook.lookup('color').onmessage)
					}
				}				
				
			} else { 
				try {
					var ip = JSON.parse(evt.data);
					for (var x = 0; x < Object.keys(playbook).length; x++ ) {
						var ek = Object.keys(ip)[x];
						if ( ip[ek] ) {
							console.log('UPDATE:' + ek + ' ' + ip[ek]);
							player[ek] = ip[ek] 
						}
					}
				} catch (err) {
					playbook.swkey = evt.data;
					console.log('set swkey:' + playbook.swkey);
					websocket.send(JSON.stringify(playbook));					
				}
			}
		};
		
		return websocket; 
	}	
		
	var websocket = open_socket();
	
	return {
		
		send : function() {
			console.log('sending');
			console.log(playbook);
			if (websocket.readyState == 1) {
				websocket.send(JSON.stringify(playbook));				
			}
		},		
		set_league : function(l,ready) {
			console.log('set league');
			websocket.league = l;
			if (ready) {
				this.send(ready);
			} else {
				this.send({loaded: true})
			}
			
		}
	};	
});