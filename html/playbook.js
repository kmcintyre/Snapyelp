define(function() {
	
	function url_domain(data) {
		var a = document.createElement('a');
		a.href = data;
		return a.hostname;
	}
 
	var javascript_site = url_domain('loading');
	console.log(javascript_site);	
	var reconnect_timeout = 1000 * 15;	
	var lookup_array = [];
		
	function lookup_item(key, value) {
		console.log('lookup_item:' + key + 'value:' + value )
		for ( var x = 0; x < lookup_array.length; x++ ) {
			if ( lookup_array[x].key == key ) {
				if (value) {
					lookup_array[x] = value;					
				} else {					
					lookup_array.splice(x, 1);
				}
				return
			}
		}
		lookup_array.push({'key': key, 'value': value});
	}	
	
	function lookup(key) {
		if ( !key ) { return lookup_array; }
		for ( var x = 0; x < lookup_array.length; x++ ) {
			if ( lookup_array[x].key == key ) {
				return lookup_array[x].value;
			}
		}
		return null;
	}	

	function get_connection_for(ws_url) {		
		tried_which = lookup('connection').indexOf(ws_url);
		if ( tried_which >= 0 && tried_which < lookup('connection').length - 1 ) {
			var tn = lookup('connection')[tried_which+1];
			console.log('try next:' + tn);
			return tn;
		} else {
			console.log('default too:',lookup('connection')[0]);
			return lookup('connection')[0];
		}
	}
		
	function consume(msg) {
		lookup_item(msg.key,msg.value)		
	}
	
	function connection(ws_url) {
		if ( !lookup('connection') ) {			
			return 'ws://service.' + this.site + ':8081'; 
		} else {
			return get_connection_for(ws_url) 
		}
	}
		
	return { 
		swkey : null,
		consume: consume,		
		lookup : lookup,
		site : javascript_site.substring(javascript_site.indexOf('.')+1),
		connection : connection		
	}	
})