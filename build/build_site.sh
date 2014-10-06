if [ -d ../$1 ]; then
    echo building $1

	if [ ! -f 'jquery.min.js' ]; then
		echo "get jquery"  
		wget http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js
	fi
	
	cd ~/scewpt
	
	export PYTHONPATH=`pwd`
	
	cd ~/scewpt/sites/$1

	/usr/local/bin/node ../build/r.js -o baseUrl=script/ paths.jquery=../../build/jquery.min name=index out=../build/index.js
    
    if [ "$2" == "true" ]; then
    	echo 'will publish'
    	
    	cd ~/scewpt

		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/error.html -t error.html -p public-read
		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/unknown.svg -t unknown.svg -p public-read
		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/google087e985081b2667c.html -t google087e985081b2667c.html -p public-read
		
		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/$1/index.html -t index.html -p public-read
		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/script/index.css -t script/index.css -p public-read		
		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/build/index.js -t script/index.js -p public-read -e gzip			
		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/$1/channel.json -t channel.json -p public-read -e gzip		
		python ~/6998159/s3copy.py -b www.$1 -f ~/scewpt/sites/$1/script/require.js -t script/require.js -p public-read -e gzip
		
		python pyscewpt/site/invalidate.py $1
				    	
    else
    	echo 'will not publish'
    fi
else
	echo $1 cannot be found
fi