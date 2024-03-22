/*ejemplo basico de http y websocket*/
const http = requiere('http'); //paquete para usar http con Nodejs
        fs=requiere('fs');
        root=__dirname+'/public';
//documentacion http con nodejs: https://nodejs.org/api/http.html

const server=http.createServer((req,res)=>{//request y response
    //req.write()IMPOSIBLE, no se puede escribir en el canal que recibo
    //res.read()IMPOSIBLE, no se puede leer en el canal que escribo
    let host=req.headers.host.split(':').shift();
    
    
    pathname=path.join(root,host,request.url);


    console.dir(req.method,{depth:null}); 
    console.dir(req.url,{depth:null});
    console.dir(host,{depth:null});

    res.writeHead(200,{'Content-Type':'application/json'});//code 200 significa todo esta bien
    res.write(JSON.stringify({
        data: 'Hola Mundo desde el servidor!',
    }));
    res.end();
    // res.end(JSON.stringify({
    //     data: 'Hola Mundo desde el servidor!',
    // })); //forma de hecer lo mismo pero reducido
}); 
server.listen(8000);//escuchar peticiones por este puerto