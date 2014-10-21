define(["jquery", "site", "stream"], function($, site, stream) {		
	$(document).ready(function() {
		console.log('create button');
		$(document.body).append('<button id="randombutton">Random Reserve</button>').one('click', function (e) {			
			stream.send({'reserve': 'random'});
			$(e.target).html('Init Reservation')
		})
	});		
});	
