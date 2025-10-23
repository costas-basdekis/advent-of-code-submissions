const DefaultDelta = 0.00001;

function main() {
    const [$svg] = document.getElementsByTagName("svg");
    window.svgWidth = parseInt($svg.attributes.width.value, 10);
    window.svgHeight = parseInt($svg.attributes.height.value, 10);
    normalisePoints();
    window.trianglesBySide = TrianglesBySide.fromTriangles(data);
    window.triangleSideMap = TriangleSideMap.fromTrianglesBySide(data, trianglesBySide);
    const firstSideRanges = getFirstSideRanges();
    const [allSideRanges] = getAllSideRangesAndRibbons(firstSideRanges);
    const allEndSideRanges = getEndSideRanges(allSideRanges);
    const [allReverseSideRanges, allReverseRibbons] = getAllSideRangesAndRibbons(allEndSideRanges);
    if (allReverseRibbons.length > 50) {
        console.log(`Too many ribbons (${allReverseRibbons.length}), limiting them`);
        allReverseRibbons.splice(0, allReverseRibbons.length - 50);
    }
    showRibbons(allReverseRibbons, true);
    const allReverseEndSideRanges = getEndSideRanges(allReverseSideRanges, 0);
    const allStartSideRanges = mergeSideRanges(allReverseEndSideRanges);
    console.log(`${firstSideRanges.length} start side ranges`);
    console.log(`${allSideRanges.length} side ranges`);
    console.log(` * ${allSideRanges.map(sideRange => data.indexOf(sideRange.triangle)).join(', ')}`);
    console.log(`${allEndSideRanges.length} end side ranges`);
    console.log(`${allReverseSideRanges.length} reverse side ranges`);
    console.log(`${allReverseEndSideRanges.length} reverse end side ranges`);
    console.log(`${allStartSideRanges.length} merged side ranges`);
    console.log(allStartSideRanges);
    if (!allStartSideRanges.length) {
        console.log("No valid Ys");
    } else {
        console.log(`Valid Y values are ${allStartSideRanges.map(({side: [{y: first}, {y: second}], start, end}) => almostEqual(start, end) ? `${first + (second - first) * start}` : `${first + (second - first) * start}-${first + (second - first) * end}`).join(", ")}`);
    }
    $svg.addEventListener("mousemove", e => {
        if (e.x >= 0 && e.x <= svgWidth && e.y >= 0 && e.y <= svgHeight) {
            const mouse = {x: e.x, y: e.y};
            setMousePolyline(mouse);
            // console.log(mouse, triangles.map(triangle => data.indexOf(triangle)), segment);
        }
    });
}

function normalisePoints() {
    const pointsByKey = {}
    for (const triangle of data) {
        for (const points of [triangle.points, triangle.min, triangle.max, [triangle.named.min, triangle.named.mid, triangle.named.max, triangle.named.new]]) {
            for (const point of points) {
                pointsByKey[getPointKey(point)] = point;
            }
        }
    }
    for (const triangle of data) {
        for (const points of [triangle.points, triangle.min, triangle.max]) {
            for (let index = 0 ; index < points.length ; index++) {
                const point = points[index];
                points[index] = pointsByKey[getPointKey(point)];
            }
        }
        triangle.named.min = pointsByKey[getPointKey(triangle.named.min)];
        triangle.named.mid = pointsByKey[getPointKey(triangle.named.mid)];
        triangle.named.max = pointsByKey[getPointKey(triangle.named.max)];
        triangle.named.new = pointsByKey[getPointKey(triangle.named.new)];
    }
}

function findTriangles(point) {
    return data.filter(({points}) => isPointInTriangle(point, points));
}

function isPointInTriangle(point, triangle) {
    if (triangle.some(other => arePointsEqual(other, point))) {
        return true;
    }
    const [a, b, c] = triangle;

    const as_x = point.x - a.x;
    const as_y = point.y - a.y;
    const s_ab = (b.x - a.x) * as_y - (b.y - a.y) * as_x >= 0;
    if ((c.x - a.x) * as_y - (c.y - a.y) * as_x >= 0 === s_ab) {
        return false;
    }

    const bs_x = point.x - b.x;
    const bs_y = point.y - b.y;
    if ((c.x - b.x) * bs_y - (c.y - b.y) * bs_x >= 0 !== s_ab) {
        return false;
    }
    return true;
}

