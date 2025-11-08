import * as THREE from "three";
import {
  OrbitControls,
  LineSegmentsGeometry,
  LineMaterial,
  LineSegments2,
} from "three/addons";
const {GUI} = lil;

export function initialise3D() {
    const rerender = makeScene(data);

    rerender();
}

function makeScene(hills) {
    const {zFactor, minStartZ, maxStartZ, minEndZ, maxEndZ} = getPointsBoundaries(hills);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(
        70,
        window.innerWidth / window.innerHeight,
        0.1,
        10000
    );
    camera.position.z = 5000;
    camera.position.y = 500;

    var renderer = new THREE.WebGLRenderer({
        canvas: document.getElementById("3d-target"),
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const pinkMaterial = new THREE.MeshBasicMaterial({
        color: 0xffc0cb,
        side: THREE.DoubleSide,
    });
    const cyanMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        side: THREE.DoubleSide,
    });
    const maxMountainGeometry = new THREE.BufferGeometry();
    maxMountainGeometry.setAttribute(
        "position",
        new THREE.BufferAttribute(
            new Float32Array(
                hills.flatMap(({ named: { mid, max, new: _new } }) =>
                    [mid, max, _new].flatMap(({ x, y, z }) => [x, y, z * zFactor])
                )
            ),
            3
        )
    );
    const maxMountainMesh = new THREE.Mesh(maxMountainGeometry, pinkMaterial);
    scene.add(maxMountainMesh);
    const minMountainGeometry = new THREE.BufferGeometry();
    minMountainGeometry.setAttribute(
        "position",
        new THREE.BufferAttribute(
            new Float32Array(
                hills.flatMap(({ named: { mid, min, new: _new } }) =>
                    [mid, min, _new].flatMap(({ x, y, z }) => [
                        x,
                        y,
                        z * zFactor,
                    ])
                )
            ),
            3
        )
    );
    const minMountainMesh = new THREE.Mesh(minMountainGeometry, cyanMaterial);
    scene.add(minMountainMesh);

    const lineMaterial = new LineMaterial({
        linewidth: 10,
        color: 0xffffff,
        // alphaToCoverage: true,
        worldUnits: true,
    });
    const minWireframe = new LineSegmentsGeometry().fromWireframeGeometry(
        minMountainGeometry
    );
    const minWireframeLine = new LineSegments2(minWireframe, lineMaterial);
    scene.add(minWireframeLine);

    const maxWireframe = new LineSegmentsGeometry().fromWireframeGeometry(
        maxMountainGeometry
    );
    const maxWireframeLine = new LineSegments2(maxWireframe, lineMaterial);
    scene.add(maxWireframeLine);

    const startPlaneMaterial = new THREE.MeshBasicMaterial({
        color: 0xffff00,
        transparent: true,
        opacity: 0.5,
        side: THREE.DoubleSide,
    });
    const endPlaneMaterial = new THREE.MeshBasicMaterial({
        color: 0xff00ff,
        transparent: true,
        opacity: 0.5,
        side: THREE.DoubleSide,
    });
    const width = 2000,
        height = 1000,
        planeWidth = 3000,
        planeHeight = 1500,
        planeXOffset = width / 2,
        planeYOffset = height / 2;
    const minStartPlaneGeometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
    minStartPlaneGeometry.translate(planeXOffset, planeYOffset, minStartZ);
    const minStartPlane = new THREE.Mesh(minStartPlaneGeometry, startPlaneMaterial);
    scene.add(minStartPlane);
    const maxStartPlaneGeometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
    maxStartPlaneGeometry.translate(planeXOffset, planeYOffset, maxStartZ);
    const maxStartPlane = new THREE.Mesh(maxStartPlaneGeometry, startPlaneMaterial);
    scene.add(maxStartPlane);
    const minEndPlaneGeometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
    minEndPlaneGeometry.translate(planeXOffset, planeYOffset, minEndZ);
    const minEndPlane = new THREE.Mesh(minEndPlaneGeometry, endPlaneMaterial);
    scene.add(minEndPlane);
    const maxEndPlaneGeometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
    maxEndPlaneGeometry.translate(planeXOffset, planeYOffset, maxEndZ);
    const maxEndPlane = new THREE.Mesh(maxEndPlaneGeometry, endPlaneMaterial);
    scene.add(maxEndPlane);
    const planes = [
        minStartPlane,
        maxStartPlane,
        minEndPlane,
        maxEndPlane,
    ];
    const outOfBoundsPlanes = [
        minEndZ <= minStartZ && minStartZ <= maxEndZ ? null : minStartPlane,
        minEndZ <= maxStartZ && maxStartZ <= maxEndZ ? null : maxStartPlane,
        minStartZ <= minEndZ && minEndZ <= maxStartZ ? null : minEndPlane,
        minStartZ <= maxEndZ && maxEndZ <= maxStartZ ? null : maxEndPlane,
    ].filter((mesh) => mesh);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.update();

    makeGui(planes, outOfBoundsPlanes);

    setUpEvents(camera, [minMountainMesh, maxMountainMesh]);

    function render() {
        renderer.render(scene, camera);
        rerender();
    }
    function rerender() {
        requestAnimationFrame(render);
    }

    return rerender;
}

function makeGui(planes, outOfBoundsPlanes) {
    const settings = {
        showPlanes: true,
        showOutOfBoundsPlanes: false,
    };
    const gui = new GUI({ container: document.getElementById("3d-parent") });
    function togglePlanes() {
        planes.forEach((mesh) => {
            mesh.visible = settings.showPlanes && (!outOfBoundsPlanes.includes(mesh) || settings.showOutOfBoundsPlanes);
        });
    }
    togglePlanes();
    gui
        .add(settings, "showPlanes")
        .onChange(togglePlanes);
    gui
        .add(settings, "showOutOfBoundsPlanes")
        .onChange(togglePlanes);
}

function getPointsBoundaries(hills) {
    const allPoints = hills.flatMap(({ points }) => points);
    const zs = allPoints.map(({ z }) => z);
    const maxZ = Math.max(...zs);
    const zFactor = 1000 / maxZ;
    const xs = allPoints.map(({ x }) => x);
    const maxX = Math.max(...xs);
    const startZs = allPoints.filter(({ x }) => x === 0).map(({ z }) => z);
    const minStartZ = Math.min(...startZs) * zFactor;
    const maxStartZ = Math.max(...startZs) * zFactor;
    const endZs = allPoints.filter(({ x }) => x === maxX).map(({ z }) => z);
    const minEndZ = Math.min(...endZs) * zFactor;
    const maxEndZ = Math.max(...endZs) * zFactor;
    return {zFactor, minStartZ, maxStartZ, minEndZ, maxEndZ};
}

function setUpEvents(camera, objects) {
    const pointer = new THREE.Vector2();
    const raycaster = new THREE.Raycaster();
    const $canvas = document.getElementById("3d-target");
    const boundingRect = $canvas.getBoundingClientRect();
    $canvas.addEventListener("mousemove", e => {
        pointer.set(
            ((e.clientX - boundingRect.left) / boundingRect.width) * 2 - 1, 
            -((e.clientY - boundingRect.top) / boundingRect.height) * 2 + 1,
        );
        raycaster.setFromCamera(pointer, camera);
        const intersections = raycaster.intersectObjects(objects, false);
        // if (intersections.length) {
        //     console.log("Yes", intersections[0].point);
        // } else {
        //     console.log("No");
        // }
    });
}
