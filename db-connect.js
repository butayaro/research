var net = require('net'),
    JsonSocket = require('json-socket');
var http = require('http');
// requireの設定
const mysql = require('mysql');

// MySQLとのコネクションの作成
const connection = mysql.createConnection({
  host : 'localhost',
  user : 'root',
  password : '',
  database: 'nginx'
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

SQL_request='select bytes_sent size,remote_addr,request_length,uri,count(time between "'+zero+' 00:00:00" and "'+first+' 00:00:00" or null) first ,count(time between "'+first+' 00:00:01" and "'+second+' 00:00:00" or null) second,count(time between "'+second+' 00:00:01" and "'+third+' 00:00:00" or null) third,count(time between "'+third+' 00:00:01" and "'+forth+' 00:00:00" or null) forth from access_log  group by uri;'
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

// 接続終了
connection.end();