function getLineAndSegmentIntersection(a1, a2, b1, b2) {
    const a_dx = a2.x - a1.x;
    const a_dy = a2.y - a1.y;
    const b_dx = b2.x - b1.x;
    const b_dy = b2.y - b1.y;
    const ab_x = a1.x - b1.x;
    const ab_y = a1.y - b1.y;
    const d = -b_dx * a_dy + a_dx * b_dy;
    const s = (b_dx * ab_y - b_dy * ab_x) / d;
    const t = (a_dx * ab_y - a_dy * ab_x) / d;
    if (!(t >= 0 && t <= 1)) {
        return null;
    }
    return {x: a1.x + s * a_dx, y: a1.y + s * a_dy};
}

function addPoints(first, second, secondFactor = 1) {
    return {x: first.x + second.x * secondFactor, y: first.y + second.y * secondFactor};
}

function subtractPoints(first, second) {
    return addPoints(first, second, -1);
}

function arePointsEqual(first, second) {
    return first.x === second.x && first.y === second.y;
}

function arePointsAlmostEqual(first, second, delta = DefaultDelta) {
    return almostEqual(first.x, second.x, delta) && almostEqual(first.y, second.y, delta);
}

function almostEqual(first, second, delta = DefaultDelta) {
    return Math.abs(first - second) <= delta;
}

function getPointsDistance(first, second) {
    const dx = first.x - second.x;
    const dy = first.y - second.y;
    return Math.sqrt(dx * dx + dy * dy);
}

function getPathDistance(points) {
    let distance = 0;
    let previousPoint = null;
    for (const point of points) {
        if (previousPoint) {
            distance += getPointsDistance(previousPoint, point);
        }
        previousPoint = point;
    }
    return distance;
}

function getTriangleIntersectingSegment(mouse, triangle) {
    const direction = triangle.direction;
    const points = triangle.points;
    const mouseDirection = addPoints(mouse, direction);
    const intersections = [
        getLineAndSegmentIntersection(mouse, mouseDirection, points[0], points[1]),
        getLineAndSegmentIntersection(mouse, mouseDirection, points[1], points[2]),
        getLineAndSegmentIntersection(mouse, mouseDirection, points[2], points[0]),
    ].filter(point => point);
    if (intersections.length === 3) {
        if (arePointsEqual(intersections[0], intersections[1])) {
            intersections.splice(0, 1);
        } else if (arePointsEqual(intersections[0], intersections[2])) {
            intersections.splice(0, 1);
        } else if (arePointsEqual(intersections[1], intersections[2])) {
            intersections.splice(2);
        } else {
            console.error(`Got too many intersections for ${mouse.x},${mouse.y}`);
        }
    }
    if (intersections.length !== 2) {
        return null;
    }
    return intersections;
}

function getPointKey(point) {
    return `${point.x},${point.y}`;
}

function getSideKey(side) {
    if (side.length !== 2) {
        throw new Error(`Side has too many sides: ${JSON.stringify(side)}`);
    }
    return side.map(getPointKey).sort().join("|");
}

class TrianglesBySide {
    static fromTriangles(triangles) {
        const bySide = new this();
        bySide.addMany(triangles);
        return bySide;
    }

    bySide = {};

    add(triangle) {
        const points = triangle.points;
        for (const side of [[points[0], points[1]], [points[1], points[2]], [points[2], points[0]]]) {
            const key = getSideKey(side);
            if (!(key in this.bySide)) {
                this.bySide[key] = [];
            }
            this.bySide[key].push(triangle);
        }
    }

    addMany(triangles) {
        for (const triangle of triangles) {
            this.add(triangle);
        }
    }

    get(side) {
        return this.bySide[getSideKey(side)];
    }
}

class TriangleSideMap {
    static fromTrianglesBySide(data, trianglesBySide) {
        const triangleSideMap = new this();
        triangleSideMap.addManyTriangles(data, trianglesBySide);
        return triangleSideMap;
    }

    sideMap = new Map();

    add(triangle, side, otherTriangle) {
        if (!this.sideMap.has(triangle)) {
            this.sideMap.set(triangle, {});
        }
        this.sideMap.get(triangle)[getSideKey(side)] = otherTriangle;
    }

    addTriangle(triangle, trianglesBySide) {
        const points = triangle.points;
        for (const side of [[points[0], points[1]], [points[1], points[2]], [points[2], points[0]]]) {
            const otherTriangles = trianglesBySide.get(side).filter(other => other !== triangle);
            if (!otherTriangles.length) {
                continue;
            }
            if (otherTriangles.length !== 1) {
                throw new Error(`There were too many other triangles for ${data.indexOf(triangle)}.${getSideKey(side)}: ${otherTriangles.map(triangle => data.indexOf(triangle)).join(", ")}`);
            }
            const [otherTriangle] = otherTriangles;
            this.add(triangle, side, otherTriangle);
        }
    }

