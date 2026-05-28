"""
DepartmentTreeService — Domain layer (pure Python, không import SQLAlchemy/FastAPI).

Xử lý cây phân cấp phòng ban 4 tầng (L1→L4) bằng cấu trúc dữ liệu
in-memory. Tất cả method đều nhận toàn bộ danh sách departments để
tránh phụ thuộc vào DB trong domain layer.
"""
from __future__ import annotations

from app.domain.entities.department import Department


class DepartmentTreeService:
    """
    Service xử lý cây phân cấp phòng ban.

    Không có state — tất cả method là pure function nhận list[Department].
    Có thể dùng như singleton: tree = DepartmentTreeService()

    Sơ đồ cây 4 tầng:
        L1: Công ty
        L2: Ban A, Ban B
        L3: Phòng X, Phòng Y, Phòng Z
        L4: Nhóm 1, Nhóm 2
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_descendants(
        self,
        dept_id: int,
        all_depts: list[Department],
    ) -> set[int]:
        """
        Lấy tập hợp id của tất cả phòng ban con (cháu, chắt, ...) của dept_id.

        Args:
            dept_id: id của phòng ban gốc cần tìm con
            all_depts: toàn bộ danh sách Department từ DB

        Returns:
            set[int] — không bao gồm dept_id chính nó

        Ví dụ:
            Ban A (id=2) có Phòng X (id=4), Phòng Y (id=5)
            Phòng X (id=4) có Nhóm 1 (id=7)
            → get_descendants(2, ...) = {4, 5, 7}
        """
        index = self._build_children_index(all_depts)
        return self._collect_descendants(dept_id, index)

    def is_ancestor_of(
        self,
        ancestor_id: int,
        target_id: int,
        all_depts: list[Department],
    ) -> bool:
        """
        Kiểm tra ancestor_id có phải là tổ tiên (ancestor) của target_id không.

        Dùng để kiểm tra scope của manager: manager chỉ được thao tác
        trên các phòng ban nằm trong cây do mình quản lý.

        Args:
            ancestor_id: id phòng ban của người thực hiện hành động (manager)
            target_id: id phòng ban của đối tượng bị tác động (nhân viên)
            all_depts: toàn bộ danh sách Department từ DB

        Returns:
            True  — ancestor_id là tổ tiên trực tiếp hoặc gián tiếp của target_id
            False — hai phòng ban không có quan hệ ancestor-descendant,
                    hoặc ancestor_id == target_id (cùng phòng ban, không phải ancestor)

        Ví dụ:
            is_ancestor_of(ban_a_id, phong_x_id, ...) → True
            is_ancestor_of(ban_a_id, ban_b_id, ...)   → False (sibling)
            is_ancestor_of(phong_x_id, ban_a_id, ...) → False (ngược chiều)
        """
        if ancestor_id == target_id:
            return False
        descendants = self.get_descendants(ancestor_id, all_depts)
        return target_id in descendants

    def get_path_to_root(
        self,
        dept_id: int,
        all_depts: list[Department],
    ) -> list[int]:
        """
        Lấy đường đi từ dept_id lên đến root (L1), bao gồm dept_id.

        Returns:
            list[int] — [dept_id, parent_id, grandparent_id, ..., root_id]
        """
        index = self._build_parent_index(all_depts)
        path: list[int] = []
        current: int | None = dept_id
        visited: set[int] = set()

        while current is not None:
            if current in visited:
                break  # phòng ngừa vòng lặp nếu data không hợp lệ
            visited.add(current)
            path.append(current)
            current = index.get(current)

        return path

    def get_dept_and_descendants(
        self,
        dept_id: int,
        all_depts: list[Department],
    ) -> set[int]:
        """
        Lấy dept_id + tất cả con cháu — tiện dụng khi filter query theo scope.

        Returns:
            set[int] — bao gồm cả dept_id chính nó
        """
        return {dept_id} | self.get_descendants(dept_id, all_depts)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_children_index(
        all_depts: list[Department],
    ) -> dict[int, list[int]]:
        """Xây dựng dict {parent_id: [child_id, ...]} từ danh sách departments."""
        index: dict[int, list[int]] = {}
        for dept in all_depts:
            if dept.parent_id is not None:
                index.setdefault(dept.parent_id, []).append(dept.id)
        return index

    @staticmethod
    def _build_parent_index(
        all_depts: list[Department],
    ) -> dict[int, int | None]:
        """Xây dựng dict {dept_id: parent_id} từ danh sách departments."""
        return {dept.id: dept.parent_id for dept in all_depts}

    @staticmethod
    def _collect_descendants(
        root_id: int,
        children_index: dict[int, list[int]],
    ) -> set[int]:
        """BFS/DFS để thu thập toàn bộ con cháu từ children_index."""
        result: set[int] = set()
        queue: list[int] = list(children_index.get(root_id, []))

        while queue:
            current = queue.pop()
            if current in result:
                continue  # phòng ngừa cycle
            result.add(current)
            queue.extend(children_index.get(current, []))

        return result
