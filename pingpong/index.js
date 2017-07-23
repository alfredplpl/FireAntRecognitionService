const WebSocket = require('ws');
const wsPong = new WebSocket('ws://localhost:22222');
var twitter = require('twitter');

var twitterClient = new twitter({
    consumer_key:        'AAA',
    consumer_secret:     'BBB',
    access_token_key:    'CCC',
    access_token_secret: 'DDD',
});

wsPong.on('open', function open() {
 	console.log('connected');
	wsPong.ping();
});

wsPong.on('close', function close() {
  console.log('disconnected');
  twitterClient.post('statuses/update',
        {status: '@alfredplpl あいつはしんだ。1970年から'+Date.now()+"ミリ秒後にな。"},
        function(error, tweet, response) {
	        if (!error) {
	            console.log(tweet)
	        }
   		}
   		);
});

wsPong.on('error', function close() {
  console.log('error');
});


wsPong.on('pong', function incoming(data) {
  console.log("isAlive");
  setTimeout(function timeout() {
    	wsPong.ping();
  }, 10000);
});
