<?php
// src/models/RoleMenu.php
class RoleMenu {
    private $conn;
    private $table_name = "role_menu";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getMenusByRoleId($roleId) {
        $query = "SELECT m.id, m.name, m.url, m.icon 
                  FROM menus m
                  INNER JOIN " . $this->table_name . " rm ON m.id = rm.menu_id
                  WHERE rm.role_id = :roleId";
        
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':roleId', $roleId, PDO::PARAM_INT);
        $stmt->execute();

        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function updateRoleMenus($roleId, $menuIds) {
        $this->conn->beginTransaction();

        try {
            // Eliminar todas las asociaciones existentes para este rol
            $query = "DELETE FROM " . $this->table_name . " WHERE role_id = :roleId";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':roleId', $roleId);
            $stmt->execute();

            // Insertar las nuevas asociaciones
            $query = "INSERT INTO " . $this->table_name . " (role_id, menu_id) VALUES (:roleId, :menuId)";
            $stmt = $this->conn->prepare($query);

            foreach ($menuIds as $menuId) {
                $stmt->bindParam(':roleId', $roleId);
                $stmt->bindParam(':menuId', $menuId);
                $stmt->execute();
            }

            $this->conn->commit();
            return true;
        } catch (Exception $e) {
            $this->conn->rollBack();
            throw $e;
        }
    }
}