    addManyTriangles(triangles, trianglesBySide) {
        for (const triangle of triangles) {
            this.addTriangle(triangle, trianglesBySide);
        }
    }

    get(triangle, side) {
        return this.sideMap.get(triangle)[getSideKey(side)];
    }
}

function expandSegmentToAllTriangles(startTriangle, startSegment) {
    const points = Array.from(startSegment);
    const seen = new Set([startTriangle]);
    let [left, right] = startSegment;
    if (arePointsEqual(left, right)) {
        return points;
    }
    // console.log("Expanding sides...");
    expandSides(left, startTriangle, seen, points, true);
    expandSides(right, startTriangle, seen, points, false);
    return points;
}

function expandSides(point, triangle, seen, points, addAtStart) {
    while (true) {
        let side = getTriangleSide(point, triangle);
        if (!side) {
            break;
        }
        triangle = triangleSideMap.get(triangle, side);
        if (!triangle) {
            break;
        }
        if (seen.has(triangle)) {
            break;
        }
        const segment = getTriangleIntersectingSegment(point, triangle);
        if (!segment) {
            // console.log("No intersecting segment");
            break;
        }
        if (arePointsAlmostEqual(segment[0], point)) {
            point = segment[1];
        } else if (arePointsAlmostEqual(segment[1], point)) {
            point = segment[0];
        } else {
            // console.log(`Point ${JSON.stringify(point)} not on intersecting segment ${JSON.stringify(segment)}`);
            break;
        }
        if (addAtStart) {
            points.splice(0, 0, point);
        } else {
            points.push(point);
        }
        seen.add(triangle);
    }
}

function getTriangleSide(point, triangle) {
    const points = triangle.points;
    for (const [left, right] of [[points[0], points[1]], [points[1], points[2]], [points[2], points[0]]]) {
        const distance = getPointsDistance(left, right);
        const totalDistance = getPointsDistance(left, point) + getPointsDistance(point, right);
        if (almostEqual(totalDistance, distance)) {
            return [left, right];
        }
    }
    return null;
}

function setMousePolyline(mouse) {
    const triangles = findTriangles(mouse);
    let segment = triangles.length ? getTriangleIntersectingSegment(mouse, triangles[0]) : null;
    const [$svg] = document.getElementsByTagName("svg");
    const [$mousePolyline] = document.getElementsByClassName("mouse-polyline");
    const [$pathLength] = document.getElementsByClassName("path-length");
    const width = parseInt($svg.attributes.width.value, 10);
    if (!segment) {
        $mousePolyline.setAttribute("points", "");
        $pathLength.textContent = "";
        return;
    }
    const points = expandSegmentToAllTriangles(triangles[0], segment);
    $mousePolyline.setAttribute("points", points.map(point => `${point.x},${point.y}`).join(" "));
    const xs = points.map(({x}) => x);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    if (almostEqual(minX, 0) && almostEqual(maxX, width)) {
        $mousePolyline.classList.remove("invalid");
    } else {
        $mousePolyline.classList.add("invalid");
    }
    $pathLength.textContent = `${getPathDistance(points)}`;
}

function getInitialSideRange(triangle, side) {
    const named = triangle.named;
    const hasMin = side.includes(named.min);
    const hasMid = side.includes(named.mid);
    const hasMax = side.includes(named.max);
    if (hasMin && hasMid) {
        return {triangle, side: [named.min, named.mid], start: 0, end: 1};
    }
    if (hasMid && hasMax) {
        return {triangle, side: [named.mid, named.max], start: 0, end: 1};
    }
    if (hasMin && hasMax) {
        return {triangle, side: [named.min, named.max], start: 0, end: 1};
    }
    throw new Error(`Side ${JSON.stringify(side)} did not match points ${JSON.stringify(named)}`);
}

function getNextSideRanges(sideRange) {
    const {triangle, side, start, end} = sideRange;
    const named = triangle.named;
    const hasMin = side.includes(named.min);
    const hasMid = side.includes(named.mid);
    const hasMax = side.includes(named.max);
    const newFactor = named.new_factor;
    if (hasMin && hasMid) {
        return [
            {triangle, side: [named.min, named.max], start: start * newFactor, end: end * newFactor},
        ];
    }
    if (hasMid && hasMax) {
        return [
            {triangle, side: [named.min, named.max], start: newFactor + start * (1 - newFactor), end: newFactor + end * (1 - newFactor)},
        ];
    }
    if (hasMin && hasMax) {
        if (end <= newFactor) {
            return [
                {triangle, side: [named.min, named.mid], start: start / newFactor, end: end / newFactor},
            ];
        }
        if (newFactor <= start) {
            return [
                {triangle, side: [named.mid, named.max], start: (start - newFactor) / (1 - newFactor), end: (end - newFactor) / (1 - newFactor)},
            ];
        }
        return [
            {triangle, side: [named.min, named.mid], start: start / newFactor, end: 1},
            {triangle, side: [named.mid, named.max], start: 0, end: (end - newFactor) / (1 - newFactor)},
        ];
    }
    throw new Error(`Side ${JSON.stringify(side)} did not match points ${JSON.stringify(named)}`);
}

