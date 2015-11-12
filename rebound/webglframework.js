function startRebContext(rebContext, simid, scale) {
	///////////////////////////
	// Setup Context
	rebContext.simid = simid;	
	rebContext.N = 0;
	rebContext.scale = scale;

	rebContext.mouseDown = false;
	rebContext.lastMouseX = null;
	rebContext.lastMouseY = null;
	rebContext.mvMatrix = mat4.create();
	rebContext.mvMatrixRotated = mat4.create();
	rebContext.pMatrix = mat4.create();
	rebContext.moonRotationMatrix = mat4.create();
	mat4.identity(rebContext.moonRotationMatrix);
	
	///////////////////////////
	// Setup OpenGL
	rebContext.canvas = document.getElementById("canvas"+rebContext.simid);
	var gl;
	try {
	    gl = rebContext.canvas.getContext("experimental-webgl");
	    gl.viewportWidth = rebContext.canvas.width;
	    gl.viewportHeight = rebContext.canvas.height;
	    rebContext.gl = gl;
	} catch (e) {
	}
	if (!gl) {
	    alert("Could not initialise WebGL, sorry :-(");
	}

	gl.enable(gl.BLEND);
	gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
	gl.clearColor(0.0, 0.0, 0.0, 1.0);
	gl.clear(gl.COLOR_BUFFER_BIT);
	gl.clear(gl.COLOR_BUFFER_BIT);

	initShaders(rebContext);
	gl.useProgram(rebContext.shaderProgram);
	rebContext.pointsBuffer = gl.createBuffer();


	///////////////////////////
	// Setting callbacks
	rebContext.canvas.onmousedown = function(event) {
		rebContext.mouseDown = true;
		rebContext.lastMouseX = event.clientX;
		rebContext.lastMouseY = event.clientY;
	};
	rebContext.canvas.onmouseup = function(event) {
		rebContext.mouseDown = false;
	};
	rebContext.canvas.onmousemove = function(event) {
		if (!rebContext.mouseDown) {
	      		return;
	    	}
		var newX = event.clientX;
		var newY = event.clientY;
		
		var deltaX = newX - rebContext.lastMouseX;
		var newRotationMatrix = mat4.create();
		mat4.identity(newRotationMatrix);
		mat4.rotate(newRotationMatrix, degToRad(deltaX / 1.0), [0, 1, 0]);
		
		var deltaY = newY - rebContext.lastMouseY;
		mat4.rotate(newRotationMatrix, degToRad(deltaY / 1.0), [1, 0, 0]);
		mat4.multiply(newRotationMatrix, rebContext.moonRotationMatrix, rebContext.moonRotationMatrix);
		
		rebContext.lastMouseX = newX
		rebContext.lastMouseY = newY;
		drawScene(rebContext);
	};
	
	///////////////////////////
	// Open Socket
	var url = "ws://localhost:8877/reboundsocket";
	rebContext.socket = new WebSocket(url);
	rebContext.binaryType = "blob";
	rebContext.socket.onmessage = function(event) {
		//rebContext.N = message.N;
		console.log("debug");
		rebContext.N = 3;
		fillBuffer(rebContext, event.data);
		drawScene(rebContext);
	};
	rebContext.socket.onopen = function (event){
		rebContext.socket.send(rebContext.simid);
	};

}
function drawScene(rebContext) {
	var gl = rebContext.gl;
	if (rebContext.N>0){
		mat4.identity(rebContext.mvMatrixRotated);
		mat4.multiply(rebContext.mvMatrixRotated,rebContext.mvMatrix);
		mat4.multiply(rebContext.mvMatrixRotated,rebContext.moonRotationMatrix);
		gl.uniformMatrix4fv(rebContext.shaderProgram.mvMatrixUniform, false, rebContext.mvMatrixRotated);
		

		gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
		gl.clear(gl.COLOR_BUFFER_BIT);

		gl.useProgram(rebContext.shaderProgram);
		gl.bindBuffer(gl.ARRAY_BUFFER, rebContext.pointsBuffer);
		gl.vertexAttribPointer(rebContext.shaderProgram.vertexPositionAttribute, 3, gl.FLOAT, false, 128, 0);
		gl.drawArrays(gl.POINTS, 0, rebContext.N);
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
function initShaders(rebContext) {
	var gl = rebContext.gl;
	rebContext.shaderProgram = gl.createProgram();
	gl.attachShader(rebContext.shaderProgram, getShader(gl, "shader-vs-"+rebContext.simid));
	gl.attachShader(rebContext.shaderProgram, getShader(gl, "shader-fs-"+rebContext.simid));
	gl.linkProgram(rebContext.shaderProgram);
	if (!gl.getProgramParameter(rebContext.shaderProgram, gl.LINK_STATUS)) {
		alert("Could not initialise shaders");
	}
	gl.useProgram(rebContext.shaderProgram);
	rebContext.shaderProgram.vertexPositionAttribute = gl.getAttribLocation(rebContext.shaderProgram, "aVertexPosition");
	gl.enableVertexAttribArray(rebContext.shaderProgram.vertexPositionAttribute);
	rebContext.shaderProgram.pMatrixUniform = gl.getUniformLocation(rebContext.shaderProgram, "uPMatrix");
	rebContext.shaderProgram.mvMatrixUniform = gl.getUniformLocation(rebContext.shaderProgram, "uMVMatrix");	
}

function fillBuffer(rebContext,data) {
	var gl = rebContext.gl;
	gl.bindBuffer(gl.ARRAY_BUFFER, rebContext.pointsBuffer);
	console.log(data.slice(0));
	
	var reader = new FileReader();
	reader.onload = function(e) {
		gl.bufferData(gl.ARRAY_BUFFER, reader.result, gl.DYNAMIC_DRAW);
	}
	reader.readAsArrayBuffer(data);



	gl.useProgram(rebContext.shaderProgram);
	mat4.perspective(45, gl.viewportWidth / gl.viewportHeight, 0.1, 100.0, rebContext.pMatrix);
	mat4.identity(rebContext.mvMatrix);
	mat4.translate(rebContext.mvMatrix, [0., 0., -7.0]);
	mat4.scale(rebContext.mvMatrix, [1./rebContext.scale,1./rebContext.scale,1./rebContext.scale]);
	gl.uniformMatrix4fv(rebContext.shaderProgram.pMatrixUniform, false, rebContext.pMatrix);
	gl.uniformMatrix4fv(rebContext.shaderProgram.mvMatrixUniform, false, rebContext.mvMatrix);
}
