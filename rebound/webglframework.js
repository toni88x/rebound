<script type="text/javascript">

function webGLStart(updater) {
	updater.canvas = document.getElementById("canvas"+updater.simid);
	try {
	    updater.gl = updater.canvas.getContext("experimental-webgl");
	    updater.gl.viewportWidth = updater.canvas.width;
	    updater.gl.viewportHeight = updater.canvas.height;
	} catch (e) {
	}
	if (!updater.gl) {
	    alert("Could not initialise WebGL, sorry :-(");
	}
	initShaders(updater);
	updater.gl.clearColor(0.0, 0.0, 0.0, 1.0);
	updater.gl.clear(gl.COLOR_BUFFER_BIT);
	updater.gl.clear(gl.COLOR_BUFFER_BIT);

	updater.gl.useProgram(updater.shaderProgram);
	updater.pointsBuffer = updater.gl.createBuffer();

	updater.gl.enable(updater.gl.BLEND);
	updater.gl.blendFunc(updater.gl.SRC_ALPHA, updater.gl.ONE);

	mat4.identity(updater.moonRotationMatrix);
	updater.canvas.onmousedown = updater.handleMouseDown;
	updater.canvas.onmouseup = updater.handleMouseUp;
	updater.canvas.onmousemove = updater.handleMouseMove;
}
function drawScene(updater) {
	if (updater.N>0){
		mat4.identity(updater.mvMatrixRotated);
		mat4.multiply(updater.mvMatrixRotated,updater.mvMatrix);
		mat4.multiply(updater.mvMatrixRotated,updater.moonRotationMatrix);
		updater.gl.uniformMatrix4fv(updater.shaderProgram.mvMatrixUniform, false, updater.mvMatrixRotated);
		

		updater.gl.viewport(0, 0, updater.gl.viewportWidth, updater.gl.viewportHeight);
		updater.gl.clear(updater.gl.COLOR_BUFFER_BIT);

		updater.gl.useProgram(updater.shaderProgram);
		updater.gl.bindBuffer(updater.gl.ARRAY_BUFFER, updater.pointsBuffer);
		updater.gl.vertexAttribPointer(updater.shaderProgram.vertexPositionAttribute, 3, updater.gl.FLOAT, false, 0, 0);
		updater.gl.drawArrays(updater.gl.POINTS, 0, updater.N);
	}
}
	
	
function degToRad(f){
	return f*0.01745329251994;
}
	
function getShader(gl, id) {
	var shaderScript = document.getElementById(id);
	if (!shaderScript) {
	    return null;
	}
	var str = "";
	var k = shaderScript.firstChild;
	while (k) {
	    if (k.nodeType == 3) {
	        str += k.textContent;
	    }
	    k = k.nextSibling;
	}
	var shader;
	if (shaderScript.type == "x-shader/x-fragment") {
	    shader = gl.createShader(gl.FRAGMENT_SHADER);
	} else if (shaderScript.type == "x-shader/x-vertex") {
	    shader = gl.createShader(gl.VERTEX_SHADER);
	} else {
	    return null;
	}
	gl.shaderSource(shader, str);
	gl.compileShader(shader);
	if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
	    alert(gl.getShaderInfoLog(shader));
	    return null;
	}
	return shader;
}
function initShaders(updater) {
	updater.shaderProgram = updater.gl.createProgram();
	updater.gl.attachShader(updater.shaderProgram, getShader(updater.gl, "shader-vs-"+updater.simid));
	updater.gl.attachShader(updater.shaderProgram, getShader(updater.gl, "shader-fs-"+updater.simid));
	updater.gl.linkProgram(updater.shaderProgram);
	if (!updater.gl.getProgramParameter(updater.shaderProgram, updater.gl.LINK_STATUS)) {
		alert("Could not initialise shaders");
	}
	updater.gl.useProgram(updater.shaderProgram);
	updater.shaderProgram.vertexPositionAttribute = updater.gl.getAttribLocation(updater.shaderProgram, "aVertexPosition");
	updater.gl.enableVertexAttribArray(updater.shaderProgram.vertexPositionAttribute);
	updater.shaderProgram.pMatrixUniform = updater.gl.getUniformLocation(updater.shaderProgram, "uPMatrix");
	updater.shaderProgram.mvMatrixUniform = updater.gl.getUniformLocation(updater.shaderProgram, "uMVMatrix");	
}

function fillBuffer(updater,data) {
	updater.gl.bindBuffer(updater.gl.ARRAY_BUFFER, updater.pointsBuffer);
	updater.gl.bufferData(updater.gl.ARRAY_BUFFER, new Float32Array(data), updater.gl.DYNAMIC_DRAW);

	updater.gl.useProgram(updater.shaderProgram);
	mat4.perspective(45, updater.gl.viewportWidth / updater.gl.viewportHeight, 0.1, 100.0, updater.pMatrix);
	mat4.identity(updater.mvMatrix);
	mat4.translate(updater.mvMatrix, [0., 0., -7.0]);
	mat4.scale(updater.mvMatrix, [1./updater.scale,1./updater.scale,1./updater.scale]);
	updater.gl.uniformMatrix4fv(updater.shaderProgram.pMatrixUniform, false, updater.pMatrix);
	updater.gl.uniformMatrix4fv(updater.shaderProgram.mvMatrixUniform, false, updater.mvMatrix);
}

function StartUpdater(updater) {
	webGLStart(updater);
	var url = "ws://localhost:8877/reboundsocket";
	updater.socket = new WebSocket(url);
	updater.socket.onmessage = function(event) {
		updater.onmessage(JSON.parse(event.data));
	};
	updater.socket.onopen = function (event){
		updater.socket.send(updater.simid);
	};
}


var updater{simid} = {
	simid: {simid},	
	N: 0,
	scale: 1,
	socket: null,
	gl: null,
	shaderProgram: null,
	pointsBuffer: null,

	mouseDown: false,
	lastMouseX: null,
	lastMouseY: null,
	moonRotationMatrix: mat4.create(),
	mvMatrix: mat4.create(),
	mvMatrixRotated: mat4.create(),
	pMatrix: mat4.create(),
	
	onmessage: function(message) {
		updater{simid}.N = message.N;
		updater{simid}.scale = message.scale;
		fillBuffer(updater{simid}, message.data);
		drawScene(updater{simid});
	},
	
	handleMouseDown: function(event) {
		updater{simid}.mouseDown = true;
		updater{simid}.lastMouseX = event.clientX;
		updater{simid}.lastMouseY = event.clientY;
	},
	
	handleMouseUp: function(event) {
		updater{simid}.mouseDown = false;
	},
	
	handleMouseMove: function(event) {
		if (!updater{simid}.mouseDown) {
	      		return;
	    	}
		var newX = event.clientX;
		var newY = event.clientY;
		
		var deltaX = newX - lastMouseX;
		var newRotationMatrix = mat4.create();
		mat4.identity(newRotationMatrix);
		mat4.rotate(newRotationMatrix, degToRad(deltaX / 1.0), [0, 1, 0]);
		
		var deltaY = newY - lastMouseY;
		mat4.rotate(newRotationMatrix, degToRad(deltaY / 1.0), [1, 0, 0]);
		mat4.multiply(newRotationMatrix, updater{simid}.moonRotationMatrix, updater{simid}.moonRotationMatrix);
		
		updater{simid}.lastMouseX = newX
		updater{simid}.lastMouseY = newY;
		drawScene(updater{simid});
	},
};
	
	
StartUpdater(updater{simid});
</script>