function splitSideRange(sideRange) {
    const {triangle, side, start, end} = sideRange;
    const named = triangle.named;
    const newFactor = named.new_factor;
    if (side.includes(named.mid) || newFactor <= start || end <= newFactor) {
        return [sideRange];
    }
    return [
        {triangle, side, start: start, end: newFactor},
        {triangle, side, start: newFactor, end: end},
    ];
}

function translateSideRangeToNextTriangle(sideRange) {
    const {triangle, side, start, end} = sideRange;
    const nextTriangle = triangleSideMap.get(triangle, side);
    if (!nextTriangle) {
        return null;
    }
    const currentNamed = triangle.named;
    const currentHasMin = side.includes(currentNamed.min);
    const currentHasMid = side.includes(currentNamed.mid);
    const currentHasMax = side.includes(currentNamed.max);
    let currentLow, currentHigh;
    if (currentHasMin) {
        currentLow = currentNamed.min;
        if (currentHasMid) {
            currentHigh = currentNamed.mid;
        } else {
            currentHigh = currentNamed.max;
        }
    } else {
        currentLow = currentNamed.mid;
        currentHigh = currentNamed.max;
    }
    const nextNamed = nextTriangle.named;
    const nextHasMin = side.includes(nextNamed.min);
    const nextHasMid = side.includes(nextNamed.mid);
    const nextHasMax = side.includes(nextNamed.max);
    let nextLow, nextHigh;
    if (nextHasMin) {
        nextLow = nextNamed.min;
        if (nextHasMid) {
            nextHigh = nextNamed.mid;
        } else {
            nextHigh = nextNamed.max;
        }
    } else {
        nextLow = nextNamed.mid;
        nextHigh = nextNamed.max;
    }
    if (currentLow === nextLow && currentHigh === nextHigh) {
        return {triangle: nextTriangle, side, start, end};
    } else {
        return {triangle: nextTriangle, side, start: 1 - end, end: 1 - start};
    }
}

function convertSideRangeToPoints(sideRange) {
    const {side, start, end} = sideRange;
    const [first, second] = side;
    if (start === 0 && end === 1) {
        return side;
    }
    const delta = subtractPoints(second, first);
    return [addPoints(first, delta, start), addPoints(first, delta, end)];
}

function getFirstSideRanges() {
    const triangles = data.filter(triangle => triangle.points.filter(({x}) => x === 0).length === 2);
    return triangles.map(triangle => getInitialSideRange(triangle, triangle.points.filter(({x}) => x === 0)));
}

function getNextSideRangesAndSeenAndRibbonsAndTerminals(sideRangesAndSeen) {
    const nextSideRangesAndSeenList = sideRangesAndSeen.map(
        ({sideRange, seen}) => getNextSideRanges(sideRange).map(
            nextSideRange => ({sideRange: nextSideRange, seen})));
    const ribbons = sideRangesAndSeen.flatMap(({sideRange}, index) => {
        const nextSideRangesAndSeen = nextSideRangesAndSeenList[index];
        const splitSideRanges = splitSideRange(sideRange);
        return nextSideRangesAndSeen.map(({sideRange: nextSideRange}, nextIndex) => ({
            isValid: !!triangleSideMap.get(nextSideRange.triangle, nextSideRange.side) || nextSideRange.side.every(({x}) => almostEqual(x, svgWidth)),
            points: [
                ...convertSideRangeToPoints(splitSideRanges[nextIndex]),
                ...Array.from(convertSideRangeToPoints(nextSideRange)).reverse(),
            ],
        }));
    });
    const translatedNextSideRangesAndSeen = nextSideRangesAndSeenList
        .flat()
        .map(({sideRange, seen}) => {
            const translatedSideRange = translateSideRangeToNextTriangle(sideRange);
            if (!translatedSideRange || seen.has(translatedSideRange.triangle)) {
                return null;
            }
            const newSeen = new Set(seen);
            newSeen.add(translatedSideRange.triangle);
            return {sideRange: translatedSideRange, seen: newSeen};
        })
        .filter(sideRangeAndSeen => sideRangeAndSeen);
    const terminalSideRanges = nextSideRangesAndSeenList
        .flat()
        .filter(({sideRange}) => !triangleSideMap.get(sideRange.triangle, sideRange.side))
        .map(({sideRange}) => sideRange);
    return [translatedNextSideRangesAndSeen, ribbons, terminalSideRanges];
}

