import * as THREE from 'https://cdn.skypack.dev/three@0.135.0';
import { TextGeometry } from "./TextGeometry.js";
import { FontLoader } from "./FontLoader.js";

let canvas, scene, camera, renderer;
var textObj;

init();

function init(){
	canvas = document.getElementById('canvas'); // Be sure to change this 
	// Camera
	camera = new THREE.PerspectiveCamera( 
		75, // Field of View
		5, // Aspect Ratio
		0.1, // Near Clipping Plane
		100 // Far Clipping Plane
	);
	camera.position.set( -600, 100, -600 );
	
	// Scene
	scene = new THREE.Scene();
	scene.background = new THREE.Color( 0x000000 );
	scene.fog = new THREE.Fog( 0x000000, 250, 1400 );

	// Lights
	const dirLight = new THREE.DirectionalLight( 0xffffff, 0.125 );
	dirLight.position.set( 0, 0, 1 ).normalize();
	scene.add( dirLight );

	const pointLight = new THREE.PointLight( 0xffffff, 1.5 );
	pointLight.position.set( 0, 100, 90 );
	scene.add( pointLight );

	const fontUrl = "https://threejs.org/examples/fonts/helvetiker_regular.typeface.json";
	const loader = new FontLoader();
	loader.load( fontUrl , function ( font ) {
		const textMaterial = new THREE.MeshBasicMaterial( 
		{
			color: 0x2c3e50,
			transparent: true,
			opacity: 0.8,
			side: THREE.DoubleSide
		});
		const textString = "Explore Music in a new way";
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

	renderer = new THREE.WebGLRenderer( {antialias: true} );
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
	textObj.rotation.y -= 0.01;
	render();
};

function render() {
	renderer.render( scene, camera );
};