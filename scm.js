var net = require('net'),
    JsonSocket = require('json-socket');
var http = require('http');
// requireの設定

var chokidar = require("chokidar");

//chokidarの初期化
var watcher = chokidar.watch('./cold-files',{
    ignored:/[\/\\]\./,
    persistent:true
});

watcher.on('ready',function(){
    watcher.on('change',function(path){
        console.log(path + " changed.");
        var fs = require("fs");
        var readline = require("readline");
        //Coldなファイルを書き出したファイルを生成、以下の処理を行う。
        var stream = fs.createReadStream("./cold-files", "utf8");

        var reader = readline.createInterface({ input: stream });
        reader.on("line", (data) => {
        //    console.log('line : ',data);
            var uriarr = data.split("/");
            bucket = uriarr[1];
//            path = uriarr[2];
            bucket = encodeURIComponent(bucket);
	    path = uriarr.slice(2,uriarr.length).join("/");
            path = encodeURIComponent(path);
	    console.log('backet:'+bucket+' path:'+path);
            var options = {
                host: '192.168.1.151',
                path: '/ScalityArchiverRest/layer\?mode=archive\&bucket\='+bucket+'\&path\='+path,
                port: '8080',
                method: 'PUT',
//                headers: {
//                    'Content-Type': 'application/json',
//                    'Accept': 'application/json'
//                }
            };
            callback = function(response) {
                var str = ''
                response.on('data', function(chunk) {
                    str += chunk;
                });
                response.on('end', function() {
		    console.log(str);
                   // console.log(JSON.parse(str));
                })
              };
            var req = http.request(options, callback);
            console.log("Layer API call " + options.path);
//            body = "{\"usertaglist\":{\"usertag\":[\"test\"]}}";
//            req.write(body);
            req.end();

            //データ移動命令を発行
        });
    });
});

// 接続終了

