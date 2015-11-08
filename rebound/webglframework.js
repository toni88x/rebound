<script id="shader-fs" type="x-shader/x-fragment">
    precision mediump float;
    void main(void) {
	vec2 pc = gl_PointCoord;
	pc.x -= 0.5;
	pc.y -= 0.5;
	pc.x *= 2.;
	pc.y *= 2.;
	float dis = length(pc);
        gl_FragColor = vec4(1.0, 1.0, 1.0, 1.-dis*dis);
    }
</script>

<script id="shader-vs" type="x-shader/x-vertex">
    attribute vec3 aVertexPosition;
    uniform mat4 uMVMatrix;
    uniform mat4 uPMatrix;
    void main(void) {
        gl_Position = uPMatrix * uMVMatrix * vec4(aVertexPosition, 1.0);
	gl_PointSize = 9.;
    }
</script>

<script id="clearshader-fs" type="x-shader/x-fragment">
    precision mediump float;
    void main(void) {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 0.5);
    }
</script>

<script id="clearshader-vs" type="x-shader/x-vertex">
    attribute vec3 aVertexPosition;
    void main(void) {
        gl_Position = vec4(aVertexPosition, 1.0);
    }
</script>


<script type="text/javascript">
    var gl;
    var N = 0;
    var scale = 1.;
    function initGL(canvas) {
        try {
            gl = canvas.getContext("experimental-webgl");
            gl.viewportWidth = canvas.width;
            gl.viewportHeight = canvas.height;
        } catch (e) {
        }
        if (!gl) {
            alert("Could not initialise WebGL, sorry :-(");
        }
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
    var shaderProgram;
    var clearShaderProgram;
    function initShaders() {
	shaderProgram = gl.createProgram();
        gl.attachShader(shaderProgram, getShader(gl, "shader-vs"));
        gl.attachShader(shaderProgram, getShader(gl, "shader-fs"));
        gl.linkProgram(shaderProgram);
        if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
            alert("Could not initialise shaders");
        }
        gl.useProgram(shaderProgram);
        shaderProgram.vertexPositionAttribute = gl.getAttribLocation(shaderProgram, "aVertexPosition");
        gl.enableVertexAttribArray(shaderProgram.vertexPositionAttribute);
        shaderProgram.pMatrixUniform = gl.getUniformLocation(shaderProgram, "uPMatrix");
        shaderProgram.mvMatrixUniform = gl.getUniformLocation(shaderProgram, "uMVMatrix");
        
	
	clearShaderProgram = gl.createProgram();
        gl.attachShader(clearShaderProgram, getShader(gl, "clearshader-vs"));
        gl.attachShader(clearShaderProgram, getShader(gl, "clearshader-fs"));
        gl.linkProgram(clearShaderProgram);
        if (!gl.getProgramParameter(clearShaderProgram, gl.LINK_STATUS)) {
            alert("Could not initialise shaders");
        }
        gl.useProgram(clearShaderProgram);
        clearShaderProgram.vertexPositionAttribute = gl.getAttribLocation(clearShaderProgram, "aVertexPosition");
        gl.enableVertexAttribArray(clearShaderProgram.vertexPositionAttribute);
    }

    var pointsBuffer; 
    var mvMatrix = mat4.create();
    var mvMatrixRotated = mat4.create();
    var pMatrix = mat4.create();
    
    function fillBuffer(data) {
        gl.bindBuffer(gl.ARRAY_BUFFER, pointsBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.DYNAMIC_DRAW);
    	
	
	
        gl.useProgram(shaderProgram);
        mat4.perspective(45, gl.viewportWidth / gl.viewportHeight, 0.1, 100.0, pMatrix);
        mat4.identity(mvMatrix);
        mat4.translate(mvMatrix, [0., 0., -7.0]);
        mat4.scale(mvMatrix, [1./scale,1./scale,1./scale]);
        gl.uniformMatrix4fv(shaderProgram.pMatrixUniform, false, pMatrix);
        gl.uniformMatrix4fv(shaderProgram.mvMatrixUniform, false, mvMatrix);
    }
    function drawScene() {
	if (N>0){
        	mat4.identity(mvMatrixRotated);
		mat4.multiply(mvMatrixRotated,mvMatrix);
		mat4.multiply(mvMatrixRotated,moonRotationMatrix);
        	gl.uniformMatrix4fv(shaderProgram.mvMatrixUniform, false, mvMatrixRotated);
		

		gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
		gl.clear(gl.COLOR_BUFFER_BIT);

        	gl.useProgram(shaderProgram);
        	gl.bindBuffer(gl.ARRAY_BUFFER, pointsBuffer);
		gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, 3, gl.FLOAT, false, 0, 0);
		gl.drawArrays(gl.POINTS, 0, N);
	}
    }
    function webGLStart(id) {
        var canvas = document.getElementById("canvas"+id);
        initGL(canvas);
        initShaders();
	gl.clearColor(0.0, 0.0, 0.0, 1.0);
		gl.clear(gl.COLOR_BUFFER_BIT);
	gl.clear(gl.COLOR_BUFFER_BIT);
        
        gl.useProgram(shaderProgram);
	pointsBuffer = gl.createBuffer();
        
	gl.enable(gl.BLEND);
	gl.blendFunc(gl.SRC_ALPHA, gl.ONE);



	canvas.onmousedown = handleMouseDown;
	canvas.onmouseup = handleMouseUp;
	canvas.onmousemove = handleMouseMove;
    }

var mouseDown = false;
  var lastMouseX = null;
  var lastMouseY = null;

  var moonRotationMatrix = mat4.create();
  mat4.identity(moonRotationMatrix);

  function handleMouseDown(event) {
    mouseDown = true;
    lastMouseX = event.clientX;
    lastMouseY = event.clientY;
  }

  function handleMouseUp(event) {
    mouseDown = false;
  }
  function degToRad(f){
	return f*0.01745329251994;
  }

  function handleMouseMove(event) {
    if (!mouseDown) {
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

    mat4.multiply(newRotationMatrix, moonRotationMatrix, moonRotationMatrix);

    lastMouseX = newX
    lastMouseY = newY;
    drawScene();
  }
</script>
