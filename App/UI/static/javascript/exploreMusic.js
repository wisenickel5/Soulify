import * as THREE from 'https://cdn.skypack.dev/three@0.135.0';
import { TextGeometry } from "./TextGeometry.js";
import { FontLoader } from "./FontLoader.js";

let parent, canvas, scene, camera, renderer;
var textObj;

init();

function init(){
	parent = document.getElementById('canvas-holder');
	canvas = document.getElementById('canvas');
	canvas.width = parent.offsetWidth;
	canvas.height = parent.offsetHeight;

	// Camera
	camera = new THREE.PerspectiveCamera( 
		75, // Field of View
		5, // Aspect Ratio
		0.1, // Near Clipping Plane
		1000 // Far Clipping Plane
	);
	camera.position.set( -500, 100, 0 );
	
	// Scene
	scene = new THREE.Scene();

	// Lights
	const dirLight = new THREE.DirectionalLight( 0xffffff, 0.125 );
	dirLight.position.set( -500, 100, 10 ).normalize();
	scene.add( dirLight );

	const pointLight = new THREE.PointLight( 0xffffff, 1.5 );
	pointLight.position.set( -500, 100, 20 );
	scene.add( pointLight );

	const fontUrl = "https://threejs.org/examples/fonts/helvetiker_regular.typeface.json";
	const loader = new FontLoader();
	loader.load( fontUrl , function ( font ) {
		const textMaterial = new THREE.MeshPhongMaterial( 
		{
			color: 0xFFFFFF,
			flatShading: true,
			side: THREE.DoubleSide,
			reflectivity: 1,
			shininess: 100,
			emissive: 0x000000,
			emissiveIntensity: 50
		});
		const textString = "Explore Music In A New Way";
		const shapes = font.generateShapes( textString, 100 );
		const geometry = new THREE.ShapeGeometry( shapes );
        geometry.computeBoundingBox();
		const xMid = - 0.5 * ( geometry.boundingBox.max.x - geometry.boundingBox.min.x );
        geometry.translate( xMid, 0, 0 );

		textObj = new THREE.Mesh( geometry, textMaterial );
		textObj.position.z = - 150;
		scene.add( textObj );

		camera.lookAt(new THREE.Vector3( textObj.position.x, 0, textObj.position.z ));

		animate();
	}); // End .load

	renderer = new THREE.WebGLRenderer( {alpha: true, antialias: true} );
	renderer.setClearColor( 0x000000, 0 );
	canvas.appendChild( renderer.domElement );
	renderer.setSize( canvas.clientWidth, canvas.clientHeight );
	window.addEventListener( 'resize', onWindowResize, false );	

}; // End init()

function onWindowResize() {
	camera.aspect = 5;
	camera.updateProjectionMatrix();
	renderer.setSize( canvas.clientWidth, canvas.clientHeight );
};

function animate() {
	requestAnimationFrame( animate );
	textObj.rotation.y -= 0.0055;
	render();
};

function render() {
	renderer.render( scene, camera );
};