function getAllSideRangesAndRibbons(firstSideRanges = getFirstSideRanges()) {
    const sideRanges = [...firstSideRanges];
    const ribbons = [];
    let previousSideRangesAndSeen = firstSideRanges
        .map(sideRange => ({sideRange, seen: new Set([sideRange.triangle])}));
    while (previousSideRangesAndSeen.length) {
        const [nextSideRangesAndSeen, nextRibbons, terminalSideRanges] = getNextSideRangesAndSeenAndRibbonsAndTerminals(previousSideRangesAndSeen);
        sideRanges.push(...nextSideRangesAndSeen.map(({sideRange}) => sideRange));
        sideRanges.push(...terminalSideRanges);
        ribbons.push(...nextRibbons);
        previousSideRangesAndSeen = nextSideRangesAndSeen;
    }
    return [sideRanges, ribbons];
}

function showRibbons(ribbons, final = false) {
    return ribbons.map(ribbon => {
        const [$ribbonsContainer] = document.getElementsByClassName("ribbons");
        const $ribbon = document.createElementNS(document.documentElement.namespaceURI, "polygon");
        $ribbon.setAttribute("points", ribbon.points.map(getPointKey).join(" "));
        $ribbon.classList.add("ribbon");
        if (final) {
            $ribbon.classList.add("final");
        } else if (!ribbon.isValid) {
            $ribbon.classList.add("invalid");
        }
        $ribbonsContainer.appendChild($ribbon);
        return $ribbon;
    });
}

function getEndSideRanges(allSideRanges, matchX = svgWidth) {
    return allSideRanges.filter(sideRange => (
        (almostEqual(sideRange.start, 0) && almostEqual(sideRange.side[0].x, matchX))
        || (almostEqual(sideRange.end, 1) && almostEqual(sideRange.side[1].x, matchX))
        || (sideRange.side.every(({x}) => almostEqual(x, matchX)))
    )).map(sideRange => {
        if (almostEqual(sideRange.start, 0) && almostEqual(sideRange.side[0].x, matchX)) {
            return {
                triangle: sideRange.triangle,
                side: sideRange.side,
                start: 0,
                end: 0,
            };
        }
        if (almostEqual(sideRange.end, 1) && almostEqual(sideRange.side[1].x, matchX)) {
            return {
                triangle: sideRange.triangle,
                side: sideRange.side,
                start: 1,
                end: 1,
            };
        }
        return sideRange;
    });
}

function mergeSideRanges(sideRanges) {
    const sideRangesByTriangleAndSide = new Map();
    for (const sideRange of sideRanges) {
        const sideKey = getSideKey(sideRange.side);
        if (!sideRangesByTriangleAndSide.has(sideRange.triangle)) {
            sideRangesByTriangleAndSide.set(sideRange.triangle, {});
        }
        if (!(sideKey in sideRangesByTriangleAndSide.get(sideRange.triangle))) {
            sideRangesByTriangleAndSide.get(sideRange.triangle)[sideKey] = new Set();
        }
        sideRangesByTriangleAndSide.get(sideRange.triangle)[sideKey].add(sideRange);
    }
    const mergedSideRanges = [];
    for (const bySideMap of sideRangesByTriangleAndSide.values()) {
        for (const group of Object.values(bySideMap)) {
            const sortedGroup = Array.from(group).sort((left, right) => left.start - right.start);
            let previous = null;
            for (const sideRange of sortedGroup) {
                if (previous === null) {
                    previous = sideRange;
                    continue;
                }
                if (sideRange.start > previous.end && !almostEqual(sideRange.start, previous.end)) {
                    mergedSideRanges.push(previous);
                    previous = sideRange;
                    continue;
                }
                previous = {
                    triangle: previous.triangle,
                    side: previous.side,
                    start: previous.start,
                    end: sideRange.end,
                };
            }
            if (previous) {
                mergedSideRanges.push(previous);
            }
        }
    }
    mergedSideRanges.sort((left, right) => Math.min(...left.side.map(({x}) => x)) - Math.min(...right.side.map(({x}) => x)));
    return mergedSideRanges;
}

main();
