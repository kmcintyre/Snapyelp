define(['playbook'], function(playbook) {
	playbook.consume({key:'init',value:['AWS Stadium', 'tweets from pros', 'world Around']})
	playbook.consume({key:'onclose',value:['Fumble!', 'Ball\`s on the Turf', 'Pile up near mid-field']})
	playbook.consume({key:'onopen',value:['Enjoy sport']})
	playbook.consume({key:'connection',value:['ws://localhost:8080']})
	playbook.consume({key:'color',value:{ 'onmessage' : '#0052A5', 'onopen' : '#f7a70c', 'onclose' : '#960018'}}) 		
	return {		
		loaded:true
	}	
})