#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

import utils
from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
    min_and_max_tuples, Point3D, join_multiline,
)
from year_2022.day_22 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """


FaceVertices = Tuple[Point3D, Point3D, Point3D, Point3D]
Vertices = Dict[Point2D, FaceVertices]
FaceEdge = Tuple[Point3D, Point3D]
Edges = Dict[Point2D, Tuple[FaceEdge, FaceEdge, FaceEdge, FaceEdge]]


@dataclass
class CubeSolver:
    board: part_a.Board
    size: int = 50

    edges_indexes: Tuple[
        Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int],
    ] = ((0, 1), (1, 3), (3, 2), (2, 0))

    def visualise_edges(self, vertices: Vertices, edges: Edges) -> str:
        """
        >>> solver = CubeSolver(
        ...     part_a.Board.from_board_text(part_a.BOARD_INPUT), 4,
        ...     )
        >>> _vertices = solver.find_vertices(Point2D(0, 1))
        >>> _edges = solver.assign_edges(_vertices)
        >>> print(solver.visualise_edges(_vertices, _edges))
               D
              RBL
               U
         B  B  B
        LDRDRURUL
         F  F  F
               U  U
              RFLFLB
               D  D
        """
        edges_by_face: Dict[Point2D, List[FaceEdge]] = {
            face: [
                tuple(sorted(
                    face_vertices[edge_index]
                    for edge_index in edge_indexes
                ))
                for edge_indexes in self.edges_indexes
            ]
            for face, face_vertices in vertices.items()
        }
        faces_by_edge = helper.group_by((
            (edge, face)
            for face, edges in edges_by_face.items()
            for edge in edges
        ), key=lambda pair: pair[0], value="auto", values_container=set)
        face_counts_by_edge = set(map(len, faces_by_edge.values()))
        if face_counts_by_edge != {2}:
            raise Exception(
                f"Some edges didn't have exactly 2 faces, "
                f"but had: {face_counts_by_edge - {2}}"
            )
        other_face_by_face_and_edge = {
            (face, edge): other_face
            for edge, faces in faces_by_edge.items()
            for first_face, second_face in [faces]
            for face, other_face
            in [(first_face, second_face), (second_face, first_face)]
        }
        other_face_name_by_face_and_edge = {
            key: self.face_name_by_vertices[
                cast(FaceVertices, tuple(sorted(vertices[other_face])))
            ]
            for key, other_face in other_face_by_face_and_edge.items()
        }
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(vertices)
        return "\n".join(
            join_multiline("", (
                " {up} \n{left}{name}{right}\n {down} ".format(
                    name=self.face_name_by_vertices[
                        cast(FaceVertices, tuple(sorted(face_vertices)))
                    ],
                    up=other_face_name_by_face_and_edge[(
                        face_point, tuple(sorted(up_edge))
                    )],
                    right=other_face_name_by_face_and_edge[(
                        face_point, tuple(sorted(right_edge)),
                    )],
                    down=other_face_name_by_face_and_edge[(
                        face_point, tuple(sorted(down_edge)),
                    )],
                    left=other_face_name_by_face_and_edge[(
                        face_point, tuple(sorted(left_edge)),
                    )],
                )
                if face_point in vertices else
                "   \n   \n   "
                for x in range(min_x, max_x + 1)
                for face_point in [Point2D(x, y)]
                for face_vertices
                in [
                    vertices[face_point]
                    if face_point in vertices else
                    None
                ]
                for up_edge, right_edge, down_edge, left_edge
                in [
                    edges[face_point]
                    if face_point in vertices else
                    (None, None, None, None)
                ]
            ))
            for y in range(min_y, max_y + 1)
        )

    def assign_opposite_edges(
        self, vertices: Vertices, edges: Edges,
    ):
        """
        >>> solver = CubeSolver(
        ...     part_a.Board.from_board_text(part_a.BOARD_INPUT), 4,
        ...     )
        >>> _vertices = solver.find_vertices(Point2D(0, 1))
        >>> _edges = solver.assign_edges(_vertices)
        >>> solver.assign_opposite_edges(_vertices, _edges)
        """
        edge_inwards_directions = [
            part_a.Direction.Down, part_a.Direction.Left,
            part_a.Direction.Up, part_a.Direction.Right,
        ]
        edge_offsets: Tuple[
            Tuple[Point2D, Point2D], Tuple[Point2D, Point2D],
            Tuple[Point2D, Point2D], Tuple[Point2D, Point2D],
        ] = (
            (Point2D(0, 0), Point2D(1, 0)),
            (Point2D(1, 0), Point2D(1, 1)),
            (Point2D(1, 1), Point2D(0, 1)),
            (Point2D(0, 1), Point2D(0, 0)),
        )
        size_minus_1 = self.size - 1
        per_point_edge_offsets: Dict[Point2D, Tuple[
            Tuple[Point2D, Point2D, part_a.Direction],
            Tuple[Point2D, Point2D, part_a.Direction],
            Tuple[Point2D, Point2D, part_a.Direction],
            Tuple[Point2D, Point2D, part_a.Direction],
        ]] = {
            point: tuple(
                (
                    first.resize(size_minus_1).offset(offset),
                    second.resize(size_minus_1).offset(offset),
                    edge_inwards_direction
                )
                for (first, second), edge_inwards_direction
                in zip(edge_offsets, edge_inwards_directions)
            )
            for point in edges
            for offset in [point.resize(self.size)]
        }
        return per_point_edge_offsets

    def assign_edges(self, vertices: Vertices) -> Edges:
        return {
            face_point: (
                [face_vertices[0], face_vertices[1]],
                [face_vertices[1], face_vertices[3]],
                [face_vertices[3], face_vertices[2]],
                [face_vertices[2], face_vertices[0]],
            )
            for face_point in vertices
            for face_vertices in [vertices[face_point]]
        }

    vertices_by_face_name: ClassVar[Dict[str, FaceVertices]] = {
        "D": (
            Point3D(x, y, z)
            for x in [0, 1]
            for y in [0, 1]
            for z in [0]
        ),
        "U": (
            Point3D(x, y, z)
            for x in [0, 1]
            for y in [0, 1]
            for z in [1]
        ),
        "L": (
            Point3D(x, y, z)
            for x in [0]
            for y in [0, 1]
            for z in [0, 1]
        ),
        "R": (
            Point3D(x, y, z)
            for x in [1]
            for y in [0, 1]
            for z in [0, 1]
        ),
        "B": (
            Point3D(x, y, z)
            for x in [0, 1]
            for y in [0]
            for z in [0, 1]
        ),
        "F": (
            Point3D(x, y, z)
            for x in [0, 1]
            for y in [1]
            for z in [0, 1]
        ),
    }
    face_name_by_vertices: ClassVar[Dict[FaceVertices, str]] = {
        tuple(sorted(face_vertices)): face_name
        for face_name, face_vertices in vertices_by_face_name.items()
    }

    def visualise_faces(self, vertices: Vertices) -> str:
        """
        >>> solver = CubeSolver(
        ...     part_a.Board.from_board_text(part_a.BOARD_INPUT), 4,
        ...     )
        >>> print(solver.visualise_faces(solver.find_vertices(Point2D(0, 1))))
          B
        DRU
          FL
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(vertices)
        return "\n".join(
            "".join(
                self.face_name_by_vertices.get(face_vertices, "?")
                if face_point in vertices else
                " "
                for x in range(min_x, max_x + 1)
                for face_point in [Point2D(x, y)]
                for face_vertices
                in [cast(FaceVertices, tuple(sorted(
                    vertices.get(face_point, ()),
                )))]
            )
            for y in range(min_y, max_y + 1)
        )

    def find_vertices(
        self, first_face: Optional[Point2D] = None,
    ) -> Vertices:
        return self.assign_vertices(self.find_faces(), first_face=first_face)

    def assign_vertices(
        self, faces: Set[Point2D], first_face: Optional[Point2D] = None,
    ) -> Vertices:
        """
        >>> solver = CubeSolver(
        ...     part_a.Board.from_board_text(part_a.BOARD_INPUT), 4,
        ...     )
        >>> _vertices = solver.find_vertices(Point2D(0, 1))
        >>> _vertices[Point2D(0, 1)]  # D
        (Point3D(x=0, y=0, z=0), Point3D(x=1, y=0, z=0),
            Point3D(x=0, y=1, z=0), Point3D(x=1, y=1, z=0))
        >>> _vertices[Point2D(1, 1)]  # R
        (Point3D(x=1, y=0, z=0), Point3D(x=1, y=0, z=1),
            Point3D(x=1, y=1, z=0), Point3D(x=1, y=1, z=1))
        >>> _vertices[Point2D(2, 1)]  # U
        (Point3D(x=1, y=0, z=1), Point3D(x=0, y=0, z=1),
            Point3D(x=1, y=1, z=1), Point3D(x=0, y=1, z=1))
        >>> _vertices[Point2D(2, 0)]  # B
        (Point3D(x=1, y=0, z=0), Point3D(x=0, y=0, z=0),
            Point3D(x=1, y=0, z=1), Point3D(x=0, y=0, z=1))
        >>> _vertices[Point2D(2, 2)]  # F
        (Point3D(x=1, y=1, z=1), Point3D(x=0, y=1, z=1),
            Point3D(x=1, y=1, z=0), Point3D(x=0, y=1, z=0))
        >>> _vertices[Point2D(3, 2)]  # L
        (Point3D(x=0, y=1, z=1), Point3D(x=0, y=0, z=1),
            Point3D(x=0, y=1, z=0), Point3D(x=0, y=0, z=0))
        """
        vertices = {}
        remaining_faces = set(faces)
        if first_face is None:
            first_face = remaining_faces.pop()
        else:
            remaining_faces.remove(first_face)
        vertices[first_face] = (
            Point3D(0, 0, 0), Point3D(1, 0, 0),
            Point3D(0, 1, 0), Point3D(1, 1, 0),
        )
        queue = [first_face]

        while queue and remaining_faces:
            face = queue.pop()
            face_vertices = vertices[face]
            plane_index = next(
                index
                for index in range(3)
                if len({vertex[index] for vertex in face_vertices}) == 1
            )
            plane_value = face_vertices[0][plane_index]
            opposite_plane_value = 1 - plane_value
            opposite_face_vertices = tuple(
                face_vertex.replace_dimension(
                    plane_index, opposite_plane_value,
                )
                for face_vertex in face_vertices
            )
            face_up = face.offset(Point2D(0, -1))
            if face_up in remaining_faces:
                remaining_faces.remove(face_up)
                queue.append(face_up)
                vertices[face_up] = (
                    opposite_face_vertices[0], opposite_face_vertices[1],
                    face_vertices[0], face_vertices[1],
                )
            face_down = face.offset(Point2D(0, 1))
            if face_down in remaining_faces:
                remaining_faces.remove(face_down)
                queue.append(face_down)
                vertices[face_down] = (
                    face_vertices[2], face_vertices[3],
                    opposite_face_vertices[2], opposite_face_vertices[3],
                )
            face_left = face.offset(Point2D(-1, 0))
            if face_left in remaining_faces:
                remaining_faces.remove(face_left)
                queue.append(face_left)
                vertices[face_left] = (
                    opposite_face_vertices[0], face_vertices[0],
                    opposite_face_vertices[1], face_vertices[2],
                )
            face_right = face.offset(Point2D(1, 0))
            if face_right in remaining_faces:
                remaining_faces.remove(face_right)
                queue.append(face_right)
                vertices[face_right] = (
                    face_vertices[1], opposite_face_vertices[1],
                    face_vertices[3], opposite_face_vertices[3],
                )

        return vertices

    def find_faces(self) -> Set[Point2D]:
        """
        >>> sorted(CubeSolver(
        ...     part_a.Board.from_board_text(part_a.BOARD_INPUT), 4,
        ...     ).find_faces())
        [Point2D(x=0, y=1), Point2D(x=1, y=1), Point2D(x=2, y=0),
            Point2D(x=2, y=1), Point2D(x=2, y=2), Point2D(x=3, y=2)]
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.board.points)
        board_width = max_x - min_x + 1
        board_height = max_y - min_y + 1
        if board_width % self.size != 0 or board_height % self.size != 0:
            raise Exception(
                f"Board size ({board_width}x{board_height}) "
                f"is not congruent to cube size {self.size}"
            )
        face_count_x = board_width // self.size
        face_count_y = board_height // self.size
        faces = set()
        for y in range(face_count_y):
            ys = range(y * self.size, (y + 1) * self.size)
            for x in range(face_count_x):
                xs = range(x * self.size, (x + 1) * self.size)
                exist_values = {
                    Point2D(x, y) in self.board.points
                    for x in xs
                    for y in ys
                }
                if len(exist_values) == 2:
                    raise Exception(f"Board face at {x}x{y} was not consistent")
                face_exists, = exist_values
                if face_exists:
                    faces.add(Point2D(x, y))

        return faces


Challenge.main()
challenge = Challenge()
