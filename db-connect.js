// requireの設定
const mysql = require('mysql');
 
// MySQLとのコネクションの作成
const connection = mysql.createConnection({
  host : 'localhost',
  user : 'root',
  password : 'password',
  database: 'test'
});
 
// 接続
connection.connect();

//現在の年、月を取得
require('date-utils');
var dt = new Date();
var ym = dt.toFormat("YYYY-MM");

// userdataの取得
var cycle = 31; //in case classification cycle is 30day
var zero = ym +'-'+(Math.ceil(cycle/4*0)+1);
var first = ym +'-'+(Math.ceil(cycle/4*1));
var second = ym +'-'+(Math.ceil(cycle/4*2));
var third = ym +'-'+(Math.ceil(cycle/4*3));
var forth = ym +'-'+(Math.ceil(cycle/4*4));

 
// userdataの取得
SQL_request='select remote_addr,bytes_sent,uri,count(time between "'+zero+' 00:00:00" and "'+first+' 00:00:00" or null) first ,count(time between "'+first+' 00:00:01" and "'+second+' 00:00:00" or null) second,count(time between "'+second+' 00:00:01" and "'+third+' 00:00:00" or null) third,count(time between "'+third+' 00:00:01" and "'+forth+' 00:00:00" or null) forth from log_test where query_string = "-" group by uri;'
connection.query(SQL_request, function (err, rows, fields) {
  if (err) { console.log('err: ' + err); } 
 
   var spawn = require('child_process').spawn,
    py    = spawn('python', ['compute_input.py']),
    data = rows,
    dataString = '';
    errString = '';

   py.stderr.on('data', (err) => {  // 昨日は、data 部分が error だった
        console.error(err.toString());
    //    console.log('spawn Error *********');
    })

   py.stdout.on('data', function(data){
    dataString += data.toString();
   });
   py.stderr.on('data', function(data){
    errString += data.toString();
   });
   py.stdout.on('end', function(){
    console.log('Hot files=',dataString);
    console.log('0 : ',dataString[1]);
   });
   py.stderr.on('end', function(){
    console.log('Errors=',errString);
   });
   py.stdin.write(JSON.stringify(data));
   py.stdin.end();
   //
  //}

});

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
  //          console.log('line : ',data);
            //RINGに存在するかチェック
　            //存在する場合は、SCM登録を行う。
　　            //登録に失敗したら終了
            //データ移動命令を発行
        });
    });
});
// time , size, request_length, request_method(up,down,update),remote_addr 
/*  
// userdataのカラムを取得
connection.query('SHOW COLUMNS FROM log_test;', function (err, rows, fields) {
  if (err) { console.log('err: ' + err); }
 
  console.log(rows[0].Field);
  console.log(rows[1].Field);
});
*/ 
// 接続終了
connection.end();
