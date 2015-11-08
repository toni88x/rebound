var updater = {
    socket: null,

    start: function() {
	console.log("starting rebound websocket");
        var url = "ws://localhost:8877/reboundsocket";
        updater.socket = new WebSocket(url);
	console.log(updater.socket);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
    },

    showMessage: function(message) {
        //console.log(message);
	if (message.id==0){
		N = message.N;
	}
	if (message.id==1){
		fillBuffer(message.data);
        	drawScene();
	}
    }
};
updater.start();
