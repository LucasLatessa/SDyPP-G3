const net = require('net');

// --------------------------------------------------------

const server = net.createServer((socket) => {
        var buffer = '';  
        
        socket.on('data', (chunk) => {
          buffer += chunk.toString();
          
          try {
            const data = read(buffer);          
            buffer = data.buffer;
            
            data.messages.forEach((message) => {
              parse(message, socket);
            });   
          } catch(err) {
            console.error('!!! INTENTO DE HACKEO !!!');
            socket.end();            
          }
        });
        
        socket.on('error', () => { });
      });
      
server.on('error', (err) => {
  console.error(err);
});

server.listen(52030, () => {
  console.log('Server ready.');
}); 

// --------------------------------------------------------

function read(buffer) {
  let messages = buffer.split('|');
  
  buffer = messages.pop();  
  messages = messages.map((msj) => {
    try {
      msj = JSON.parse(msj);
    } catch(err) {
      msj = false;
    }
    
    return msj;
  })
  .filter(Boolean);
  
  return { messages, buffer };
}

function write(socket, id, data, error) {
  try {
    data = JSON.stringify({ id, data, error });  
    socket.write(data + '|');
  } catch(err) {
    console.error(data);
    console.error(err);    
  }
}

function parse(message, socket) {
  console.dir(message, { depth: null });
  
  if ( !_PROTOCOLO_.hasOwnProperty(message.data.type) ) {
    console.error('!!! INTENTO DE HACKEO !!!');
    console.error(message);
    socket.end();    
    return;
  }
  
  try {
    _PROTOCOLO_[message.data.type](socket, message.id, message.data.data);
  } catch(err) {
    console.error(message);
    console.error(err);
  }
}

// --------------------------------------------------------

const _PROTOCOLO_ = {
  sorpresa: function(socket, id, data) {
    setTimeout(function() {
      const err = Math.random() > 0.5;

      if (err) {        
        write(socket, id, { message: 'Error salvaje aparecio.' }, err);
      } else {
        const randomIndex = Math.floor(Math.random() * data.length);
        const randomNumber = data[randomIndex];
        write(socket, id, { randomNumber }, err);        
      }
    }, Math.random() * 1000);    
  }
}


// --------------------------------------------------------