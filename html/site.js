define(['playbook'], function(playbook) {
	playbook.consume({key:'connection',value:['ws://service.snapyelp.com:8081']}) 		
	return {		
		loaded:true
	}	
})