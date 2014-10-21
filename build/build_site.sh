if [ ! -f 'jquery.min.js' ]; then
	echo "get jquery"  
	wget http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js
fi
	
cd ~/Snapyelp

export PYTHONPATH=`pwd`
	
cd html

/usr/local/bin/node ../build/r.js -o baseUrl=../html paths.jquery=../build/jquery.min name=index out=../build/index.js

if [ "$1" == "true" ]; then
    	echo 'will publish'
    	
    	cd ~/Snapyelp
		
		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/html/index.html -t index.html -p public-read
		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/build/index.js -t index.js -p public-read -e gzip			
		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/html/require.js -t require.js -p public-read -e gzip
		
		python snapyelp/aws/invalidate.py		

		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/html/inbox/ws.js -t inbox/ws.js -p public-read
		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/html/inbox/index.css -t inbox/index.css -p public-read
		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/html/inbox/index.html -t inbox/index.html -p public-read
		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/html/inbox/font.css -t inbox/font.css -p public-read
		python ~/6998159/s3copy.py -b snapyelp.com -f ~/Snapyelp/html/inbox/font.woff -t inbox/font.woff -p public-read
				    	
else
	echo 'will not publish'
fi
