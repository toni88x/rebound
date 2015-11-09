<script id="shader-fs-{simid}" type="x-shader/x-fragment">
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

<script id="shader-vs-{simid}" type="x-shader/x-vertex">
    attribute vec3 aVertexPosition;
    uniform mat4 uMVMatrix;
    uniform mat4 uPMatrix;
    void main(void) {
        gl_Position = uPMatrix * uMVMatrix * vec4(aVertexPosition, 1.0);
	gl_PointSize = 9.;
    }
</script>

<script id="clearshader-fs-{simid}" type="x-shader/x-fragment">
    precision mediump float;
    void main(void) {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 0.5);
    }
</script>

<script id="clearshader-vs-{simid}" type="x-shader/x-vertex">
    attribute vec3 aVertexPosition;
    void main(void) {
        gl_Position = vec4(aVertexPosition, 1.0);
    }
</script>
