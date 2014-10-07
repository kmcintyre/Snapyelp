requirejs.config({
	urlArgs: "vet=ted",	
    "paths": {    	
      "jquery": "//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min",
    }
});
requirejs(["init"]);