
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 POSCAR 文件读取晶格向量，计算倒易格子，
利用提供的 BZ 类计算布里渊区，并在交互式 3D 图中标注倒易向量和高对称点。
"""

import numpy as np
from scipy.spatial import Voronoi, ConvexHull, Delaunay
from collections import defaultdict
import warnings
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

#==================== POSCAR 读取与倒易格子计算 ====================

# 修改这里
POSCAR_PATH = "./POSCAR"  # 学姐只需要修改这部分为实际路径即可

def read_poscar(poscar_path):
    """
    读取 POSCAR 文件，返回晶格向量 a1, a2, a3（3个 numpy 数组）。
    假定 POSCAR 格式：
      Line 1: 注释
      Line 2: 标度因子 (float)
      Line 3-5: 晶格向量（空格分隔的3个数字）
    """
    with open(poscar_path, 'r') as f:
        lines = f.readlines()
    if len(lines) < 5:
        raise ValueError("POSCAR 文件行数不足，无法解析晶格向量")
    scale = float(lines[1].strip())
    a1 = np.array([float(x) for x in lines[2].strip().split()]) * scale
    a2 = np.array([float(x) for x in lines[3].strip().split()]) * scale
    a3 = np.array([float(x) for x in lines[4].strip().split()]) * scale
    return a1, a2, a3

def compute_reciprocal(a1, a2, a3):
    """
    计算倒易格子向量 b1, b2, b3：
      b1 = 2π * (a2 x a3) / (a1 · (a2 x a3))，依此类推
    """
    volume = np.dot(a1, np.cross(a2, a3))
    b1 = 2 * np.pi * np.cross(a2, a3) / volume
    b2 = 2 * np.pi * np.cross(a3, a1) / volume
    b3 = 2 * np.pi * np.cross(a1, a2) / volume
    return b1, b2, b3

#==================== BZ 类及相关函数 =====================

class BZ:
    """Class to compute the Brillouin zone of a crystal."""

    def __init__(self, b1, b2, b3) -> None:
        self._b_vectors = (b1, b2, b3)
        self._initialize_BZ(b1, b2, b3)

    @property
    def b_vectors(self) -> tuple:
        return self._b_vectors

    @property
    def hull(self) -> ConvexHull:
        return self._hull

    @property
    def delaunay(self) -> Delaunay:
        return self._delaunay

    @property
    def triangles_vertices(self):
        return self._triangles_vertices

    @property
    def triangles(self):
        return self._triangles

    @property
    def faces(self):
        return self._faces

    def _get_missing_point(self, tr, p1, p2):
        missing = None
        for vertex in tr:
            if vertex not in (p1, p2):
                if missing is not None:
                    raise ValueError("Two missing points found...")
                missing = vertex
        if missing is None:
            raise ValueError("No missing points!")
        return missing

    def _are_coplanar(self, v1, v2, v3) -> bool:
        return float(abs(np.dot(np.cross(v1, v2), v3))) < 1.0e-6

    def _initialize_BZ(self, b1, b2, b3) -> None:
        ret_data = {}
        supercell_size = 3  # 超胞大小

        points3d = []
        central_idx = None
        for i in range(-supercell_size, supercell_size + 1):
            for j in range(-supercell_size, supercell_size + 1):
                for k in range(-supercell_size, supercell_size + 1):
                    if i == 0 and j == 0 and k == 0:
                        central_idx = len(points3d)
                    points3d.append(
                        i * np.array(b1) + j * np.array(b2) + k * np.array(b3)
                    )

        vor3d = Voronoi(np.array(points3d))
        central_voronoi_3d = np.array(
            [vor3d.vertices[idx] for idx in vor3d.regions[vor3d.point_region[central_idx]]]
        )

        hull = ConvexHull(central_voronoi_3d)
        ret_data["triangles_vertices"] = hull.points.tolist()
        ret_data["triangles"] = []
        for simplex in hull.simplices:
            points = np.array([hull.points[i] for i in simplex])
            center = points.sum(axis=0) / float(len(points))
            normal = np.cross(center - points[1], center - points[0])
            normal = normal / np.linalg.norm(normal)
            max_length = np.sqrt((points**2).sum(axis=1).max())
            normal /= max_length
            normal *= 1.0e-4
            point_up = center + normal
            point_down = center - normal
            delaunay = Delaunay(hull.points)
            is_up_inside = delaunay.find_simplex(point_up) >= 0
            is_down_inside = delaunay.find_simplex(point_down) >= 0
            if is_up_inside and not is_down_inside:
                correct_orientation = True
            elif not is_up_inside and is_down_inside:
                correct_orientation = False
            else:
                correct_orientation = True
            if correct_orientation:
                ret_data["triangles"].append(simplex.tolist())
            else:
                ret_data["triangles"].append(simplex[::-1].tolist())

        edges = defaultdict(list)
        for simplex_idx, simplex in enumerate(hull.simplices):
            edges[tuple(sorted([simplex[0], simplex[1]]))].append(simplex_idx)
            edges[tuple(sorted([simplex[1], simplex[2]]))].append(simplex_idx)
            edges[tuple(sorted([simplex[2], simplex[0]]))].append(simplex_idx)
        edges = dict(edges)

        merge_with = defaultdict(set)
        for (p1, p2), triangles in edges.items():
            merge_with[triangles[0]].add(triangles[0])
            merge_with[triangles[1]].add(triangles[1])
            if len(triangles) != 2:
                continue
            else:
                otherpoint0 = self._get_missing_point(hull.simplices[triangles[0]], p1, p2)
                otherpoint1 = self._get_missing_point(hull.simplices[triangles[1]], p1, p2)
                otherpoint0_p = hull.points[otherpoint0]
                otherpoint1_p = hull.points[otherpoint1]
                p1_p = hull.points[p1]
                p2_p = hull.points[p2]
                if self._are_coplanar(p2_p - p1_p, otherpoint0_p - p1_p, otherpoint1_p - p1_p):
                    merge_with[triangles[0]].add(triangles[1])
                    merge_with[triangles[1]].add(triangles[0])
        has_changed = True
        while has_changed:
            has_changed = False
            for tr in range(len(hull.simplices)):
                for other1 in merge_with[tr]:
                    for other2 in merge_with[tr]:
                        if other1 not in merge_with[other2]:
                            has_changed = True
                            merge_with[other2].add(other1)
                        if other2 not in merge_with[other1]:
                            has_changed = True
                            merge_with[other1].add(other2)
        merge_with = {k: sorted(v) for k, v in merge_with.items()}
        merge_group = {k: v[0] for k, v in merge_with.items()}
        groups = defaultdict(list)
        for k, v in merge_group.items():
            groups[v].append(k)
        faces = []
        for group in groups.values():
            if len(group) == 1:
                faces.append([hull.points[pt_idx] for pt_idx in hull.simplices[group[0]]])
            else:
                all_points_idx = sorted(set(np.concatenate([hull.simplices[g] for g in group])))
                all_points_coords = [hull.points[pt_idx] for pt_idx in all_points_idx]
                v1 = all_points_coords[1] - all_points_coords[0]
                temp_v2 = all_points_coords[2] - all_points_coords[0]
                b_vec = np.cross(v1, temp_v2)
                v2 = np.cross(v1, b_vec)
                v1 = v1 / np.linalg.norm(v1)
                v2 = v2 / np.linalg.norm(v2)
                x = [np.dot(point, v1) for point in all_points_coords]
                y = [np.dot(point, v2) for point in all_points_coords]
                hull_face2d = ConvexHull(np.array([x, y]).T)
                actual_points_idx = [all_points_idx[subset_idx] for subset_idx in hull_face2d.vertices]
                faces.append([hull.points[pt_idx].tolist() for pt_idx in actual_points_idx])
        ret_data["faces"] = faces

        self._hull = hull
        self._delaunay = Delaunay(hull.points)
        self._triangles_vertices = ret_data["triangles_vertices"]
        self._triangles = ret_data["triangles"]
        self._faces = ret_data["faces"]

    def is_inside_bz(self, p):
        return self._delaunay.find_simplex(p) >= 0

#==================== 3D 可视化辅助类 =====================

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)

#==================== 高对称点辅助函数 =====================

def fractional_to_cartesian(frac, b1, b2, b3):
    """
    将分数坐标转换为笛卡尔坐标：
      cartesian = frac[0]*b1 + frac[1]*b2 + frac[2]*b3
    """
    return frac[0]*np.array(b1) + frac[1]*np.array(b2) + frac[2]*np.array(b3)

#==================== 主程序 =====================

def main():
    # 读取 POSCAR 文件，获得晶格向量
    a1, a2, a3 = read_poscar(POSCAR_PATH)
    print("原晶格向量 a1, a2, a3:")
    print(a1, a2, a3)

    # 计算倒易格子向量
    b1, b2, b3 = compute_reciprocal(a1, a2, a3)
    print("倒易格子向量 b1, b2, b3:")
    print(b1, b2, b3)

    # 计算布里渊区
    bz = BZ(b1, b2, b3)

    # 获取布里渊区面（用于可视化）
    faces_coords = bz.faces

    # 输出面统计
    faces_count = defaultdict(int)
    for face in faces_coords:
        faces_count[len(face)] += 1
    print("面统计:")
    for num_sides in sorted(faces_count.keys()):
        print(f"{num_sides} 边面: {faces_count[num_sides]} 个")

    #==================== 高对称点计算 =====================
    # 这里我们使用示例的分数坐标（请根据实际晶体系统修改）
    # 注意：下面给出的坐标仅供参考！
    high_sym_frac = {
        "Γ": np.array([0.0, 0.0, 0.0]),
        "X": np.array([0.0, 0.5, 0.0]),
        "M": np.array([0.5, 0.5, 0.0]),
        "R": np.array([0.0, 0.5, 0.5]),
        "Z": np.array([0.0, 0.0, 0.5]),
        "A": np.array([0.5, 0.5, 0.5])
    }
    # 转换为笛卡尔坐标（单位：1/Å）
    high_sym_cart = {label: fractional_to_cartesian(frac, b1, b2, b3)
                     for label, frac in high_sym_frac.items()}
    print("高对称点（笛卡尔坐标）：")
    for label, coord in high_sym_cart.items():
        print(f"{label}: {coord}")

    #==================== 可视化 =====================
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    poly3d = Poly3DCollection(faces_coords, linewidths=1, alpha=0.3, edgecolor="k", facecolor="#ccccff")
    ax.add_collection3d(poly3d)

    # 绘制原点
    ax.scatter([0], [0], [0], color="g", s=100)

    # 绘制倒易向量起点和箭头
    for vec, label in zip([b1, b2, b3], ["b1", "b2", "b3"]):
        vec = np.array(vec)
        ax.quiver(0, 0, 0, vec[0], vec[1], vec[2], color="k", arrow_length_ratio=0.1)
        # 在箭头末尾标注标签
        ax.text(vec[0], vec[1], vec[2], label, color="k", fontsize=12, fontweight="bold")

    # 绘制高对称点
    for label, coord in high_sym_cart.items():
        ax.scatter(coord[0], coord[1], coord[2], color="r", s=50)
        ax.text(coord[0], coord[1], coord[2], label, color="r", fontsize=12, fontweight="bold")

    # 添加坐标轴箭头（使用 Arrow3D 辅助类）
    axes_length = 1.5 * np.linalg.norm(b1)
    ax.add_artist(Arrow3D((0, axes_length), (0, 0), (0, 0), mutation_scale=20, lw=1, arrowstyle="-|>", color="k"))
    ax.add_artist(Arrow3D((0, 0), (0, axes_length), (0, 0), mutation_scale=20, lw=1, arrowstyle="-|>", color="k"))
    ax.add_artist(Arrow3D((0, 0), (0, 0), (0, axes_length), mutation_scale=20, lw=1, arrowstyle="-|>", color="k"))

    # 设置坐标轴范围（可根据具体情况调整）
    max_range = np.max(np.abs(np.concatenate([b1, b2, b3]))) * 2
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    ax.axis("off")
    ax.view_init(elev=20, azim=30)
    plt.title("Brillouin Zone with High-Symmetry Points")
    plt.show()

if __name__ == "__main__":
    main()
