const net = require('net');

const opts = {
  host: '127.0.0.1',
  port: 52030
}

const socket = net.createConnection(opts, () => {
                 var buffer = '';

                 socket.on('data', (chunk) => {
                   buffer += chunk.toString();                   
                   buffer = read(buffer);
                 });

                 _MAIN_(socket);
               });

socket.on('end', () => {
  console.log('disconnected from server');
});

// --------------------------------------------------------

const _PROMISES_ = { };

// --------------------------------------------------------

function read(buffer) {
  let responses = buffer.split('|');
  buffer = responses.pop();

  try {
    responses = responses.map(JSON.parse);
    
    responses.forEach((message) => {      
      if ( !_PROMISES_.hasOwnProperty(message.id) ) {
        return;
      }

      if (message.error) {
        _PROMISES_[message.id].reject(message.data);
        delete _PROMISES_[message.id];
        return;
      }

      _PROMISES_[message.id].resolve(message.data);
      delete _PROMISES_[message.id];
    });
  } catch(err) {
    console.error(buffer);
    console.error(err);
  }

  return buffer;
}

function write(socket, id, data) {
  try {
    data = JSON.stringify({ id, data });
    socket.write(data + '|');
  } catch(err) {
    console.error(data);
    console.error(err);
  }
}

// --------------------------------------------------------

async function task(socket, data) {
  const id = Date.now().toString();

  return new Promise(function(resolve, reject) {
    _PROMISES_[id] = { resolve, reject };
    write(socket, id, data);
  });
}

// --------------------------------------------------------

async function _MAIN_(socket) {
  try {
    var result = await task(socket, {
      type: 'sorpresa',
      data: [ 4, 5 ]
    });
    
    console.log(result);
  } catch(err) {
    console.error(err);
  }
}

// --------------------------------------------------------