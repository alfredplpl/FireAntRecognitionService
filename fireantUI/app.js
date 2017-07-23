// Thanks for
// http://qiita.com/nkjm/items/723990c518acfee6e473

var express = require("express");
var app = express();
var fs = require('fs');
var multer = require('multer'); 
var upload = multer({ dest: './public/uploads/' }); 
var responses=new Array();
var requests=new Array();
const WebSocket = require('ws');

app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');
//TODO: static path
app.use(express.static('public'));

app.listen(80, function () {
  console.log('[FireAntUI] INFO: app listening on port 80!');
});

//heart beat
const wssPong = new WebSocket.Server({ backlog:1,port: 22222 });
wssPong.on('connection', function connection(ws) {
  	ws.on('ping', function(){
  	});
});

const wss = new WebSocket.Server({ backlog:1,port: 24564 });
wss.on('connection', function connection(ws) {
	ws.on('message', function incoming(message) {
		console.log('[FireAntUI] INFO: received: %s', message);
		msg=JSON.parse(message);
		console.log(msg);

		res=responses.shift();
		req=requests.shift();

		if(msg.filename!=req.file.filename){
			res.render('result', {result : "内部でエラーが起きたよ。もう一度送信してね。",image:"/img/unknown.jpg"});
			console.log("[FireAntUI] ERROR: request mismatch!");
			requests=new Array();
			responses=new Array();
			return;
		}

		switch(msg.answer){
			case "true":
				res.render('result', {result : "ヒアリかもしれない",image:"uploads/"+msg["filename"]});
			break;
			case "false":
				res.render('result', {result : "ヒアリじゃないアリかもしれない",image:"uploads/"+msg["filename"]});	
			break;
			case "cannotRead":
				res.render('result', {result : "画像が読み込めなかったよ・・・。",image:"/img/unknown.jpg"});	
			break;
			case "arigumo":			
				res.render('result', {result : "アリじゃなくてそもそもアリグモかもしれない",image:"uploads/"+msg["filename"]});	
			break;
			case "hillary":			
				res.render('result', {result : "ヒアリーじゃなくてヒラリーかもしれない",image:"uploads/"+msg["filename"]});	
			break;
			case "neutral":			
				res.render('result', {result : "そもそもアリじゃないかもしれない",image:"uploads/"+msg["filename"]});	
			break;
			default:
				res.render('result', {result : "今の僕には理解できませんでした",image:"uploads/"+msg["filename"]});					
		}
	});
});

saveUploads = function(req, res) {
  	console.log(req.file);
	if (typeof req.file === "undefined"){
  		console.log("[FireAntUI] WARN: go cat.");	
		res.render('result', {result : "ねこでもみて落ち着いてファイルを選択してね",image:"/img/unknown.jpg"});
		return;
	}

  	if(wss.clients.size==0){
		res.render('result', {result : "内部でエラーが起きたよ。運営の人に知らせてね。",image:"/img/unknown.jpg"});
		console.log("[FireAntUI] ERROR: recognition server is down!");
		requests=new Array();
		responses=new Array();
		return;
  	}

  	responses.push(res);
  	requests.push(req);
  	wss.clients.forEach(function each(client) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(req.file));
      }
  	});

};

app.post('/upload',upload.single('upfile'),saveUploads);


